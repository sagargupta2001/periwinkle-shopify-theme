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

## 2. The operator's shortcuts

1. Make the [folder reference and build](building-and-signing.md#for-a-new-apple-account).
2. Open each signed file on the Mac and click **Add Shortcut**. They sync to any iPhone
   on the same Apple Account.
3. Check there's one copy of each. Importing a name that already exists can add a copy
   called `… 2`, so delete the old one first when updating.
4. Run each once from the Shortcuts app, tapping **Always Allow** on prompts.

## 3. Handing over to the client

This hasn't been tested yet. It's the biggest remaining unknown, so try it with one
small step before anything else.

**How the client's phone reaches your folder:** you share the folder with the client's
Apple Account, with permission to make changes. It then appears in the client's iCloud
Drive, and iCloud keeps both phones in sync. When the client's shortcut saves a file, it
saves into that shared folder, and the file appears on your phone too. Nothing is sent
to you directly.

**Why the client probably needs separate copies:** each shortcut stores a reference to
the folder, and that reference contains IDs tied to the Apple Account that made it. Your
copies point at the folder as your account sees it. They may not find it from the
client's account. So the client probably needs the same shortcuts built with a reference
made on the client's phone. The logic is identical, and only that reference differs.

**Steps:**
1. In Files, long-press the folder, tap **Share**, set it so only invited people can
   access it and they can make changes, and invite the client's Apple Account. The exact
   wording may vary with the iOS version.
2. The client accepts the invitation, and opens the folder once in Files.
3. On the client's phone, make a shortcut called `folderref` with one action, **Get
   Contents of Folder**, pointing at the shared folder. Share it as a file, and get it to
   the Mac, for example by AirDrop or by saving it in the shared folder.
4. Build the client's three shortcuts with it.

```bash
python3 product-ops/build/build.py product-ops/local/client-folderref.shortcut product-ops/local/client --role client
```

5. AirDrop the three signed files to the client, who taps each and then **Add Shortcut**.
6. On the client's phone, run New Product with a test SKU, and check the record reaches
   your phone. Then run Update Stock and Fix Product.

**Before sharing:** cost prices will be visible to everyone with access to the folder.
Also delete any `folderref` file left in the folder.

## Client instructions

Add New Product, Update Stock and Fix Product to the Home Screen from each shortcut's
**Share** menu, so they're one tap away. The client doesn't need the operator shortcuts.

## If something goes wrong

| What you see | What it means |
|---|---|
| "ToolKit client implementation did not implement a ToolDialogHandler…" | See [the iPhone behaviours](building-and-signing.md#iphone-behaviours-these-shortcuts-rely-on). Check the Activity log before retrying, as the record may already be saved. |
| "The file couldn't be opened" | A folder hasn't loaded on the phone, or the folder reference doesn't suit this account. |
| "Unknown Action" in the editor | The action doesn't exist in this version of Shortcuts. |
| Mail opens rather than Numbers | The saved file isn't a `.csv`. Check `views/`. |
| A shortcut is called `… 2` | A duplicate import. Delete the older one. |
