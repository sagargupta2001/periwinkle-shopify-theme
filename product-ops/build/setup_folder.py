#!/usr/bin/env python3
"""Creates the record folders and settings file. Safe to run again: records and an existing settings file are left alone."""
import json
import os
import sys

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
settings = os.path.join(ROOT, "settings.json")
if not os.path.exists(settings):
    with open(settings, "w") as f:
        json.dump(SETTINGS, f, indent=2)
print("Ready:", ROOT)
