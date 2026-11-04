#!/usr/bin/env python3
"""Creates the record folders and starting files. Safe to run again: records and existing starting files are left alone."""
import json
import os
import sys

from build import CATEGORIES

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/Library/Mobile Documents/com~apple~CloudDocs/Periwinkle Product Operations")
FOLDERS = ["products", "log", "views",
           "register/NEW", "register/IN_PROGRESS", "register/READY_TO_PUBLISH", "register/LIVE",
           "stock-requests/PENDING", "stock-requests/COMPLETED", "stock-requests/REJECTED",
           # Superseded records are moved here, never deleted
           "register/_replaced", "register/_cancelled", "products/_cancelled", "stock-requests/_handled"]
SETTINGS = {
    "productStatuses": ["NEW", "IN_PROGRESS", "READY_TO_PUBLISH", "LIVE"],
    "stockStatuses": ["IN_STOCK", "OUT_OF_STOCK"],
    "stockRequestStatuses": ["PENDING", "COMPLETED", "REJECTED"],
    "defaultCurrency": "INR",
    "timeZone": "Asia/Kolkata",
}

# Every folder keeps this placeholder so it is never empty, including PENDING after the last
# request is processed. Shortcuts skip names that start with an underscore.
for folder in FOLDERS:
    path = os.path.join(ROOT, folder)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "_keep.txt"), "w") as f:
        f.write("Keeps this folder from being empty. Please don't delete it.\n")
# Each category's number already in use outside the register. New Product suggests the next one.
INITIAL_FILES = {"settings.json": SETTINGS, "sku-start.json": {code: 0 for _, code in CATEGORIES}}
for name, content in INITIAL_FILES.items():
    path = os.path.join(ROOT, name)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(content, f, indent=2)
print("Ready:", ROOT)
