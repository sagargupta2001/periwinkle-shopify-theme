#!/usr/bin/env python3
"""Prints the shortcuts' register as JSON. It only reads: the shortcuts own these files.

    python3 read_register.py [--sku PBS-DUP-004] [--root <folder>]

The folder is explained in docs/product-operations/README.md. A product's status is the
folder its row is in. If a stopped run left a row in two folders, the furthest one counts,
which is the same rule the shortcuts use.
"""
import argparse
import json
import os
import re
import sys

DEFAULT_ROOT = "~/Library/Mobile Documents/com~apple~CloudDocs/Periwinkle Product Operations"
STATUSES = ["NEW", "IN_PROGRESS", "READY_TO_PUBLISH", "LIVE"]
RECORD_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]*\.json$")  # The same names the shortcuts accept
SKIPPED = {"_keep.txt", ".DS_Store"}


def read_folder(folder, problems):
    """Returns {file name: record}, and reports anything in the folder that can't be used."""
    records = {}
    if not os.path.isdir(folder):
        problems.append(f"Missing folder: {folder}")
        return records
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if name in SKIPPED or name.startswith("_") or os.path.isdir(path):
            continue
        if name.endswith(".icloud"):
            problems.append(f"Not downloaded to this Mac yet: {path}")
        elif not RECORD_NAME.match(name):
            problems.append(f"Unexpected file, possibly an iCloud conflict copy: {path}")
        else:
            try:
                with open(path, encoding="utf-8") as f:
                    records[name] = json.load(f)
            except (OSError, ValueError) as error:
                problems.append(f"Can't read {path}: {error}")
    return records


def read_register(root):
    problems = []
    submissions = read_folder(os.path.join(root, "products"), problems)
    rows = {}
    for status in STATUSES:
        for name, row in read_folder(os.path.join(root, "register", status), problems).items():
            if name in rows:
                problems.append(f"{row.get('sku', name)} has a leftover row in {rows[name]['status']}. {status} counts.")
            if row.get("productStatus") != status:
                problems.append(f"{row.get('sku', name)} is in the {status} folder but says {row.get('productStatus')}.")
            rows[name] = {**row, "status": status}
    for name, row in rows.items():
        if name not in submissions:
            problems.append(f"{row.get('sku', name)} has a row but no submission in products/.")
    for name, submission in submissions.items():
        if name not in rows:
            problems.append(f"{submission.get('sku', name)} was submitted but has no row: a run stopped partway.")
    pending = read_folder(os.path.join(root, "stock-requests", "PENDING"), problems)
    return {
        "products": [rows[name] for name in sorted(rows)],
        "pendingStockRequests": [pending[name] for name in sorted(pending)],
        "problems": problems,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sku", help="only this product, in any case")
    parser.add_argument("--root", default=os.path.expanduser(DEFAULT_ROOT))
    args = parser.parse_args()
    if not os.path.isdir(args.root):
        sys.exit(f"Can't find the register at {args.root}. Is iCloud Drive on for this Mac?")
    result = read_register(args.root)
    if args.sku:
        wanted = args.sku.lower()
        result["products"] = [p for p in result["products"] if str(p.get("sku", "")).lower() == wanted]
        result["pendingStockRequests"] = [r for r in result["pendingStockRequests"] if str(r.get("sku", "")).lower() == wanted]
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
