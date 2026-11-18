#!/usr/bin/env python3
"""Stage only the four signed client shortcuts in a versioned shared folder.

python3 stage_client_release.py <signed client dir> <shared destination dir>
Run build.py with client-folderref.shortcut and --role client first.
"""
import argparse
import hashlib
import json
from pathlib import Path

from build import BUILD, CLIENT


def stage(source, destination):
    expected = {builder({"filename": "manifest"}).name + ".shortcut" for builder in CLIENT}
    files = {file.name: file for file in source.glob("*.shortcut")}
    if set(files) != expected:
        raise ValueError(f"Expected only the client shortcuts. Missing: {sorted(expected - set(files))}; "
                         f"unexpected: {sorted(set(files) - expected)}")
    payloads = {name: file.read_bytes() for name, file in files.items()}
    for name, content in payloads.items():
        if not content or content.startswith(b"bplist"):
            raise ValueError(f"Not a signed shortcut: {name}")
        target = destination / name
        if target.exists() and target.read_bytes() != content:
            raise ValueError(f"A different release already exists at {target}; use a new version folder")
    manifest = {"build": BUILD, "role": "client", "files": {
        name: {"bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
        for name, content in sorted(payloads.items())}}
    readme = f"""Periwinkle client shortcuts — build {BUILD}

Install on the CLIENT'S iPhone from Files:
iCloud Drive → Periwinkle Product Operations → shortcuts → client-build-{BUILD}

Open each of the four .shortcut files, then tap Add Shortcut:
• Periwinkle – New Product
• Periwinkle – Update Stock
• Periwinkle – Fix Product
• Periwinkle – Print Product Label (new)

Choose Replace when an existing matching shortcut is found. If an older copy
was renamed (for example, New Product without Periwinkle), keep one current
copy of each function after installation. Deleting an old shortcut tile does
not delete product records. Do not delete the shared data folders.

These files use the folder reference made on the client's Apple Account.
Operator copies must not be installed in their place.

New Product: select a category and accept/change its number, enter the prices,
choose photos, paste the copied caption into the Periwinkle Shared Album,
and post it. Only then choose Prepare SKU label. NIIMBOT opens the PDF;
tap Add, then Print. Print is manual. Confirm the B1 is connected in NIIMBOT
and that its label roll matches the current 50 × 30 mm PDF.

Update Stock, Fix Product and Print Product Label: choose a category and
enter only the number. Dupatta + 4 means PBS-DUP-004. Leading zeros are optional.
Print Product Label prepares/reprints a label without submitting another product.

Run shortcuts by opening the Shortcuts app and tapping the tile. The previous
client phone did not reliably start them from a Home Screen icon or widget.

The register still contains testing data. Wait for Sagar's reset/go-ahead
before entering real products. First confirm that the new label opens correctly
and prints at the right size on this phone and printer. PDF import has been
tested on Sagar's phone; the client's physical B1 print and the new dynamic
SKU label generation still need confirmation.

Keep this version folder for reinstalling. manifest.json records file hashes.
"""
    destination.mkdir(parents=True, exist_ok=True)
    for name, content in payloads.items():
        (destination / name).write_bytes(content)
    (destination / "README.txt").write_text(readme, encoding="utf-8")
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for name, content in payloads.items():
        if (destination / name).read_bytes() != content:
            raise OSError(f"Copy verification failed: {name}")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    manifest = stage(args.source, args.destination)
    print(f"Verified {len(manifest['files'])} signed client shortcuts in {args.destination}")


if __name__ == "__main__":
    main()
