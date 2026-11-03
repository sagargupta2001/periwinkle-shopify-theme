# Building and signing

The shortcuts are generated from scripts in [`product-ops/build/`](../../product-ops/build/),
so they can be recreated if one is deleted, and changes are reviewed like any other code.
**Change the scripts, not the shortcut in the app.** A change made in the app is lost at
the next build.

| File | What it does |
|---|---|
| `shortcutlib.py` | Writes the shortcut file format: actions, variables, ifs, loops and menus |
| `build.py` | One function per shortcut, plus signing |
| `test_build.py` | Checks each shortcut for known mistakes, with no phone or signing |
| `setup_folder.py` | Creates the record folders and `settings.json` |

Signed files and folder references contain iCloud IDs, and this repo is public. They go
in `product-ops/local/`, which git ignores.

## Build everything

Needs a Mac with Shortcuts, signed in to iCloud, and Python 3. This assumes the folder
reference is saved at `product-ops/local/operator-folderref.shortcut`.

```bash
python3 product-ops/build/build.py product-ops/local/operator-folderref.shortcut product-ops/local/signed
```

Options:
- `--role client` or `--role operator` builds one side only.
- `--only register` builds shortcuts whose name contains that text.

The file name becomes the shortcut's name on import, so `build.py` names the files.

## Changing a shortcut

1. Pull `main`, and edit the shortcut's function in `build.py`.
2. Raise `BUILD` in `build.py`. It shows in Work on Product's first menu, so you can
   check which version a phone has.
3. Run the checks, from `product-ops/build/`:

```bash
python3 -m unittest test_build
```

4. Build with `--only`, delete the old copy on the phone, and open the new file.
5. Test it on an iPhone. The Mac's command line can't show prompts, so it can't test these.
6. Update that shortcut's page in these docs, in the same PR.

Using a new action? Test it on an iPhone, then add it to `TESTED_ACTIONS` in `test_build.py`.

## Signing

`build.py` calls Apple's own tool:

```bash
shortcuts sign --mode anyone --input raw.shortcut --output "Periwinkle – Register.shortcut"
```

- **`anyone`** lets the file install on any iPhone, rather than only for people who know
  you. Nothing here embeds a password or Apple ID.
- It sends the shortcut to Apple's servers and needs internet.
- Apple's server sometimes answers 502. `build.py` retries with growing delays, and
  waits between shortcuts.

## For a new Apple Account

A folder reference can't be written by hand. It holds IDs specific to the account, so one
has to be made on that person's iPhone:

1. Create a shortcut named `folderref` with one action, **Get Contents of Folder**.
2. Tap **Folder** in the action and pick the Periwinkle folder.
3. In the list, long-press it, choose **Share**, set **Options** to **Anyone** or **File**,
   and choose **Save to Files**.
4. Copy the file to `product-ops/local/`, and delete it from the shared folder.

`build.py` reads the reference out of that signed file.

## iPhone behaviours these shortcuts rely on

These were all found by testing on iOS, and they aren't obvious. `test_build.py` enforces
the ones it can.

| Behaviour | What the scripts do |
|---|---|
| Using any value read from a file after that file moved or was deleted stops the run with a "ToolDialogHandler" error. Copying it to a Text action first doesn't help. | Moving the old file is the last step in each flow, and messages come before it. |
| Getting a missing file fails if the phone hasn't loaded that folder, even with "error if not found" off. | `lookup()` lists the folder first. |
| Move File can't replace a file of the same name. | `archive()` moves each file into its own timestamped folder. |
| The extension in the item's name sets the saved type, whatever the path says. | Register passes its own `name`. |
| `is.workflow.actions.folder` shows as "Unknown Action", although macOS lists it. | The folder comes from a File action. |
| Asking for a folder during import loops on the Mac. | The reference is built into the file. |
| Unbound parameters can silently pick up odd values. Text fields such as Trim and Match need a text token, not a plain variable. | `text()` is used for these. |
| Opening a sheet: Mail opened when the file was saved as `.json` with no `WFApp` setting. A real `.csv` with `WFApp` set opens Numbers. Which of the two mattered wasn't isolated. | Register does both. |
| Numbers changes `0012` to `12`, even in quotes, but keeps `="0012"`. | Register writes SKUs that way. |

Two earlier explanations turned out to be wrong, in case they come up again: the delete
action, and running from a menu, weren't the causes of the ToolDialogHandler error. Delete
and move both work; only values used afterwards fail.

## Reading a signed shortcut

To see what's inside a signed file, for example how the app stored a setting, extract the
signing key from it and unpack it. `read_folder_reference()` in `build.py` shows how, using
`openssl`, `aea` and `aa`.
