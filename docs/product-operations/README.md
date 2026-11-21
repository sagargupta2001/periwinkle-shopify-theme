# Product operations

How a new piece gets from the client to a live Shopify product, and how stock
changes reach Shopify, using only Apple Shortcuts on two iPhones, a shared
iCloud folder and Numbers. There is no server, database or paid app.

These shortcuts keep the record of what's been submitted, what's being worked on,
and what's live or out of stock. They never change Shopify. Shopify is updated by the
operator, by hand or with the `/add-products` skill in Claude Code, which reads this
register but never writes to it
([decision 24](../decisions.md#24-add-products-lists-what-the-register-holds-and-never-tracks-status)).

## The shortcuts

Build 19 installs **Periwinkle - Client** and **Periwinkle - Operator**.
Each starts with four operation choices below. Only Client is shared with the
client; the operator can install both for testing. One operation runs per launch.
The generator keeps operations modular and inlines them into the two files,
so neither file depends on other installed shortcuts.
[Role shortcuts](role-shortcuts.md) covers installation, updates and migration.
Each operation still has its own page and diagram.

| First-menu operation | Role | What it's for |
|---|---|---|
| [New Product](new-product.md) | Client | Submit a new piece with its photos |
| [Print Product Label](new-product.md#print-again-without-resubmitting) | Client | Prepare or reprint a submitted piece's SKU label in NIIMBOT |
| [Update Stock](update-stock.md) | Client | Report that a piece is out of stock or back in stock |
| [Fix Product](fix-product.md) | Client | Correct a price or cancel a wrong SKU, until work starts |
| [Work on Product](work-on-product.md) | Operator | Start a product, record its link, move it back, correct prices |
| [Publish Products](publish-products.md) | Operator | Mark a batch of ready products as LIVE |
| [Process Stock Requests](process-stock-requests.md) | Operator | Complete or reject the client's stock requests |
| [Register](register.md) | Operator | Browse/find products and optionally export tables to Numbers |

Also here:
- [Rebuild and share a release](building-and-signing.md#build-all-workflows-from-scratch):
  reproduce both role bundles and stage the client's single account-bound file in iCloud.
- [Installation](installation.md): setting up a phone, and sharing with the client.
- [Recovery](recovery.md): recreate the entire folder structure, restore metadata,
  preserve SKU numbering and rebuild account references after deletion.
- [Building and signing](building-and-signing.md): recreating or changing the
  shortcuts, and the iPhone behaviours they're written around.
- [Listing checklist](listing-checklist.md): what a Shopify listing needs.
- [Test report](test-report.md): what has been tested, and what hasn't.
- [Improvements](improvements.md): fixes and ideas to pick up later, on hold until the
  client's phone has been tested.

## How a product moves

```mermaid
flowchart LR
    C["Client:<br/>New Product"] --> NEW
    NEW -->|"Work on Product:<br/>Start a new product"| IP[IN_PROGRESS]
    IP -->|"Lists it in Shopify,<br/>then adds the link"| RTP[READY_TO_PUBLISH]
    RTP -->|"Publish Products"| LIVE
    IP -->|"Link added, already<br/>checked it's live"| LIVE
    NEW -->|"Fix Product:<br/>wrong SKU"| X[Cancelled]
    LIVE -.->|"Work on Product:<br/>Move a product back"| IP
    RTP -.-> IP
    IP -.-> NEW
```

Publication status and stock status are separate. A product can be `LIVE` and
`OUT_OF_STOCK` at once, and changing one never changes the other. A link alone
never makes a product `LIVE`: the operator has to confirm it.

## How a stock change moves

```mermaid
flowchart LR
    C["Client:<br/>Update Stock"] --> P[PENDING]
    P -->|"Operator updates Shopify,<br/>then completes it"| D[COMPLETED]
    P -->|"Operator rejects it"| R[REJECTED]
    D --> S["Product's stock status<br/>and update time change"]
```

The client reports a status only, never a quantity. Every variant tracks its
quantity and stops selling at zero
([decision 16](../decisions.md#16-every-variant-tracks-stock-and-stops-selling-at-zero)),
so bringing a piece back in stock means entering a number in Shopify. Most
pieces are one of a kind, so that's usually 1.

## Daily routine

**Client** — open Periwinkle - Client, then choose the operation.
1. New piece: run New Product, pick the category, and tap through the suggested number.
   Then paste the caption and post to the album. Choose **Prepare SKU label** to
   open its PDF in NIIMBOT, tap **Add**, and print the label for the piece straight
   away ([decision 25](../decisions.md#25-the-client-prints-the-sku-label-right-after-submitting)).
   For a retry, use **Print Product Label**, without submitting the product again.
2. Sold or back: run Update Stock.
3. Typed something wrong: run Fix Product straight away. If work has started,
   message the operator.

**Operator** — open Periwinkle - Operator, then choose the operation.
1. Run Register → Browse products → New to see what's waiting.
2. Run Work on Product → Start a new product. The details are copied, ready
   for Claude.
3. New Product (included in build 19) confirms the actual posted album photo during intake. For an older
   record only, link it in Register or Work on Product once. Later visits preview
   directly from the Shared Album. Run
   `/add-products list <SKU>` in Claude Code with a photo. It creates the draft and
   gives you the store link. Then add the photos in Shopify.
4. Run Work on Product → Add or fix a Shopify link.
5. Run `/add-products live <SKU>`, which checks the [listing checklist](listing-checklist.md)
   and publishes it. Then run Publish Products.
6. Run Process Stock Requests.

## Where the data lives

Everything is in one iCloud Drive folder, **Periwinkle Product Operations**,
created by hand at the top level of iCloud Drive. It can't go inside the
`Shortcuts` folder: that one belongs to the app and reportedly can't be shared.

```text
Periwinkle Product Operations/
  settings.json                     Valid statuses, currency, time zone
  sku-start.json                    Each category's starting number
  products/<sku>.json               What was submitted. Used to spot duplicates
  products/_cancelled/<time>/       Cancelled submissions
  register/<STATUS>/<sku>.json      A product's current row, in one status folder
  register/_replaced/<time>/        Every earlier version of a row
  register/_cancelled/<time>/       Rows of cancelled submissions
  stock-requests/PENDING/<id>.json  Waiting for the operator
  stock-requests/COMPLETED/<id>.json
  stock-requests/REJECTED/<id>.json
  stock-requests/_handled/<time>/   The original of each processed request
  log/<time>-<sku>-<event>.json     One file per event, never changed
  views/*.csv                       Tables for Numbers, rebuilt on demand
  photo-links/<sku>.json            Album/name/date reference only, no image bytes
  photo-pending/<sku>.json          Pending album-name snapshot, then completion marker
```

File names use the SKU in lowercase, which makes duplicate checks
case-insensitive and exact. The SKU as typed is kept inside the file, so
hyphens and leading zeros survive. Every folder holds a `_keep.txt`: please
leave those in place. [Installation](installation.md#initial-files) lists what the
folder needs before first use.

**Why one small file per event:** two phones editing one file can produce sync
conflicts and lost records. New files can't overwrite each other. The product records
that get overwritten are a product's row and, when the client corrects prices, its
submission. Photo links and pending snapshots are also updated during client
confirmation or recovery. Only one person edits those at a time: the client while it's `NEW`, the
operator after that.

**Storage:** records are a few hundred bytes each, so thousands take a few MB.
Photos stay in the Shared Album and never enter this folder.

### Record fields

| Table | Fields |
|---|---|
| Product row | `sku`, `costPrice`, `sellingPrice`, `productStatus`, `stockStatus`, `shopifyUrl`, `submittedAt`, `publishedAt`, `lastStockUpdateAt`, `operatorNotes` |
| Stock request | `requestId`, `sku`, `requestedStockStatus`, `requestStatus`, `requestedAt`, `processedAt`, `operatorNotes` |
| Activity log | `timestamp`, `sku`, `eventType`, `previousValue`, `newValue`, `source`, `notes` |
| Photo link | `version`, `sku`, `albumName`, `photoName`, `photoTakenAt`; intake also sets `source` |

Log event types: `PRODUCT_SUBMITTED`, `PRICE_CORRECTED`,
`SUBMISSION_CANCELLED`, `PROCESSING_STARTED`, `SHOPIFY_URL_RECORDED`,
`PRODUCT_PUBLISHED`, `STATUS_MOVED_BACK`, `STOCK_REQUESTED`,
`STOCK_REQUEST_COMPLETED`, `STOCK_REQUEST_REJECTED`.

## SKUs

- The format and codes are in [sku-codes.md](../sku-codes.md): `PBS-<CODE>-<NNN>`.
- The client picks a category and a number, and the shortcut builds the SKU. New
  Product [suggests the next number](new-product.md#how-the-number-is-chosen). This
  replaces the client's notebook.
- **Before using a category that has older products,** set its starting number. See
  [Installation](installation.md#initial-files). Otherwise the register starts at `001`,
  which may match an SKU already in Shopify.
- Operator manual lookup also uses category plus number. Retired SKU formats
  are not offered during this catalogue rebuild.
- Duplicates are only checked against this register, not against SKUs already
  in Shopify. If an old product is still active with the same SKU, Shopify
  won't warn you here.

## Known limits

- **Numbers is a snapshot.** Each table is rebuilt when Register runs. Typing
  into it changes nothing and is lost on the next refresh. Shortcuts can only
  add rows to Numbers, not read or update them, so a live workbook can't do
  duplicate checks or status changes.
- **SKU-comment search is not used.** Build 13 can preview a manually linked
  photo from its Shared Album by name/date. New Product (included in build 19) confirms the
  posted reference during intake; cross-account matching still needs testing. For an unlinked photo, use the register's
  submitted date to find photos. See [Next phase](#next-phase).
- **Posting isn't confirmed.** The record is saved before the Share sheet opens,
  because Shortcuts can't tell whether the client posted. If the client cancels,
  the product stays `NEW` with no photos in the album.
- **Captions don't update.** Shortcuts can't edit an album comment, so the
  register is the source of truth for prices and links.
- **Sync isn't instant.** A record reaches the other phone once iCloud syncs,
  usually in seconds. Offline, a duplicate check only sees what's on that phone.
- **Time zone.** Times use the phone's own zone. They're right for Asia/Kolkata
  while both phones are set to India, and the offset is stored with each time.
- **Speed.** Reading records takes about 0.2 seconds each, so Register took
  about 2 minutes for 500. Lookups also list each folder they check, about 5
  seconds per 500 files, so Update Stock will slow down as the catalogue grows.
- **No automatic rollback.** Shortcuts can't catch errors, so a stopped run can't
  undo itself. Flows save the new record and log first, and move the old file
  last, so a failure leaves at worst a spare copy. Fix a wrong status with
  [Move a product back](work-on-product.md).

## Next phase

- **Photo lookup by SKU:** a Shared Library was tested and ruled out
  ([decision 26](../decisions.md#26-stay-with-the-shared-album-not-a-shared-library)), so the
  album stays. See [Finding photos](improvements.md#finding-photos) for what else could help.
- **Existing products:** they aren't in the register, so Update Stock doesn't
  know them. The idea of archiving them and recreating them through this system
  is still undecided.
