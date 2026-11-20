# Test report

## Current release — build 19

20 November 2026. The eight operation builders are now inlined into two
self-contained role bundles, each with four first-menu choices and one account
binding. No Run Shortcut dependencies or installed helpers are required.
Client has 911 actions and Operator has 2,104 actions. After Sagar explicitly
approved Apple signing, all three files were signed: operator-account Client
and Operator, plus client-account Client. Each signed payload was decoded and
its complete action graph compared with a fresh builder after UUID normalization.
The folder bindings match their intended private references and differ between
accounts. Apple's signed payload omits WFWorkflowName; the filename determines
the imported name.

The private **Periwinkle Operator Install - Build 19 - 2026-11-20** iCloud folder
contains both operator-account files, README.txt and a SHA-256 manifest. The
shared **shortcuts/client-build-19** folder contains only client-account Client,
README.txt and manifest.json. Staging rechecked the client binding/current menu;
copied file bytes were verified. No account identifiers or installers are committed.

Mac import did not complete: the native Import dialog kept Open disabled for
the signed file, and subsequent UI access timed out. No new installed role tile
was observed. Files-based iPhone installation and runtime checks are pending;
the existing build-18 operation tiles/installers remain available.

The full generator suite passes **54 tests**. New checks compare every inlined
branch with its original operation after UUID/root normalization, verify menu
structure and branch stops, and restrict record-file deletion to Register
exports. Client packaging rejects wrong account bindings, stale build menus and
extra old-operation files before writing.

Build-19 phone import/runtime, complete new intake/photo confirmation/resume,
cross-account matching, removal behaviour and physical B1 printing remain
rollout checks. Existing build-18 operation tiles are retained until bundle
checks pass. No records or photo metadata are reset by bundling.

**Installer-folder cleanup:** At Sagar's request, the private operator build-18
folder and shared client-build-11/client-build-18 folders were moved out of
iCloud to Mac Trash after an 18-file rollback archive was hash-verified under
ignored product-ops/local/backups/. The missing private operator build-19 folder
was restored from the signed local files and its account binding/action graphs
were rechecked. Only private operator build 19 and shared client-build-19 remain
as iCloud installer folders; both current manifests match their file bytes.
Installed operation tiles, personal shortcuts, records and Shared Albums were
unchanged. Older installers remain recoverable locally, without cluttering Files.

## Prior verified phone state — build 18

20 November 2026. Sagar confirmed that Register now successfully previews the
existing PBS-SAR-006 Shared Album photo. Read-only inspection confirms its
reference is now shared_album_confirmed, with the actual uploaded UUID name
and album date. The original selection's name and date both changed on upload.
The explicit Text conversion fixed the invalid Dictionary Value If seen on iPhone.

The full generator suite now passes **46 tests**, including complete folder
creation and rerun preservation of settings, SKU high-water marks, records and
photo metadata. The new intake/post/client-confirm/resume flow, cross-account
delivery, deletion behaviour and physical B1 printing remain rollout checks;
the successful Register test is not proof of those separate paths.

Cleanup removed Photo Lookup Check from the synced library (14 → 13 shortcuts,
with the eight operational and five personal shortcuts retained). The Mac UI
confirmed removal; phone propagation was not separately observed. Twenty
explicit temporary/superseded directories were moved to Trash after verifying
a private 125-file rollback archive. Current build-18 installers, account
references, the prior stable client-build-11 package and all live operations
records/Shared Albums were preserved. Diagnostic source builders and automated
tests remain reproducible; disposable signed exports and test images were cleaned.
The private development archive is not a backup of the live operations register.

The setup script now creates photo-links, photo-pending and shortcuts alongside
all record/archive folders. [Recovery](recovery.md) covers restoring data versus
recreating structure and rebinding both accounts after a new folder is created.


Tested on 3–5 November 2026 with shortcuts signed on a Mac on macOS 27.0.1 and synced through
iCloud. Records were checked by reading the files.

## Passed on iPhone

