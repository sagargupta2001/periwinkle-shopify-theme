# Installation

How to set up the folder and shortcuts on a new phone. The Mac is only needed to build
and sign the shortcuts. Daily use is on iPhone.

## What's needed

- iPhone with the Shortcuts, Files and Numbers apps. Numbers is a free download.
- iCloud Drive turned on, and enough free iCloud space for a few MB.
- For deleting old Numbers copies: **Settings → Apps → Shortcuts → Advanced → Allow
  Deleting Without Confirmation**, on the operator's phone only.

## 1. The folder (operator, once)

1. Open **Files → Browse → iCloud Drive**.
2. Tap **•••**, then **New Folder**, and name it `Periwinkle Product Operations`. It must
   be at the top level, not inside `Shortcuts`.
3. On the Mac, run the setup script to create the subfolders. It's safe to run again.

```bash
python3 product-ops/build/setup_folder.py
```

### Initial files

The folder needs these before any shortcut runs. Lookups list a folder before checking
inside it, so a missing folder stops the shortcut.

| Path | What it's for |
|---|---|
| `products/` | One file per submitted product |
| `products/_cancelled/` | Cancelled submissions |
| `register/NEW/` | Products waiting to be started |
| `register/IN_PROGRESS/` | Products being listed |
| `register/READY_TO_PUBLISH/` | Listed products with a link, waiting to be marked live |
| `register/LIVE/` | Live products |
| `register/_replaced/` | Earlier versions of each product's row |
| `register/_cancelled/` | Rows of cancelled submissions |
| `stock-requests/PENDING/` | Requests waiting for the operator |
| `stock-requests/COMPLETED/` | Completed requests |
| `stock-requests/REJECTED/` | Rejected requests |
| `stock-requests/_handled/` | The original of each processed request |
| `log/` | The Activity log, one file per event |
| `views/` | Tables for Numbers |
| `_keep.txt` in **each folder above** | A one-line placeholder that keeps the folder from being empty, so iCloud always keeps it. Shortcuts skip it. |
| `settings.json` | Valid statuses, default currency (INR) and time zone (Asia/Kolkata), for reference. No shortcut reads it today. |
| `sku-start.json` | Each category's starting number, all 0 to begin with, so the first suggestion is `001`. New Product reads it. |

**Setting a starting number:** if a category already has SKUs outside the register, set its
number to the highest in use, on the Mac, for example `"SAR": 408`, and the next suggestion
is `409`. A category missing from the file counts as 0.

Everything else is created as the shortcuts run: product and request records, log entries,
timestamped folders under `_replaced`, `_cancelled` and `_handled`, and the CSV files in
`views/`.

**If a folder gets deleted by mistake,** run the script again. It recreates anything missing,
and it doesn't touch your records, or an existing `settings.json` or `sku-start.json`. Records already deleted
can't be rebuilt from it, so check **Files → Recently Deleted** first.

## 2. The operator's shortcuts

1. Make the [folder reference and build](building-and-signing.md#for-a-new-apple-account).
2. Open each signed file on the Mac and click **Add Shortcut**. They sync to any iPhone
   on the same Apple Account.
3. Close the old shortcut's editor before importing. Choose Replace when offered,
   then check there's one current copy of each. If an older copy had a different
   name, remove its tile after identifying the new one. Shortcut tiles and shared
   product records are separate; do not delete the shared data folders.
4. Run each once from the Shortcuts app, tapping **Always Allow** on prompts.

## 3. Handing over to the client

Tested on 5 November 2026, using the steps below and installing from the shared folder.

**How the client's phone reaches your folder:** you share the folder with the client's
Apple Account, with permission to make changes. It then appears in the client's iCloud
Drive, and iCloud keeps both phones in sync. When the client's shortcut saves a file, it
saves into that shared folder, and the file appears on your phone too. Nothing is sent
to you directly.

**Why the client needs separate copies:** each shortcut stores a reference to the folder,
and that reference contains IDs tied to the Apple Account that made it. The client's IDs
differ from the operator's, so the client's shortcuts are built with a reference made on
the client's phone. The logic is identical, and only that reference differs.

**Steps:**
1. In Files, long-press the folder, tap **Share**, set it so only invited people can
   access it and they can make changes, and invite the client's Apple Account. The exact
   wording may vary with the iOS version.
2. The client accepts the invitation, and opens the folder once in Files.
3. On the client's phone, make a shortcut called `folderref` with one action, **Get
   Contents of Folder**, pointing at the shared folder. Share it as a file, and get it to
   the Mac, for example by AirDrop or by saving it in the shared folder.
4. Build the client's four shortcuts with it (build 10 added Print Product Label;
   build 11 standardises manual SKU entry). See the complete
   [release commands](building-and-signing.md#rebuild-and-share-a-release).

```bash
python3 product-ops/build/build.py product-ops/local/client-folderref.shortcut product-ops/local/client --role client
```

5. AirDrop the four signed files to the client, who taps each and then **Add Shortcut**. If
   you're not together, stage them in the shared folder with
   `stage_client_release.py`. For build 11 she opens **Files → iCloud Drive →
   Periwinkle Product Operations → shortcuts → client-build-11**, then opens the
   four .shortcut files and chooses Replace for matching older shortcuts. Keep
   this version folder for reinstalling. It contains README.txt and a file-hash
   manifest, and never includes the raw folder-reference file or operator files.
6. On the client's phone, run New Product with a test SKU, and check the record reaches
   your phone. Then run Update Stock and Fix Product.

**Before sharing:** cost prices will be visible to everyone with access to the folder.
Also delete any `folderref` file left in the folder.

## Client instructions

Run New Product, Update Stock and Fix Product by opening the **Shortcuts** app and tapping the
shortcut's tile. Print Product Label is also a client shortcut, for retries and
reprints without submitting another product. Install NIIMBOT from the App Store
and connect her B1 inside it. Match the label roll size (the initial PDF template
is 50 × 30 mm). The client doesn't need the operator shortcuts.

- **Check Home Screen icons on each phone.** On 5 November 2026 an icon opened the first menu on the
  operator's phone. On the client's phone, neither an icon nor a widget opened anything, and the menu
  was waiting when the Shortcuts app was opened separately. The cause isn't known yet. Some users report
  that prompts get stuck outside the Shortcuts app.
- **Tap the tile, not its •••.** The ••• opens the editor. Shortcuts can't be locked against editing,
  as far as we could find.
- **If a shortcut gets changed or deleted,** delete it and reinstall it from
  the current version folder under the shared folder's `shortcuts/` directory.
  Records are in the shared folder, not in the shortcut, so they aren't
  affected. Files already saved by a wrongly edited shortcut would still need checking.

## If something goes wrong

| What you see | What it means |
|---|---|
| "ToolKit client implementation did not implement a ToolDialogHandler…" | See [the iPhone behaviours](building-and-signing.md#iphone-behaviours-these-shortcuts-rely-on). Check the Activity log before retrying, as the record may already be saved. |
| "The file couldn't be opened" | A folder hasn't loaded on the phone, or the folder reference doesn't suit this account. |
| "Unknown Action" in the editor | The action doesn't exist in this version of Shortcuts. |
| Mail opens rather than Numbers | The saved file isn't a `.csv`. Check `views/`. |
| A shortcut is called `… 2` | A duplicate import. Delete the older one. |
