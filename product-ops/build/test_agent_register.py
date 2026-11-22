"""Real filesystem transitions and crash recovery, isolated from iCloud/Shopify."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[2] / ".claude/skills/add-products"
sys.path.insert(0, str(SKILL))
from register_ops import Register, RegisterError, encoded


class AgentRegister(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for folder in ["products", "register/_replaced", "log", "stock-requests/PENDING",
                       "photo-links", "photo-pending", *["register/" + s for s in ["NEW", "IN_PROGRESS", "READY_TO_PUBLISH", "LIVE"]]]:
            (self.root / folder).mkdir(parents=True, exist_ok=True)
        self.sku = "PBS-SAR-001"
        self.row = {"sku": self.sku, "costPrice": 100, "sellingPrice": 250,
                    "productStatus": "NEW", "stockStatus": "IN_STOCK", "shopifyUrl": "",
                    "submittedAt": "2026-11-22T10:00:00+05:30", "publishedAt": "",
                    "lastStockUpdateAt": "", "operatorNotes": "Keep this note"}
        self.write("products/pbs-sar-001.json", {"sku": self.sku, "submittedAt": self.row["submittedAt"],
                                                "costPrice": 100, "sellingPrice": 250})
        self.write("register/NEW/pbs-sar-001.json", self.row)
        self.write("photo-links/pbs-sar-001.json", {"photoName": "keep-photo-reference"})
        self.write("stock-requests/PENDING/request.json", {"sku": "PBS-SAR-999", "requestedStockStatus": "OUT_OF_STOCK"})
        self.register = Register(self.root)
        self.url = "https://periwinklebysherry.com/products/test-saree"

    def write(self, relative, value):
        (self.root / relative).write_bytes(encoded(value))

    def move(self, action, **kwargs):
        snapshot = self.register.snapshot(self.sku)
        return self.register.transition(action, self.sku, snapshot["sha256"], **kwargs)

    def ready(self):
        self.move("start")
        snapshot = self.register.snapshot(self.sku)
        self.register.checkpoint(self.sku, snapshot["sha256"], {"productId": "gid://shopify/Product/123", "handle": "test-saree"})
        self.move("ready", url=self.url)

    def receipt(self, **overrides):
        return {"sku": self.sku, "productId": "gid://shopify/Product/123", "url": self.url,
                "checkedAt": datetime.now(timezone.utc).isoformat(), "status": "ACTIVE",
                "onlineStorePublished": True, "price": "250.00", "cost": "100.00", "mediaCount": 2,
                "singleDefaultVariant": True, "tracked": True, "inventoryPolicy": "DENY", "taxable": False,
                "requiresShipping": True, "vendor": "Periwinkle By Sherry", "categorySet": True,
                "collectionsVerified": True, "contentVerified": True, **overrides}

    def test_complete_workflow_archives_and_logs_without_changing_prices_stock_or_sources(self):
        preserved = {str(p.relative_to(self.root)): p.read_bytes() for folder in ["products", "photo-links", "stock-requests"]
                     for p in (self.root / folder).rglob("*.json")}
        self.ready()
        self.move("publish", receipt=self.receipt())
        final = self.register.snapshot(self.sku)["row"]
        self.assertEqual(final["productStatus"], "LIVE")
        self.assertEqual(final["shopifyUrl"], self.url)
        self.assertTrue(final["publishedAt"])
        for key in ["sku", "costPrice", "sellingPrice", "stockStatus", "submittedAt", "lastStockUpdateAt", "operatorNotes"]:
            self.assertEqual(final[key], self.row[key])
        self.assertEqual(len(list((self.root / "register/_replaced").glob("*/*.json"))), 3)
        events = [json.loads(p.read_text()) for p in (self.root / "log").glob("*.json")]
        self.assertEqual({event["eventType"] for event in events},
                         {"PROCESSING_STARTED", "SHOPIFY_URL_RECORDED", "PRODUCT_PUBLISHED"})
        self.assertTrue(all(event["source"] == "operator" for event in events))
        for name, data in preserved.items():
            self.assertEqual((self.root / name).read_bytes(), data)

    def test_retry_is_a_noop_and_preserves_first_publication_time(self):
        self.ready()
        self.move("publish", receipt=self.receipt())
        before = self.register.snapshot(self.sku)
        result = self.register.transition("publish", self.sku, "old-retry-fingerprint", receipt=None)
        self.assertFalse(result["changed"])
        self.assertEqual(self.register.snapshot(self.sku), before)
        self.assertEqual(len(list((self.root / "log").glob("*.json"))), 3)

    def test_stale_snapshot_cannot_overwrite_client_corrections(self):
        original = self.register.snapshot(self.sku)
        corrected = {**self.row, "sellingPrice": 300}
        self.write("register/NEW/pbs-sar-001.json", corrected)
        with self.assertRaisesRegex(RegisterError, "changed"):
            self.register.transition("start", self.sku, original["sha256"])
        self.assertEqual(self.register.snapshot(self.sku)["row"], corrected)
        self.assertEqual(list((self.root / "log").iterdir()), [])

    def test_publication_requires_fresh_matching_shopify_verification(self):
        self.ready()
        invalid = [None, self.receipt(onlineStorePublished=False), self.receipt(cost="101"),
                   self.receipt(mediaCount=1), self.receipt(productId="gid://shopify/Product/999"),
                   self.receipt(checkedAt=(datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()),
                   self.receipt(tracked=False), self.receipt(taxable=True)]
        for receipt in invalid:
            with self.subTest(receipt=receipt), self.assertRaises(RegisterError):
                self.move("publish", receipt=receipt)
        self.assertEqual(self.register.snapshot(self.sku)["row"]["productStatus"], "READY_TO_PUBLISH")
        self.assertEqual(len(list((self.root / "log").glob("*.json"))), 2)

    def test_ready_link_correction_preserves_the_old_row_and_checks_the_verified_handle(self):
        self.ready()
        with self.assertRaisesRegex(RegisterError, "handle"):
            self.move("ready", url="https://periwinklebysherry.com/products/wrong-piece")
        snapshot = self.register.snapshot(self.sku)
        self.register.checkpoint(self.sku, snapshot["sha256"], {"handle": "renamed-saree"})
        self.move("ready", url="https://periwinklebysherry.com/products/renamed-saree")
        self.assertTrue(self.register.snapshot(self.sku)["row"]["shopifyUrl"].endswith("/renamed-saree"))
        archived = [json.loads(p.read_text()) for p in (self.root / "register/_replaced").glob("*/*.json")]
        self.assertTrue(any(row["shopifyUrl"] == self.url for row in archived))

    def test_pending_out_of_stock_request_blocks_start_without_changing_it(self):
        self.write("stock-requests/PENDING/current.json", {"sku": self.sku, "requestedStockStatus": "OUT_OF_STOCK"})
        with self.assertRaisesRegex(RegisterError, "out-of-stock"):
            self.move("start")
        self.assertEqual(self.register.snapshot(self.sku)["row"]["productStatus"], "NEW")
        self.assertTrue((self.root / "stock-requests/PENDING/current.json").exists())

    def test_a_new_out_of_stock_request_blocks_publication_even_with_a_positive_receipt(self):
        self.ready()
        self.write("stock-requests/PENDING/current.json", {"sku": self.sku, "requestedStockStatus": "OUT_OF_STOCK"})
        with self.assertRaisesRegex(RegisterError, "out-of-stock"):
            self.move("publish", receipt=self.receipt())
        self.assertEqual(self.register.snapshot(self.sku)["row"]["productStatus"], "READY_TO_PUBLISH")

    def test_crash_at_each_write_phase_recovers_once_without_losing_rows_or_audit(self):
        for phase in ["intent", "archive", "row", "log", "source_removed"]:
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as temporary:
                # Independent fixture for each interruption.
                root = Path(temporary)
                for directory in self.root.rglob("*"):
                    relative = directory.relative_to(self.root)
                    if directory.is_dir(): (root / relative).mkdir(parents=True, exist_ok=True)
                    elif relative.parts[0] != "agent": (root / relative).write_bytes(directory.read_bytes())
                def fail(actual):
                    if actual == phase: raise RuntimeError("simulated interruption")
                broken = Register(root, fault=fail)
                snapshot = broken.snapshot(self.sku)
                with self.assertRaises(RuntimeError):
                    broken.transition("start", self.sku, snapshot["sha256"])
                recovery = Register(root)
                transaction_id = recovery.pending(self.sku)[0]["id"]
                recovery.recover(transaction_id)
                self.assertEqual(recovery.snapshot(self.sku)["row"]["productStatus"], "IN_PROGRESS")
                self.assertFalse(recovery.recover(transaction_id)["changed"])
                self.assertEqual(len(list((root / "log").glob("*.json"))), 1)
                self.assertEqual(len(list((root / "register/_replaced").glob("*/*.json"))), 1)

    def test_publication_recovery_rechecks_shopify_instead_of_using_a_stale_receipt(self):
        self.ready()
        def fail(phase):
            if phase == "row": raise RuntimeError("interrupted after LIVE row")
        self.register.fault = fail
        with self.assertRaises(RuntimeError): self.move("publish", receipt=self.receipt())
        transaction_id = self.register.pending(self.sku)[0]["id"]
        recovery = Register(self.root)
        with self.assertRaises(RegisterError): recovery.recover(transaction_id)
        recovery.recover(transaction_id, self.receipt())
        self.assertEqual(recovery.snapshot(self.sku)["row"]["productStatus"], "LIVE")

    def test_duplicate_or_conflict_rows_are_not_silently_fixed(self):
        self.write("register/IN_PROGRESS/pbs-sar-001.json", {**self.row, "productStatus": "IN_PROGRESS"})
        with self.assertRaises(RegisterError): self.register.snapshot(self.sku)
        (self.root / "register/IN_PROGRESS/pbs-sar-001.json").unlink()
        self.write("register/NEW/pbs-sar-001 conflict.json", self.row)
        with self.assertRaisesRegex(RegisterError, "conflict"): self.register.snapshot(self.sku)

    def test_checkpoint_cannot_change_register_fields_or_replace_product_identity(self):
        self.move("start")
        snapshot = self.register.snapshot(self.sku)
        with self.assertRaises(RegisterError):
            self.register.checkpoint(self.sku, snapshot["sha256"], {"sellingPrice": 1})
        self.register.checkpoint(self.sku, snapshot["sha256"], {"productId": "gid://shopify/Product/123"})
        with self.assertRaises(RegisterError):
            self.register.checkpoint(self.sku, snapshot["sha256"], {"productId": "gid://shopify/Product/456"})
        with self.assertRaises(RegisterError):
            self.register.checkpoint(self.sku, snapshot["sha256"], {"imageFileIds": ["base64-image-data"]})

    def test_bad_sku_or_symlink_cannot_escape_the_operations_folder(self):
        with self.assertRaises(RegisterError): self.register.snapshot("../../outside")
        (self.root / "register/NEW/pbs-sar-001.json").unlink()
        (self.root / "register/NEW/pbs-sar-001.json").symlink_to(self.root / "products/pbs-sar-001.json")
        with self.assertRaises(RegisterError): self.register.snapshot(self.sku)

    def test_a_longer_valid_number_is_not_mistaken_for_a_conflict_copy(self):
        neighbor = {**self.row, "sku": "PBS-SAR-0010"}
        self.write("products/pbs-sar-0010.json", {"sku": neighbor["sku"], "submittedAt": neighbor["submittedAt"]})
        self.write("register/NEW/pbs-sar-0010.json", neighbor)
        self.assertEqual(self.register.snapshot(self.sku)["row"]["sku"], self.sku)

    def test_new_session_queue_resumes_agent_work_but_not_unrelated_operator_work(self):
        self.move("start")
        another = {**self.row, "sku": "PBS-SAR-002", "productStatus": "IN_PROGRESS"}
        self.write("products/pbs-sar-002.json", {"sku": another["sku"], "submittedAt": another["submittedAt"]})
        self.write("register/IN_PROGRESS/pbs-sar-002.json", another)
        queue = Register(self.root).queue()
        self.assertEqual([item["row"]["sku"] for item in queue["products"]], [self.sku])

    def test_queue_cli_is_read_only_and_transition_cli_accepts_its_snapshot_hash(self):
        def command(*arguments):
            result = subprocess.run([sys.executable, str(SKILL / "register_ops.py"), "--root", str(self.root), *arguments],
                                    capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        queue = command("queue")
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        self.assertFalse((self.root / "agent").exists())
        result = command("start", "--sku", self.sku, "--expected-sha256", queue["products"][0]["sha256"])
        self.assertEqual(result["row"]["productStatus"], "IN_PROGRESS")

    def test_manually_moving_a_published_product_back_does_not_automatically_republish_it(self):
        self.ready()
        self.move("publish", receipt=self.receipt())
        row = self.register.snapshot(self.sku)["row"]
        (self.root / "register/LIVE/pbs-sar-001.json").unlink()
        self.write("register/IN_PROGRESS/pbs-sar-001.json", {**row, "productStatus": "IN_PROGRESS"})
        queue = self.register.queue()
        self.assertEqual(queue["products"], [])
        self.assertTrue(any("rework" in problem for problem in queue["problems"]))


if __name__ == "__main__":
    unittest.main()
