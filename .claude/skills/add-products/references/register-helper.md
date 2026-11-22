# Register helper

Use from the repository root. Default root is the shared iCloud operations folder;
--root may select an isolated fixture or a restored operations folder. It does not
create the operations root and never calls Shopify. No real processing occurs
while updating or testing the skill itself.

```bash
python3 .claude/skills/add-products/register_ops.py queue
python3 .claude/skills/add-products/register_ops.py snapshot --sku PBS-SAR-001
python3 .claude/skills/add-products/register_ops.py start --sku PBS-SAR-001 --expected-sha256 HASH
python3 .claude/skills/add-products/register_ops.py checkpoint --sku PBS-SAR-001 --expected-sha256 HASH --patch PATCH_FILE
python3 .claude/skills/add-products/register_ops.py ready --sku PBS-SAR-001 --expected-sha256 HASH --url https://periwinklebysherry.com/products/example
python3 .claude/skills/add-products/register_ops.py publish --sku PBS-SAR-001 --expected-sha256 HASH --receipt RECEIPT_FILE
python3 .claude/skills/add-products/register_ops.py recover --transaction-id UUID --receipt RECEIPT_FILE
```

Replace HASH with the latest snapshot's sha256, never a submission hash or a value
from a previous row version. Use a new snapshot after each successful transition.
start/ready/publish preserve all fields except productStatus, shopifyUrl and
publishedAt. They copy the old row to register/_replaced/agent-UUID/, write the
usual operator activity event and remove the superseded current-status copy.
Repeating a completed matching transition is a no-op, not another event or reset
of publishedAt. They never change product submissions, price/cost or stock fields.
Checkpoint both the product ID and its current handle before ready; the URL must
match that handle. A later verified handle correction can update a READY row,
also preserving its old version and logging the URL change.

## Metadata checkpoints

PATCH_FILE is a JSON object, not shell code. Supported keys are stage, productId,
variantId, inventoryItemId, handle, imageFileIds, imageHashes,
inventoryIdempotencyKey, inventoryInitialized and lastError. Store only metadata,
never image bytes. Shopify IDs and SHA-256 values must have their proper formats.
Product identity cannot change after a checkpoint has established it.

Stages: awaiting_photo, photo_received, images_prepared, draft_created,
inventory_initialized, media_attached, ready, published, blocked. Persist the
returned IDs after each write, and the inventory UUID before its first use.
The job's SKU/submittedAt identity is managed by the helper; the caller cannot
patch register fields through the checkpoint command.

Jobs live in agent/jobs/<sku>.json. A fresh queue resumes only a job matching the
current row's submission identity; unrelated operator-owned IN_PROGRESS rows are
not automatically adopted. Missing source files on resume mean requesting only
the unfinished SKU's photo again. Verified existing Shopify media can be reused.
A completed published job moved back by an operator is reported for explicit
rework; it is not automatically republished by a later default batch.

## Publication receipt

Save this JSON from the actual final Shopify read/checks, with real values:

```json
{
  "sku": "PBS-SAR-001",
  "productId": "gid://shopify/Product/123",
  "url": "https://periwinklebysherry.com/products/example",
  "checkedAt": "2026-11-22T12:00:00+05:30",
  "status": "ACTIVE",
  "onlineStorePublished": true,
  "price": "250.00",
  "cost": "100.00",
  "mediaCount": 2,
  "singleDefaultVariant": true,
  "tracked": true,
  "inventoryPolicy": "DENY",
  "taxable": false,
  "requiresShipping": true,
  "vendor": "Periwinkle By Sherry",
  "categorySet": true,
  "collectionsVerified": true,
  "contentVerified": true
}
```

The example is documentation, not a ready-to-use verification. Use a timezone-aware
checkedAt from the current check (valid for ten minutes), exact row SKU/prices,
the checkpointed product ID and the recorded canonical URL. Derived booleans
represent actual field/membership/content checks; never fill them just to pass.
This receipt is an agent assertion backed by tool results, not a cryptographic
proof or an independent Shopify query by the helper.

## Interrupted writes

The transaction intent in agent/transactions/ is persisted before row mutation.
For a pending intent, use recover with its exact ID instead of manually deleting
duplicate rows. Known matching destination/log/archive files are reused once.
Unexpected current-row differences stop recovery without overwriting them.
Publication recovery requires a fresh Shopify receipt; never reuse an old checkedAt
after a restart. A complete intent is a no-op when recovered again.

The advisory lock only coordinates local helper processes. It does not turn
iCloud Drive into a distributed database or stop another phone's edit. Row hashes,
matching transaction contents and single-SKU ownership are the concurrency guards.
If an unexplained conflict remains, block that SKU and preserve files for review.