| Test | Result |
|---|---|
| New Product: submit with photos | Records and log saved correctly |
| Duplicate SKU in a different case | Rejected |
| Update Stock: unknown SKU | Rejected with the agreed message |
| Update Stock: new request, and the same status as on record | Request saved; the second asks first |
| Fix Product: correct prices while NEW | Row, submission and log updated |
| Fix Product: after work started | Refused, asks to message the operator |
| Fix Product: cancel, then resubmit the same SKU | Worked, with history kept |
| Work on Product: start, bad link, good link to READY_TO_PUBLISH | Worked |
| Work on Product: move back from READY_TO_PUBLISH | Worked, with old versions kept |
| Publish Products: one product | Published 1, Skipped 0, Need URLs 0 |
| Process Stock Requests: complete | LIVE and OUT_OF_STOCK together, as intended |
| Register: all three views, twice each | Opened in Numbers with the right data, no errors |
| Shopify link in Numbers | Opens when tapped |
| Leading zeros in Numbers | `="0012"` keeps them; plain and quoted don't |
| Share to the real Shared Album | Posted, with the caption shown as a comment |
| 500 dummy records | Listing about 5 s, reading about 1 min 50 s |

## Passed on iPhone: category menu and numbering

Tested on 4 November 2026.

| Test | Result |
|---|---|
| New Product suggests the next number | `002` after `001`, with `PBS-DUP-002` on the price screens |
| Each category counts separately | Saree suggested `001` while Dupatta was at `002` |
| Starting numbers | A fake file with `SAR: 408` suggested `409` |
| Changing the number to an existing one | `1` was read as `PBS-DUP-001` and rejected as a duplicate |
| Entering `0` | Rejected |
| Update Stock and Fix Product by category and number | Found `PBS-DUP-001` from `1`; `99` wasn't found |
| Cancelling the latest submission | Its number was suggested again |

## Passed on the client's iPhone

Tested on 5 November 2026 with the client's own Apple Account. Records were read on the Mac.

| Test | Result |
|---|---|
| Client's account reaching the shared folder | The client's `folderref` file reached the operator's folder |
| Folder reference | Different account IDs from the operator's, so the client does need a separate build |
| Installing from the shared folder, not AirDrop | All three shortcuts installed |
| New Product, Update Stock and Fix Product | Records and log entries reached the operator's folder, with the source shown as `client` |
| Operator picks up the client's product | Work on Product listed it on the operator's phone and moved it to `IN_PROGRESS` |

## Not tested yet

| Test | Why it matters |
|---|---|
| Process Stock Requests: Reject and Skip | Built, not run |
| Work on Product: mark LIVE directly, and Correct a product's prices | Built, not run |
| Publish Products: products with bad links, or a deselected product | Built, not run |
| Several stock requests or products in one batch | Only one at a time has run |
| Searching and filtering in Numbers | Expected to work, not checked |
| Tapping EDIT in Numbers | May create a copy. Worth checking before sharing. |
| Deleting an old Numbers copy | No copy has been created in testing, so that step hasn't had to act |

## Photo search

Tested on iPhone, by searching Photos for an exact SKU posted in the caption of a Shared
Album photo.

- **Result:** not found. The caption is stored as a comment on the photo.
- **Not tried:** partial SKUs, or searching again after a long wait.
- **Suitable for daily use:** no. The register is the dependable lookup, using the
  submitted date to find the photos.

Also tested on 5 November 2026 with an iCloud Shared Photo Library between the client's and the
operator's accounts: searching for the caption didn't work, so it was ruled out.

## Home Screen

Tested on 5 November 2026.

- **Operator's iPhone:** a Home Screen icon opens New Product's first menu straight away.
- **Client's iPhone:** New Product didn't open from the Shortcuts widget or a Home Screen icon, and its
  first menu was waiting when the Shortcuts app was opened separately. It works from inside the app.

The two builds differ only in their folder reference, so the difference is probably in the phone: its
iOS version, model or settings. That isn't confirmed. A one-action shortcut made on the client's
phone would show whether all shortcuts behave this way there.

## Numbers

Shortcuts offers actions for adding rows to Numbers, but third-party guides report none for
reading or updating them. That wasn't tested directly, because this design doesn't use them.
So Numbers is a view of the records, not where they live. No `.numbers` workbook ships with
this system; Numbers opens the CSV files that Register creates.

## NIIMBOT printing experiment

