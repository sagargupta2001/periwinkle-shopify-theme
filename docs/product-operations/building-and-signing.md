# Building and signing

The current signed release is **build 19**; installation packages are staged and
phone rollout is pending. Build 18 remains installed. Change the generators, not the installed
shortcut: app-only edits disappear on rebuild. Every operational workflow can
be recreated from source plus the two private account-specific folder references.
See [Recovery](recovery.md) before recreating a deleted operations folder.

## Sources

| File | Purpose |
|---|---|
| `build.py` | Modular operation builders, two role bundles, account binding and Apple signing |
| `shortcutlib.py` | Plist actions, variables, menus and control flow |
| `photo_links.py` | Category albums, uploaded-photo confirmation, pending snapshots and previews |
| `label_printing.py` | SKU-only PDF generation and NIIMBOT handoff |
| `setup_folder.py` | Complete folder structure and non-overwriting initial settings/SKU starts |
| `stage_client_release.py` | Client-only installer package, README and verified hash manifest |
| `.claude/skills/add-products/register_ops.py` | Logged agent start/link/publication updates; independent of installed shortcut builds |
| `test_*.py` | Generator, PDF, photo-flow, folder recovery and data-safety checks |
| `photo_lookup_experiment.py`, `printing_experiment.py` | Reproducible diagnostics; not operational releases |

Signed files, folder references, backups and generated previews stay under
ignored `product-ops/local/`: they can contain account-specific iCloud IDs.
Never commit them to this public repository. Temporary diagnostic exports and
superseded development installers have been cleaned up; their source remains.

## Build all workflows from scratch

Use a Mac with Shortcuts, Python 3, internet for Apple's signing service, and a
saved reference for each account. From the repo root:

```bash
python3 product-ops/build/setup_folder.py
python3 product-ops/build/build.py product-ops/local/operator-folderref.shortcut product-ops/local/releases/build-19/operator --role all
python3 product-ops/build/build.py product-ops/local/client-folderref.shortcut product-ops/local/releases/build-19/client --role client
```

The first build produces **Periwinkle - Operator.shortcut** and
**Periwinkle - Client.shortcut**, both bound to the operator's account. The
Client copy is for own-phone testing. The second produces only **Periwinkle -
Client.shortcut**, bound to the client's account. Their folder references differ,
even though both accounts access the same shared folder. Keep each account's
output in its own directory; the two Client files have the same name.

`--role operator` produces only Operator; `--role client` produces only Client.
`--only` filters role bundle names, not operation names. Each operation remains
an independent builder in source, then is inlined beneath the role's first menu.
There are no Run Shortcut dependencies or separately installed helpers. See
[Role shortcuts](role-shortcuts.md) for the menu map and migration checks.

The operator's two installers belong in a **private iCloud Drive folder outside
the shared operations root**, such as **Periwinkle Operator Install - Build 19 -
2026-11-20**. Use their canonical filenames; no filename aliases are needed.
Do not distribute these account-bound copies to the client. Keep the preceding
release privately until the new bundle passes phone checks.

## Package the client's file

```bash
python3 product-ops/build/stage_client_release.py product-ops/local/releases/build-19/client "$HOME/Library/Mobile Documents/com~apple~CloudDocs/Periwinkle Product Operations/shortcuts/client-build-19" --folderref product-ops/local/client-folderref.shortcut
```

Only the single signed Client file is accepted. The script decodes it and
checks its folder binding against the supplied client reference, its current
build/menu, missing/extra files, unsigned plists and overwriting different
existing files. It writes README.txt and manifest.json, then verifies copied
bytes. Use a new release folder for a later build. Operator-account files and
raw folder references never go into this shared package.

The client opens **Files → iCloud Drive → Periwinkle Product Operations →
shortcuts → client-build-19 → Periwinkle - Client.shortcut** and taps Add Shortcut.
For future releases choose Replace. During the first migration, keep the four
old client tiles until phone checks pass, then remove those tiles only.
Installation never resets the register or changes photo links.

## Test and install a change

1. Fetch the current main branch and edit the generators. Raise BUILD for an
   operational release; both role shortcuts show it in their first menu.
2. Run all checks from the repo root:

