#!/usr/bin/env python3
"""Logged, resumable operator transitions; never calls Shopify or changes stock/prices."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit
import uuid
from zoneinfo import ZoneInfo

from read_register import DEFAULT_ROOT, STATUSES, read_register

SKU = re.compile(r"PBS-(?:SAR|SKZ|MIN|RED|DUP|HOM|JEW)-[0-9]{3,}")
PATCH_KEYS = {"stage", "productId", "variantId", "inventoryItemId", "handle", "imageFileIds",
              "imageHashes", "inventoryIdempotencyKey", "inventoryInitialized", "lastError"}
STAGES = {"awaiting_photo", "photo_received", "images_prepared", "draft_created",
          "inventory_initialized", "media_attached", "ready", "published", "blocked"}
ROW_FIELDS = {"sku", "costPrice", "sellingPrice", "productStatus", "stockStatus", "shopifyUrl",
              "submittedAt", "publishedAt", "lastStockUpdateAt", "operatorNotes"}


class RegisterError(Exception):
    pass


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def now():
    return datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(timespec="seconds")


def money(value):
    try:
        if isinstance(value, bool):
            raise ValueError()
        result = Decimal(str(value))
        if not result.is_finite() or result < 0:
            raise ValueError()
        return result
    except (InvalidOperation, ValueError):
        raise RegisterError("Invalid price or cost")


def canonical_url(value):
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or parsed.netloc not in {
            "periwinklebysherry.com", "periwinkle-by-sherry.myshopify.com"}
            or parsed.query or parsed.fragment
            or not re.fullmatch(r"/products/[a-z0-9]+(?:-[a-z0-9]+)*/?", parsed.path)):
        raise RegisterError("Use a canonical Periwinkle /products/<handle> HTTPS URL")
    return "https://periwinklebysherry.com" + parsed.path.rstrip("/")


class Register:
    def __init__(self, root, fault=None):
        self.root = Path(root).expanduser().resolve()
        self.fault = fault or (lambda phase: None)
        for directory in ["products", "log", "register/_replaced", *["register/" + s for s in STATUSES]]:
            if not self.path(directory).is_dir():
                raise RegisterError("Missing operations folder: " + directory)

    def path(self, relative):
        path = self.root / relative
        if not path.resolve().is_relative_to(self.root):
            raise RegisterError("Path escapes the operations folder")
        for parent in [path, *path.parents]:
            if parent == self.root:
                break
            if parent.is_symlink():
                raise RegisterError("Symlinks are not supported inside operational data")
        return path

    def json(self, relative):
        value = json.loads(self.path(relative).read_text())
        if not isinstance(value, dict):
            raise RegisterError("Expected a JSON object: " + relative)
        return value

    def key(self, sku):
        sku = sku.upper()
        if not SKU.fullmatch(sku) or int(sku.rsplit("-", 1)[1]) == 0:
            raise RegisterError("Invalid canonical SKU")
        return sku.lower()

    def atomic(self, relative, payload):
        destination = self.path(relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        staging = self.path("agent/tmp")
        staging.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=staging, delete=False) as file:
                temporary = Path(file.name)
                file.write(payload)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, destination)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()

    def immutable(self, relative, payload):
        path = self.path(relative)
        if path.exists():
            if path.read_bytes() != payload:
                raise RegisterError("Existing transaction artifact differs: " + relative)
        else:
            self.atomic(relative, payload)

    @contextmanager
    def lock(self):
        self.path("agent").mkdir(exist_ok=True)
        with self.path("agent/.lock").open("a") as file:
            try:
                fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise RegisterError("Another local operator helper is running")
            try:
                yield
            finally:
                fcntl.flock(file, fcntl.LOCK_UN)

    def pending(self, sku=None):
        transactions = [self.json(str(p.relative_to(self.root)))
                        for p in sorted(self.path("agent/transactions").glob("*.json"))]
        return [item for item in transactions if item.get("state") == "pending"
                and (sku is None or str(item.get("sku", "")).upper() == sku.upper())]

    def snapshot(self, sku):
        key = self.key(sku)
        for status in STATUSES:
            if any(re.match(re.escape(key) + r"(?:\D|$)", p.stem.lower()) and p.name != key + ".json"
                   for p in self.path("register/" + status).iterdir() if p.is_file()):
                raise RegisterError("Possible conflict copy for this SKU")
        candidates = [f"register/{status}/{key}.json" for status in STATUSES
                      if self.path(f"register/{status}/{key}.json").exists()]
        if len(candidates) != 1:
            raise RegisterError("Expected one current row; resolve missing/duplicate rows or recover its pending transaction")
        relative = candidates[0]
        raw = self.path(relative).read_bytes()
        row = self.json(relative)
        submission = self.json(f"products/{key}.json")
        if (not ROW_FIELDS.issubset(row) or not isinstance(row.get("sku"), str)
                or not isinstance(submission.get("sku"), str) or row["sku"].upper() != sku.upper()
                or row.get("productStatus") != relative.split("/")[1]
                or not row.get("submittedAt")
                or submission.get("submittedAt") != row["submittedAt"]
                or submission.get("sku", "").upper() != sku.upper()):
            raise RegisterError("SKU, submission identity or folder/status mismatch")
        job = None
        if self.path(f"agent/jobs/{key}.json").exists():
            candidate = self.json(f"agent/jobs/{key}.json")
            if candidate.get("submittedAt") == row["submittedAt"] and candidate.get("sku") == row["sku"]:
                job = candidate
        return {"row": row, "sha256": digest(raw), "path": relative, "job": job}

    def queue(self):
        register = read_register(str(self.root))
        products, problems = [], list(register["problems"])
        for row in register["products"]:
            try:
                snapshot = self.snapshot(row["sku"])
                if snapshot["job"] and snapshot["job"].get("stage") == "published" and row["status"] != "LIVE":
                    problems.append(f"{row['sku']}: previously published job was moved back; explicit rework is required")
                    continue
                if row["status"] == "NEW" or (snapshot["job"] and row["status"] in {"IN_PROGRESS", "READY_TO_PUBLISH"}):
                    products.append(snapshot)
            except (RegisterError, OSError, ValueError) as error:
                problems.append(f"{row.get('sku')}: {error}")
        products.sort(key=lambda item: (item["row"]["submittedAt"], item["row"]["sku"]))
        return {"products": products, "pendingTransactions": self.pending(),
                "pendingStockRequests": register["pendingStockRequests"], "problems": problems}

    def assert_fresh(self, snapshot, expected):
        if snapshot["sha256"] != expected or digest(self.path(snapshot["path"]).read_bytes()) != expected:
            raise RegisterError("Register changed; reread it before continuing")

    def stock_ready(self, row):
        if row.get("stockStatus") != "IN_STOCK":
            raise RegisterError("An OUT_OF_STOCK row cannot be automatically processed")
        for path in self.path("stock-requests/PENDING").glob("*.json"):
            if path.name.startswith("_"):
                continue
            request = self.json(str(path.relative_to(self.root)))
            if (str(request.get("sku", "")).upper() == row["sku"].upper()
                    and request.get("requestedStockStatus") == "OUT_OF_STOCK"):
                raise RegisterError("Resolve the pending out-of-stock request before processing this SKU")

    def publication_receipt(self, row, job, receipt):
        self.stock_ready(row)
        if not isinstance(receipt, dict):
            raise RegisterError("Missing Shopify verification receipt")
        try:
            checked = datetime.fromisoformat(receipt["checkedAt"])
            age = datetime.now(timezone.utc) - checked.astimezone(timezone.utc)
            if checked.tzinfo is None or not timedelta(seconds=-60) <= age <= timedelta(minutes=10):
                raise ValueError()
            if (receipt["sku"] != row["sku"] or receipt["productId"] != job.get("productId")
                    or canonical_url(receipt["url"]) != row["shopifyUrl"]
                    or receipt["status"] != "ACTIVE" or receipt["onlineStorePublished"] is not True
                    or money(receipt["price"]) != money(row["sellingPrice"])
                    or money(receipt["cost"]) != money(row["costPrice"])
                    or type(receipt["mediaCount"]) is not int or receipt["mediaCount"] < 2
                    or receipt["inventoryPolicy"] != "DENY" or receipt["taxable"] is not False
                    or receipt["vendor"] != "Periwinkle By Sherry"
                    or any(receipt[key] is not True for key in ["singleDefaultVariant", "tracked",
                           "requiresShipping", "categorySet", "collectionsVerified", "contentVerified"])):
                raise ValueError()
        except (KeyError, TypeError, ValueError, RegisterError):
            raise RegisterError("Fresh Shopify publication/listing verification is incomplete or mismatches the row")

    def transition(self, action, sku, expected, url=None, receipt=None):
        with self.lock():
            if self.pending(sku):
                raise RegisterError("Recover the pending transaction for this SKU first")
            snapshot = self.snapshot(sku)
            row, job = snapshot["row"], snapshot["job"]
            status = row["productStatus"]
            if job and ((action == "start" and status == "IN_PROGRESS")
                        or (action == "ready" and status == "READY_TO_PUBLISH" and row["shopifyUrl"] == canonical_url(url))
                        or (action == "publish" and status == "LIVE")):
                return {"changed": False, "row": row}
            self.assert_fresh(snapshot, expected)
            if money(row["sellingPrice"]) <= money(row["costPrice"]):
                raise RegisterError("Selling price must be above cost before automatic processing")
            timestamp, transaction_id = now(), str(uuid.uuid4())
            after = dict(row)
            if action == "start" and status == "NEW":
                if job:
                    raise RegisterError("This submission was already claimed and moved back; explicit rework is required")
                self.stock_ready(row)
                after["productStatus"] = "IN_PROGRESS"
                job = {"version": 1, "sku": row["sku"], "submittedAt": row["submittedAt"],
                       "startedAt": timestamp, "stage": "awaiting_photo"}
                event_type, previous, new = "PROCESSING_STARTED", "NEW", "IN_PROGRESS"
            elif action == "ready" and status in {"IN_PROGRESS", "READY_TO_PUBLISH"} and job:
                if not re.fullmatch(r"gid://shopify/Product/[0-9]+", job.get("productId", "")):
                    raise RegisterError("Checkpoint the verified Shopify product ID first")
                verified_url = canonical_url(url)
                if not job.get("handle") or urlsplit(verified_url).path != "/products/" + job["handle"]:
                    raise RegisterError("URL must match the verified handle in the job checkpoint")
                after.update(productStatus="READY_TO_PUBLISH", shopifyUrl=verified_url)
                event_type, previous, new = "SHOPIFY_URL_RECORDED", row["shopifyUrl"], after["shopifyUrl"]
                job = {**job, "stage": "ready"}
            elif action == "publish" and status == "READY_TO_PUBLISH" and job:
                self.publication_receipt(row, job, receipt)
                after.update(productStatus="LIVE", publishedAt=timestamp)
                event_type, previous, new = "PRODUCT_PUBLISHED", status, "LIVE"
                job = {**job, "stage": "published", "publicationReceipt": receipt}
            else:
                raise RegisterError("Unsupported transition or product not owned by this agent workflow")
            event = {"timestamp": timestamp, "sku": row["sku"], "eventType": event_type,
                     "previousValue": previous, "newValue": new, "source": "operator",
                     "notes": "Agent /add-products; transaction " + transaction_id}
            before_bytes = self.path(snapshot["path"]).read_bytes()
            if digest(before_bytes) != expected:
                raise RegisterError("Register changed before transaction preparation")
            intent = {"version": 1, "id": transaction_id, "state": "pending", "action": action,
                      "sku": row["sku"], "beforeText": before_bytes.decode(),
                      "beforeSha256": expected, "before": row, "after": after, "jobAfter": job, "event": event}
            self.immutable(f"agent/transactions/{transaction_id}.json", encoded(intent))
            self.fault("intent")
            return self.finish(intent, receipt)

    def finish(self, intent, receipt=None):
        # Derive every path; never execute path strings from a journal file.
        transaction_id = str(uuid.UUID(intent["id"]))
        key = self.key(intent["sku"])
        before, after = intent["before"], intent["after"]
        allowed_changes = {"productStatus", "shopifyUrl", "publishedAt"}
        transitions = {"start": {("NEW", "IN_PROGRESS", "PROCESSING_STARTED")},
                       "ready": {("IN_PROGRESS", "READY_TO_PUBLISH", "SHOPIFY_URL_RECORDED"),
                                 ("READY_TO_PUBLISH", "READY_TO_PUBLISH", "SHOPIFY_URL_RECORDED")},
                       "publish": {("READY_TO_PUBLISH", "LIVE", "PRODUCT_PUBLISHED")}}
        allowed = transitions.get(intent["action"], set())
        if (set(before) != set(after) or any(before[k] != after[k] for k in before if k not in allowed_changes)
                or (before["productStatus"], after["productStatus"], intent["event"]["eventType"]) not in allowed
                or before["sku"] != intent["sku"] or intent["jobAfter"]["submittedAt"] != before["submittedAt"]
                or intent["jobAfter"].get("sku") != before["sku"] or intent["event"].get("sku") != before["sku"]
                or digest(intent["beforeText"].encode()) != intent["beforeSha256"]
                or json.loads(intent["beforeText"]) != before):
            raise RegisterError("Invalid transaction intent")
        if intent["action"] == "publish":
            self.publication_receipt(before, intent["jobAfter"], receipt)
            intent["jobAfter"]["publicationReceipt"] = receipt
        source = f"register/{before['productStatus']}/{key}.json"
        target = f"register/{after['productStatus']}/{key}.json"
        old, new = intent["beforeText"].encode(), encoded(after)
        for status in STATUSES:
            relative = f"register/{status}/{key}.json"
            if self.path(relative).exists():
                content = self.path(relative).read_bytes()
                if not ((relative == source and content == old) or (relative == target and content == new)):
                    raise RegisterError("Current row differs from the transaction; no automatic overwrite")
        if not self.path(source).exists() and not self.path(target).exists():
            raise RegisterError("Transaction row was removed")
        self.immutable(f"register/_replaced/agent-{transaction_id}/{key}.json", old)
        self.fault("archive")
        if source == target:
            if self.path(target).read_bytes() == old:
                self.atomic(target, new)
        else:
            self.immutable(target, new)
        self.fault("row")
        self.immutable(f"log/agent-{transaction_id}-{key}.json", encoded(intent["event"]))
        self.fault("log")
        if source != target and self.path(source).exists():
            if self.path(source).read_bytes() != old:
                raise RegisterError("Source changed before archiving completed")
            self.path(source).unlink()  # An exact copy was verified in _replaced first.
        self.fault("source_removed")
        self.atomic(f"agent/jobs/{key}.json", encoded(intent["jobAfter"]))
        self.atomic(f"agent/transactions/{transaction_id}.json", encoded({**intent, "state": "complete"}))
        return {"changed": True, "row": after, "transactionId": transaction_id}

    def recover(self, transaction_id, receipt=None):
        with self.lock():
            transaction_id = str(uuid.UUID(transaction_id))
            intent = self.json(f"agent/transactions/{transaction_id}.json")
            if intent["state"] == "complete":
                return {"changed": False, "row": intent["after"]}
            return self.finish(intent, receipt)

    def checkpoint(self, sku, expected, patch):
        if not isinstance(patch, dict) or set(patch) - PATCH_KEYS or len(encoded(patch)) > 65536:
            raise RegisterError("Checkpoint accepts only processing metadata, never register fields or image bytes")
        if "stage" in patch and patch["stage"] not in STAGES:
            raise RegisterError("Unknown checkpoint stage")
        for key, kind in [("productId", "Product"), ("variantId", "ProductVariant"), ("inventoryItemId", "InventoryItem")]:
            if key in patch and (not isinstance(patch[key], str) or not re.fullmatch(r"gid://shopify/" + kind + r"/[0-9]+", patch[key])):
                raise RegisterError("Invalid Shopify identifier")
        if "imageFileIds" in patch and (not isinstance(patch["imageFileIds"], list) or any(
                not isinstance(value, str) or not re.fullmatch(r"gid://shopify/(?:MediaImage|GenericFile|Video|Model3d)/[0-9]+", value)
                for value in patch["imageFileIds"])):
            raise RegisterError("Image files must be Shopify IDs, not image data")
        if "inventoryInitialized" in patch and not isinstance(patch["inventoryInitialized"], bool):
            raise RegisterError("inventoryInitialized must be a boolean")
        if "inventoryIdempotencyKey" in patch:
            uuid.UUID(patch["inventoryIdempotencyKey"])
        if "handle" in patch and (not isinstance(patch["handle"], str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", patch["handle"])):
            raise RegisterError("Invalid product handle")
        if "lastError" in patch and (not isinstance(patch["lastError"], str) or len(patch["lastError"]) > 4000):
            raise RegisterError("lastError must be a short text message")
        if "imageHashes" in patch and (not isinstance(patch["imageHashes"], list) or
                any(not isinstance(h, str) or not re.fullmatch(r"[a-f0-9]{64}", h) for h in patch["imageHashes"])):
            raise RegisterError("Image hashes must be SHA-256 values, not image data")
        with self.lock():
            if self.pending(sku):
                raise RegisterError("Recover the pending transaction first")
            snapshot = self.snapshot(sku)
            self.assert_fresh(snapshot, expected)
            if not snapshot["job"]:
                raise RegisterError("Start this product through the agent helper first")
            if ("productId" in patch and snapshot["job"].get("productId")
                    and snapshot["job"]["productId"] != patch["productId"]):
                raise RegisterError("Shopify product identity cannot change on retry")
            job = {**snapshot["job"], **patch, "updatedAt": now()}
            self.atomic(f"agent/jobs/{self.key(sku)}.json", encoded(job))
            return job


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=DEFAULT_ROOT)
    parser.add_argument("action", choices=["queue", "snapshot", "start", "ready", "publish", "checkpoint", "recover"])
    parser.add_argument("--sku")
    parser.add_argument("--expected-sha256")
    parser.add_argument("--url")
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--patch", type=Path)
    parser.add_argument("--transaction-id")
    args = parser.parse_args()
    try:
        register = Register(args.root)
        receipt = json.loads(args.receipt.read_text()) if args.receipt else None
        if args.action == "queue":
            result = register.queue()
        elif args.action == "recover":
            result = register.recover(args.transaction_id, receipt)
        elif not args.sku:
            parser.error("--sku is required")
        elif args.action == "snapshot":
            result = register.snapshot(args.sku)
        elif args.action == "checkpoint":
            result = register.checkpoint(args.sku, args.expected_sha256, json.loads(args.patch.read_text()))
        else:
            result = register.transition(args.action, args.sku, args.expected_sha256, args.url, receipt)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (RegisterError, OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