18 November 2026. A separate **New Product – Print Test** was generated, signed
with Apple's tool, imported into Shortcuts on the Mac, and verified in All
Shortcuts. It contains four app/share handoff routes using `PBS-TEST-PRINT` only.
The PNG preview was checked for readable, centred text. The 9 production builder
checks and 3 experiment checks passed (12 total); these are structural checks,
not printing tests.

**iPhone result:** v1 synced, option 4 opened Preview with the label image
instead of NIIMBOT, and option 1 also failed to open NIIMBOT. Inspection of the
Mac editor showed an empty app selection.
The builder used legacy identifiers plus `WFApp`. A v2 probe using static
`WFSelectedApp` descriptors was rebound on Mac import to `com.apple.MRT`;
inspection of an exported shortcut confirmed this. V3 now uses a Text action
with NIIMBOT's bundle ID as a runtime variable for both Open App and Open In,
plus a fifth route with Apple's native Ask Each Time picker. The signed v3 was
imported and its runtime target verified in the Mac editor. All 12 structural
checks pass. Do not run v1 or v2 for further tests. These results do not yet
demonstrate whether NIIMBOT can import an image.

**V3 iPhone result:** the operator confirmed that option 1 opens NIIMBOT. This
confirms iPhone sync and runtime app lookup; clipboard paste is not yet checked.
Option 4 also opened NIIMBOT, but the label image did not appear. This is a
successful app launch, not a successful image import or print.
Option 3 showed NIIMBOT under More in the Share sheet; selecting it opened
NIIMBOT but did not display/import the label image either.

The B1 is with the client in Bangalore; the operator has no printer. These tests
are on the operator's phone. Actual printing needs the client's phone and B1,
and cannot be confirmed from the operator's app launch tests.

**PDF experiment:** NIIMBOT's official B1 page advertises PDF import, so a
separate **New Product – PDF Print Test** was built, signed, imported and verified
in the Mac library. It offers direct Open In and Share sheet routes. A single
50 × 30 mm vector PDF with `PBS-TEST-PRINT` was rendered and visually checked;
page dimensions, text, wiring and record-free action scope are checked by tests.
The operator confirmed PDF option 1 opens NIIMBOT's Crop and split screen with
`PBS-TEST-PRINT` visible and can add the label. The screenshot confirms that
import stage; no printer was present. Share PDF and physical printing remain
untested.

**Build 10 integration:** New Product now offers Prepare SKU label after album
sharing. Print Product Label checks the existing submission before a reprint,
without any record writes. Both use native iPhone actions to generate the
actual SKU's PDF, rather than the static test payload. All 18 checks pass;
strict PDF parsing, stream lengths, xref offsets, page dimensions, exact SKU
text, growing numbers and invalid inputs are covered. Two rendered sample
labels were visually checked. The operator's original shortcut was exported
to `product-ops/local/printing-test/New Product.before-labels.shortcut` before
replacement, and the rebuilt folder reference matches the original. Updated
New Product and Periwinkle – Print Product Label were installed on the Mac.
Shortcuts retained the old editor as New Product 2; it was renamed
**New Product – Previous Version** to distinguish it from the updated intake.
The client build 11 package was later staged in shared iCloud Drive (see below);
installation on her phone is not yet confirmed.

**Experiment cleanup:** at the operator's request, the four installed test
shortcuts (New Product – Print Test, v2, v3, and New Product – PDF Print Test)
were deleted from the Mac's iCloud Shortcuts library. The deletion dialog
specified all iCloud devices; the Mac library was checked and none remain.
Phone propagation was not directly observed. Updated New Product, Print
Product Label and the named previous-version backup were retained. Source
builders and automated tests remain in the repo for reproducibility.

