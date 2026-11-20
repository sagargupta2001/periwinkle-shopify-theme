# Recreating and recovering product operations

The repository recreates the complete **folder structure, initial configuration
and shortcut programs**. It does not contain your product records, prices,
stock history, photo mappings, account references or Shared Album images.
Existing operational data must come from Recently Deleted or a data backup.
Signed-shortcut/development backups are not backups of the register itself.

## Recreate the complete structure

From the repo root on the Mac:

```bash
python3 product-ops/build/setup_folder.py
```

Or choose an explicit destination:

```bash
python3 product-ops/build/setup_folder.py "/path/to/Periwinkle Product Operations"
```

The script creates every folder below with a _keep.txt placeholder, and creates
settings.json and sku-start.json only when absent. Rerunning does not overwrite
existing records, photo references, snapshots, settings or SKU starting values.

```text
Periwinkle Product Operations/
  settings.json
  sku-start.json
  products/
    _cancelled/
  register/
    NEW/
    IN_PROGRESS/
    READY_TO_PUBLISH/
    LIVE/
    _replaced/
    _cancelled/
  stock-requests/
    PENDING/
    COMPLETED/
    REJECTED/
    _handled/
  log/
  views/
  photo-links/
  photo-pending/
  shortcuts/
```

Timestamped archive subfolders, actual JSON records and CSV exports are created
at runtime. Client release directories are created by stage_client_release.py.
Operator installers and raw account references stay outside this shared folder.

## What the photo folders contain

**photo-links/<sku>.json** holds the album name, exact album photo name and Date
Taken, plus sku/version/source metadata. Confirmed intake references have
source shared_album_confirmed. A pending intake uses client_intake_pending;
a manual recovery link can have no source field. verified_shared_name is the
one-time recovery state for a name explicitly checked by the user.

**photo-pending/<sku>.json** initially has state pending and beforeNames: the
album-name snapshot captured before posting. The client confirms the newly
posted asset, then the snapshot file is overwritten with a small complete
marker. Finish a delayed confirmation through Fix Product → Finish photo linking
before creating another product in that album.

Both folders contain metadata only. Images remain in Shared Albums. Restoring
metadata does not restore an image deleted from an album; preview still checks
current membership. CSVs are derived views and cannot restore all source data.

## If files or the whole folder were deleted

1. Check Files → Recently Deleted or your data backup first. Restoring the
   original data preserves history that setup cannot reconstruct.
2. If recreating an empty root, run setup and restore the data directories and
   configuration from backup: products, register, stock-requests, log,
   photo-links, photo-pending, settings.json and sku-start.json. CSV views can
   be regenerated. Rebuild installer packages rather than relying on old files.
3. If records/counters cannot be restored, establish the highest previously
   allocated SKU number in every category and update sku-start.json before new
   intake. Default zeros are for a new empty register, not evidence that old
   identifiers are unused.
4. Share the recreated root with the client's account, with change access,
   and have both accounts open it in Files. Create fresh account-specific
   folder references pointing to that root. A same-name replacement has new
   folder IDs, so old installed references must not be assumed to work.
5. Follow [Building and signing](building-and-signing.md) to rebuild both
   operator-account role bundles and the single client-account Client bundle.
   Install each account's own files, choosing Replace. If restored installer directories
   contain different signed files, stage rebuilt files in a new release directory;
   the packaging script intentionally refuses to overwrite a different release.
6. Keep the existing Shared Albums when they still exist, and verify both
   accounts use the same albums listed in [New Product](new-product.md#automatic-photo-reference).
   Operations-folder reconstruction does not recreate or delete those albums.
7. Verify a restored SKU's prices/status and photo preview, then a dummy new
   intake and client-to-operator handoff before resuming actual operations.

If photo links are missing without a backup, Shortcuts cannot reconstruct the
SKU relationship from Shared Album comments automatically. Reconfirm the correct
image once through Register → Link or change photo. If a pending snapshot was
lost, restore it or use that same manual recovery route; do not treat every
existing album image as a newly posted product.

## What to retain privately

Keep a recoverable copy of the operational data directories/configuration, plus
the two account references while they remain valid. Keep the current signed
release or regenerate it from source. The repository's ignored local development
archive only preserves old installers/diagnostics and is not a complete live-data
backup. Never put these private files in the public Git repository.
