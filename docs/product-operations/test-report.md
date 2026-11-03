# Test report

Tested on 3–4 November 2026 on the operator's iPhone, with shortcuts signed on a Mac on
macOS 27.0.1 and synced through iCloud. Records were checked by reading the files.

**Nothing has been tested on the client's iPhone or Apple Account yet.**

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

## Not tested yet

| Test | Why it matters |
|---|---|
| Client's Apple Account reaching the shared folder | The main risk. See [Installation](installation.md#3-handing-over-to-the-client). |
| Importing on the client's iPhone | Signed files have only been imported on the Mac so far |
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

## Numbers

Shortcuts offers actions for adding rows to Numbers, but third-party guides report none for
reading or updating them. That wasn't tested directly, because this design doesn't use them.
So Numbers is a view of the records, not where they live. No `.numbers` workbook ships with
this system; Numbers opens the CSV files that Register creates.