**Pending:** dynamic SKU PDF generation on iPhone, full intake/label flow,
client installation, native app picker, clipboard paste, text sharing, Share PDF,
NIIMBOT-provided iPhone actions, and actual B1 printing. PNG import has failed
to produce visible content through both tested handoffs on the operator's phone. No product
records were created or reset by the agent. See
[the experiment](new-product.md#niimbot-printing-experiment--18-november-2026).

## Build 11 — category selection and client release

18 November 2026. Work on Product → Move a product back and Correct a product's
prices now use category plus number. The obsolete full-SKU helper was removed.
All other manual product selectors already used category/number; list-based
selectors remain lists. Regression checks verify both changed branches and
the absence of the old full-SKU prompt. All 20 automated checks passed.

Eight operator-account workflows and four client-account workflows were built
and signed with Apple's tool. Every signed file was decoded to verify its
folder reference, the references differ between accounts, and no signed
workflow contains the old full-SKU prompt. Work on Product's signed menu says
build 11. The installed operator version was backed up as
`product-ops/local/printing-test/Work on Product.before-build-11.shortcut`,
replaced on the Mac, and inspected in the editor to confirm build 11. The old
410-action duplicate was removed after identifying the new version; one current
Work on Product remains in the library.

The four signed client files, README.txt and manifest.json were staged in
**Periwinkle Product Operations/shortcuts/client-build-11/**. All four copied
files were read back and their SHA-256 hashes matched. No operator copies or
folder-reference exports were placed in that package. Source and exact rebuild
commands are in [Building and signing](building-and-signing.md#build-all-workflows-from-scratch).

**Not yet confirmed:** iPhone sync for the operator update, build 11 category
selection on iPhone, installation of the client package, dynamic SKU PDF
generation on the client phone, and physical B1 printing/roll size. No register
records were created, reset or changed while preparing this release.

## Build 12 — Register browser

20 November 2026. Register adds Browse products (status/category filters), Find
a product (category/number), a detail screen, Copy SKU, Copy Shopify link and
Prepare SKU label. The original three tables remain under Export to Numbers.
The browser ignores non-SKU/conflict filenames and gives the furthest status
precedence when old copies remain. It never repairs records.

All 23 automated checks passed, including plist serialization, no record writes
or sharing from inspection, and no JSON loading while building the product
list. Only previously iPhone-tested action types are used. These checks do not
establish the new combined flow's behaviour on an iPhone.

**Pending phone checks:** first menu says build 12; All statuses/All categories;
each specific filter; empty matches; category/number lookup; product details;
SKU/link copying including a missing link; label handoff; all three CSV exports;
and stale-copy precedence. No product records were created, reset or changed.

The signed build 12 Register file was decoded to verify the operator's folder
binding and first menu. Its 188-action build 11 signed predecessor is preserved
at `product-ops/local/printing-test/Register.before-build-12.shortcut`. The
native export/import panels had disabled confirmation buttons and later Mac
computer-use connections timed out repeatedly. **Register build 12 is prepared
but not installed**; the existing synced Register remains unchanged. The local
installation file is `product-ops/local/releases/build-12/install/Register.shortcut`.

### Shared Album check

Following Sagar's request, a separate read-only **Periwinkle – Photo Lookup
Check** was generated, signed and decoded. An identical copy plus README.txt
was staged in **Periwinkle Product Operations/shortcuts/photo-lookup-check/**;
source/copy SHA-256 hashes matched. This check contains no account folder
reference, file writes, image export, clipboard or Share action. It is not one
of the client's operational shortcuts and is not installed in the Mac library.

All 25 checks now pass, including two checks restricting the photo investigation
to read/display actions and requiring an Album filter in both search modes.
Find Photos, image metadata and Quick Look in this combination still require
phone testing. Automatic SKU-to-photo linking and previews in Register/Work on
Product are **not implemented** pending that result, cross-account matching and
removal behaviour. No persistent preview cache or duplicate image store was
created. The Shared Album remains the intended photo source of truth.

**Operator iPhone result, 20 November 2026:** Sagar ran Browse Shared Album
against **Miniatures Available**. The screenshot reports 413 photos, matching
the album's actual item count confirmed by Sagar. Album retrieval passed this
check. The accompanying Photos info screen shows `IMG_0338` and JPEG format;
that does not establish whether Shortcuts' Name property includes an extension.
Use the exact Name value in the diagnostic's Photo metadata alert for the next
lookup, without inventing or appending an extension. The original installed
diagnostic prompt's “including extension” wording was too restrictive; source
instructions now say “exactly as shown.” Filename retrieval, cross-account
matching, album-removal behaviour and production integration remain pending.

### Shared Album name lookup and corrected preview passed

20 November 2026. Sagar confirmed that entering the exact photo name **without
an extension** returned one result inside Miniatures Available. The first
preview attempt failed with “an action could not be found”: the generator used
`is.workflow.actions.quicklook`, which is invalid. Version 2 replaces it with
`is.workflow.actions.previewdocument`; its signed actions were decoded and the
correct final identifier verified. An identical signed file and README were
staged in `shortcuts/photo-lookup-check-v2/` in shared Drive. Sagar then confirmed
that the correct image opened. Album lookup, exact-name lookup, image metadata
and the corrected preview action are now in the phone-tested action set.

## Build 13 — metadata-only product photo links

Register and Work on Product now use `photo_links.py`. A confirmed link saves
only album name, exact Photos Name and Date Taken, in a separate
`photo-links/<sku>.json` file. Viewing rechecks Album AND Name, then compares the
saved photo date; missing matches show unavailable and multiple matches offer
a chooser. No image copy or persistent preview collection is saved. Register
previews linked photos before product details, and Work on Product does so
before Start changes status. Its View or link product photo branch only views
or changes the separate photo metadata.

All 29 automated checks passed. Checks cover serializable workflows, block/
output ordering, only phone-tested action types, no product/stock/activity
writes from Register inspection, metadata-only link saving, and required Album
membership in every photo query. Signed build 13 Register (785 actions) and
Work on Product (662 actions) were decoded: their normalized action graphs
match current source and both retain the correct operator folder binding.
The signed build 11 predecessors are backed up in
`product-ops/local/releases/build-13/backups/`.

Mac installation again timed out. An attempt to stage account-bound operator
files in the client-shared folder was rejected by automatic approval review
because of the embedded operator folder reference; that command did not run.
A safe alternative succeeded: a **new private folder at the operator's iCloud
Drive root**, named **Periwinkle Operator Install - Build 13 - 2026-11-20**,
holds Register.shortcut, Work on Product.shortcut, README.txt and manifest.json.
Both copied files' SHA-256 hashes matched. No operator files were added to the
client-shared folder, and no product, stock or image records were changed.

**Still pending:** operator installation and the complete link/save/view flow
on iPhone, first-use handling when photo-links does not exist, ambiguous/missing
matches, photo removal using only an explicitly disposable image, Register
filters/exports, and automatic preview before Start. Cross-account auto-linking
in New Product is not implemented; the four client shortcuts remain unchanged.

## Build 14 — first-use photo linking

20 November 2026. On the operator's iPhone, Register build 13 stopped with
**Photo Album Not Found**, displaying an empty album name before offering Link
or change photo. Read-only inspection confirmed that photo-links did not yet
exist in the shared folder. The previous missing-path/blank placeholder check
was insufficient; this is a first-use failure, not an incorrectly typed album.

Build 14 enumerates the actual root folder and actual link files. Only an exact
SKU filename match sets photoLinkFound to yes. No matching file means no JSON
parse and no Photos call. Incomplete album/name/date metadata also skips Photos
and allows the user to replace the link from the product actions.

All 33 checks passed. A control-flow harness executes the generated preview
against fake folders and deliberately treats blank Text as an item/value.
Regression cases cover no metadata folder, a missing link with stale variable
contents, each missing metadata field, and a valid exact SKU filename with or
without .json. The cases verify that missing/incomplete links never call Photos.
Existing safety, serialization, PDF and action/block checks also pass.

**Pending phone check:** replace both operator shortcuts with build 14; Register
→ Find a product → category/number → details → Link or change photo should now
be reachable on first use. Confirm one link, rerun that SKU and check its photo.
The previously confirmed album/name/preview primitives still pass, but the
complete corrected link/save/view flow and removal behaviour need confirmation.
No shared product, stock, activity or image records were changed by this fix.

The build 14 signed Register (819 actions) and Work on Product (696 actions)
were decoded and normalized against current generator output; both action
graphs and operator folder bindings matched. Filename aliases, README.txt and
manifest.json were prepared locally, then copied to the newly created private
operator iCloud folder **Periwinkle Operator Install - Build 14 - 2026-11-20**.
Both copied shortcut hashes matched the manifest. Operator files remain outside
the client-shared folder. Installation and the corrected full flow still need
the operator's phone confirmation.

## Build 15 — saved-link discovery and automatic intake references

20 November 2026. The operator confirmed linking PBS-SAR-001, but Register
showed no preview. Read-only inspection found a valid photo-links/pbs-sar-001.json
pointing to Miniatures Available / IMG_0340 with a photo date. The metadata was
saved correctly; no relinking was required.

The lookup used nested loops with a plain Repeat Item reference. Apple's
Shortcuts guide documents distinct names for nested repeat items. After the
regression harness was corrected to model those names, the existing valid-link
case failed with zero photo queries. Separating folder discovery and file
enumeration reproduced a red-to-green fix. The source still uses a positive
found flag and complete-field checks, preserving build 14's first-use fix.

Sagar then required linking during client intake rather than operator searching.
New Product now captures the first selected photo's exact Name/Date Taken and
the category's configured Shared Album, and saves metadata before the Share
sheet. It performs no second photo chooser. The seven new proposed album names
use Periwinkle - followed by the category name, documented in New Product and
both package READMEs. The client must create/join the Shared Albums and invite
the operator. Existing links retain their original album names.

All 35 checks passed. Intake tests execute capture/save for all seven categories,
verify the first selected photo is used, parse the saved JSON metadata, and
verify that New Product saves the reference before Share without asking for a
second photo selection. The saved-link regression and all previous generator,
PDF, serialization and record-safety checks also pass.

Three operator-account signed files were decoded and matched current source:
Register (833 actions), Work on Product (710) and New Product (190). All four
client-account files were likewise decoded and verified, including New Product
(190). The operator/client folder bindings differ and match the corresponding
saved references. Both copied packages' file hashes were verified.

**Delivered:** private iCloud root folder **Periwinkle Operator Install - Build
15 - 2026-11-20**, containing three filename aliases for the operator's phone,
README.txt and manifest.json; existing shared operations folder at
**shortcuts/client-build-15/**, containing only the four client-account files,
README.txt and manifest.json. Client New Product changes; the other client files
are included for recovery. No operator files went into the shared package.
Signed predecessors remain locally backed up under build-15/backups.

**Pending phone checks:** the existing PBS-SAR-001 link previews without relinking;
one own-account dummy intake posts to the assigned Shared Album and previews in
Register without manual linking; and one client-to-operator dummy intake verifies
name/date preservation across Shared Album upload and separate Apple Accounts.
Sagar can run the own-account test with the operator New Product file; he must
not install the client's account-bound file on his phone. Removal behaviour
also remains unverified. No product, stock, image or photo-link data was created,
reset or edited by the agent while preparing the release.

## Build 16 — fractional-second tolerance and mismatch diagnostics

20 November 2026. Sagar created PBS-SAR-006 and posted its photo to Periwinkle -
Sarees; Register reported Photo unavailable. Read-only inspection confirmed an
automatic client_intake reference to IMG_0499 with original Date Taken ending
in 21:32:28.548+05:30. The product/submission and photo-link record exist. The
exact date/filename metadata of its album copy has not yet been confirmed.

A regression fixture with that original timestamp and an album copy reporting
21:32:28.000+05:30 reproduced the exclusion: zero previews. Build 16 strips only
fractional seconds from both comparison keys, leaving the original saved
metadata untouched. Exact whole-second, filename and album matching remain.
The same fixture now previews. A different second or different album remains
excluded. This establishes a code defect and its correction, not proof that
fraction loss is the cause on the user's device.

The control-flow harness now returns nonempty mock photo query results and
executes candidate-date filtering and preview actions. All 37 checks pass.
No filename matches yields Photo unavailable with the searched name; filename
matches with a different date yields Photo date differs and shows recorded and
candidate dates. This avoids attributing every rejection to removal or sync.

**Pending:** lookup/preview of IMG_0499 using the existing phone diagnostic,
then full Register preview of the existing PBS-SAR-006 with build 16. No new
product, manual relink, image copy or metadata edit is needed for this test.
Cross-account intake and deletion behaviour remain pending. New Product and
client build-15 actions are unchanged; only two operator files need updating.

## Build 17 — capture the posted asset after upload renaming

20 November 2026. The operator's diagnostic found one photo in Periwinkle -
Sarees. The album Name was 7C8E0E8D-1633-49BF-8BC5-AC26EB68C6EB rather than
intake's IMG_0499. Exact-name lookup initially failed with a pasted line break,
then found and previewed the correct image when entered on one line. This
confirms a changed upload name, independently of any fractional-date issue.
Build 16 was superseded without phone delivery.

New Product build 17 snapshots existing album names before Share and persists
only a pending metadata record. After posting, it finds newly added album names
and shows the image for client confirmation (a chooser when several are new).
Only then does it save the actual album asset name/date as shared_album_confirmed.
Fix Product can resume this confirmation after sync, including when work has
started; that branch changes photo metadata only. Operator preview does not
confirm unreviewed album additions. Pending snapshots are replaced with small
completion markers, without deleting files or storing any image copies.

All 43 tests pass. The harness executes a complete upload-renaming case with
both name and date changed, confirms the album asset, saves canonical metadata,
then views that newly saved reference. Other cases cover empty-before albums,
pending sync, multiple new additions, missing/invalid/completed snapshots,
verified-name recovery, date precision, and album/date mismatch exclusion.
Existing PDF, native action allowlist, serialization and record-safety checks
also pass. The generator uses previously phone-tested action identifiers.
The complete new phone interaction remains unverified.

All eight signed workflows were decoded and normalized against current source:
operator Register 991 actions, Work on Product 868, New Product 390 and Fix
Product 340; client New Product 390, Update Stock 108, Fix Product 340 and Print
Product Label 54. Both account bindings match their own saved references and
are distinct. Copied file hashes were verified. Four operator filename aliases
are in the new private iCloud root folder **Periwinkle Operator Install - Build
17 - 2026-11-20**; four client-account files are in the existing shared folder
**shortcuts/client-build-17/**. No operator artifacts were put in the shared
client package.

The agent backed up only PBS-SAR-006's photo-link JSON locally under ignored
build-17/metadata-backups, then changed its photoName to the exact user-verified
album name and marked source verified_shared_name. Build 17 will retrieve that
unique album asset's actual date and convert it to shared_album_confirmed on
view. No product row, price, stock, activity record or image file was changed;
no product was resubmitted. Other photo references were left untouched.

**Pending:** view existing PBS-SAR-006 with build 17 without relinking; create
one new dummy product, post and confirm its actual album photo, then view it in
Register; finish a delayed post through Fix Product; client-to-operator
confirmation and deletion behaviour. Clients should finish photo confirmation
before creating another product in the same album.

## Build 18 — explicit text typing for dictionary-based If actions

20 November 2026. The operator supplied an editor screenshot showing
photoLinkFound is yes, dictionary reads for source/sku/albumName, then an If on
Dictionary Value with an empty comparison and the error “Please choose a value
for each parameter in this action.” This identifies an imported condition/type
problem before actual photo lookup, independently of album membership or sync.

Build 18 materializes string dictionary fields through Text actions before
comparisons and predicates. source, state and beforeNames are now explicitly
text, as are photo identity fields. All 44 automated checks pass, including a
new regression check prohibiting a text comparison directly on an untyped
Get Dictionary Value output. Prior simulations treated dictionary values as
Python strings and did not model iOS import/type inference; their passing
results did not validate this device behaviour.

**Pending:** replace Register only from the private build-18 package, verify the
first menu says build 18, and view the existing Saree 6 reference. The other
changed workflows use the same fix. No product or photo metadata was changed
for this rebuild; the existing user-verified shared name remains available for
one-time date capture. Full intake/post/confirm/preview and cross-account tests
remain pending.

All eight build-18 signed workflows were decoded, their normalized actions
matched current source, and account bindings matched the respective saved
references (which differ between roles). Operator action counts: Register
1007, Work on Product 884, New Product 396 and Fix Product 346. Client counts:
New Product 396, Update Stock 108, Fix Product 346 and Print Product Label 54.
The private iCloud root package **Periwinkle Operator Install - Build 18 -
2026-11-20** contains four install aliases, README and manifest. Client-only
files are staged at shared **shortcuts/client-build-18/**. All copied hashes
matched. No product or photo metadata was changed for this delivery. The
operator is asked to replace Register alone first and test existing Saree 6,
before updating the other installed workflows.