```bash
python3 -m unittest discover -s product-ops/build
```

PDF/printing checks need pypdf, ReportLab and Pillow. The bundled Codex Python
runtime includes them; use it when the system Python lacks them.

3. Build and sign. Decode each signed file with read_workflow() to verify the
   account binding and action graph. Verify copies against SHA-256 hashes.
4. Preserve a signed predecessor as a private file. Close old editors, import
   using the existing name and choose Replace. Verify the build and one current
   tile. Do not create Previous Version tiles in the synced library.
5. Test on an iPhone. The Mac CLI cannot validate interactive prompts or iOS
   import/type inference. A new action identifier must pass phone testing before
   entering TESTED_ACTIONS. Record results in [Test report](test-report.md).
6. Update the workflow page, decisions and recovery instructions as needed in
   the same PR.

**Prior build 18 phone result:** Register successfully previewed the existing
PBS-SAR-006 photo after explicit Text conversion for dictionary comparisons.
Build 19 bundles and full new intake/post/confirm/resume, cross-account delivery
and photo-removal behaviour need rollout checks; generator tests do not establish
those results.

## For a new Apple Account or recreated folder

A folder reference holds account-specific identifiers and cannot be written by
hand. Recreating a folder with the same name does not recreate those IDs.

1. On the intended person's iPhone, create a temporary shortcut with one
   **Get Contents of Folder** action. Pick the actual shared operations folder.
2. Share that shortcut as a file (Anyone/File option), then transfer it to the Mac.
3. Save it privately as operator-folderref.shortcut or client-folderref.shortcut
   under product-ops/local/. Never leave the raw export in the shared folder.
4. Rebuild for that account, replace its installed workflows, then delete the
   temporary reference shortcut. Verify the other account independently.

`read_folder_reference()` extracts the reference; `read_workflow()` decodes raw
or Apple-signed files using openssl, aea and aa. The saved references can be
reused only while they still point to the intended folder.

## Adding an SKU category

Add the code to CATEGORIES and its exact Shared Album name to CATEGORY_ALBUMS,
create/share that album, then rebuild. An unmapped future category prompts for
an album name. Set sku-start.json to the highest previously used number when
numbers already exist outside the register; do not reset it during recovery.

## Signing

`build.py` uses Apple's own `shortcuts sign --mode anyone`. It needs internet,
sends the workflow to Apple for validation, retries transient failures, and
waits between files. Anyone mode allows installation without requiring the
recipient to know the sender; the folder reference remains account-specific.

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
| The number keypad in Ask for Input shows no default answer, and drops leading zeros as you type. The text keyboard does neither. | New Product uses the text keyboard for its suggested number. Update Stock and Fix Product use the keypad and pad the number. |
| The Mac can rebind a static descriptor for an iPhone-only app to another Mac app. Legacy app-selection fields may also be ignored. | The NIIMBOT handoff uses `WFSelectedApp` with a Text action containing its bundle ID, resolved at runtime on iPhone. |
| PNG handoffs opened NIIMBOT without importing anything; PDF Open In reached Crop and split with the label. | Use a `.pdf` label. Add and actual printing remain manual in NIIMBOT. |

Two earlier explanations turned out to be wrong, in case they come up again: the delete
action, and running from a menu, weren't the causes of the ToolDialogHandler error. Delete
and move both work; only values used afterwards fail.


## Additional phone findings from builds 13–18

- Shared Album upload can replace an IMG filename with a UUID and change its
  date. Capture the confirmed posted asset, not the original selection's identity.
- Nested Repeat Item variables have distinct names. Photo folder discovery and
  file enumeration use sequential loops to avoid referring to the outer item.
- A missing-file/blank placeholder was not a safe Has Value gate. Enumerate real
  files and use explicit found flags before parsing or querying Photos.
- An If directly on untyped Dictionary Value imported with an empty comparison.
  Photo fields are materialized through Text before string predicates.
- The Quick Look identifier is `is.workflow.actions.previewdocument`.
  `is.workflow.actions.quicklook` is invalid.
- Metadata snapshots/confirmed references contain no image bytes. Views always
  check current Shared Album membership; no personal-library fallback is used.
