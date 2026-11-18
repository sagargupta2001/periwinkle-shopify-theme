# Test report

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
commands are in [Building and signing](building-and-signing.md#rebuild-and-share-a-release).

**Not yet confirmed:** iPhone sync for the operator update, build 11 category
selection on iPhone, installation of the client package, dynamic SKU PDF
generation on the client phone, and physical B1 printing/roll size. No register
records were created, reset or changed while preparing this release.
