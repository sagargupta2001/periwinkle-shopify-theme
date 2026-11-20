#!/usr/bin/env python3
"""Stage the single signed Client bundle in a versioned shared folder.

python3 stage_client_release.py <signed client dir> <shared destination dir> --folderref <client-folderref.shortcut>
Run build.py with client-folderref.shortcut and --role client first.
"""
import argparse
import hashlib
import json
from pathlib import Path

from build import BUILD, CATEGORIES, CLIENT_MENU, client_bundle, read_folder_reference, read_workflow
from photo_links import CATEGORY_ALBUMS


def stage(source, destination, folderref):
    expected = {client_bundle({"filename": "manifest"}).name + ".shortcut"}
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
    expected_folder = read_folder_reference(str(folderref))
    for name, file in files.items():
        workflow = read_workflow(str(file))
        actions = workflow["WFWorkflowActions"]
        if actions[0]["WFWorkflowActionParameters"].get("WFFile") != expected_folder:
            raise ValueError("Client bundle does not match the supplied client account folder reference")
        menu = actions[1]["WFWorkflowActionParameters"]
        if menu.get("WFMenuItems") != [label for label, _ in CLIENT_MENU] or menu.get("WFMenuPrompt") != f"Periwinkle - Client (build {BUILD})":
            raise ValueError("Expected the self-contained Client role menu")
    manifest = {"build": BUILD, "role": "client", "files": {
        name: {"bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
        for name, content in sorted(payloads.items())}}
    album_list = "\n".join(f"• {name}: {CATEGORY_ALBUMS[code]}" for name, code in CATEGORIES)
    readme = f"""Periwinkle client shortcuts — build {BUILD}

Install on the CLIENT'S iPhone from Files:
iCloud Drive → Periwinkle Product Operations → shortcuts → {destination.name}

Install the ONE file: Periwinkle - Client.shortcut.
It contains New Product, Update Stock, Fix Product and Print Product Label as
its first menu options. No separately installed operation shortcuts are needed.
Choose one operation per run; launch the same Client shortcut for the next task.

Choose Replace when updating an existing Periwinkle - Client. For the first
migration, keep the four old operational shortcuts until the new bundle passes
phone checks. Then remove those old tiles; do not delete the operations folder.
These files use the supplied CLIENT account folder reference. The operator's
Client testing copy has the same name but must remain private on their account.

Create these as Shared Albums and invite the operator's Apple Account:
{album_list}

New Product: select a category and accept/change its number, enter the prices,
choose photos, then paste the copied caption into the category's Shared Album
shown in the notification and post it. The shortcut automatically saves the
target album's existing photo names before posting. After posting, choose
Prepare SKU label or Finish for now; it then locates the newly added photo
and shows it for confirmation. Confirm that photo: its
actual Shared Album name/date are then saved, including upload-generated UUID
names. The operator should not search or manually link a new submission.
No image copy is saved in Drive. If the post is still syncing, use Fix Product
→ Finish photo linking before creating another product in the same album.
If Prepare SKU label was chosen, NIIMBOT then opens the PDF;
tap Add, then Print. Print is manual. Confirm the B1 is connected in NIIMBOT
and that its label roll matches the current 50 × 30 mm PDF.

Update Stock, Fix Product and Print Product Label: choose a category and
enter only the number. Dupatta + 4 means PBS-DUP-004. Leading zeros are optional.
Print Product Label prepares/reprints a label without submitting another product.

Run shortcuts by opening the Shortcuts app and tapping the tile. The previous
client phone did not reliably start them from a Home Screen icon or widget.

The register still contains testing data. Wait for Sagar's reset/go-ahead
before entering real products. First confirm a dummy New Product submission
previews correctly on the operator's phone after Shared Album sync: cross-account
confirmation of the posted album reference has not yet been verified. Also confirm that the new label opens correctly
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
    parser.add_argument("--folderref", type=Path, required=True, help="client account folder reference used for signing")
    args = parser.parse_args()
    manifest = stage(args.source, args.destination, args.folderref)
    print(f"Verified {len(manifest['files'])} signed client shortcuts in {args.destination}")


if __name__ == "__main__":
    main()
