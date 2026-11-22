---
name: add-products
description: Process client-submitted Periwinkle products one by one from the shared register, using one pasted photo per SKU, preparing images, publishing Shopify listings and logging register updates. Use for add-products or requests to process new register products. Status requests remain read-only.
---

# Create Periwinkle products

Turn the client's NEW submissions into verified live Online Store listings. Sagar's
normal task is to invoke this skill in a fresh session, paste the requested SKU's
photo from his existing iPhone preview shortcut, and review the finished products.
Do the listing, image preparation, upload, publication and logged register updates.
Ask for **one SKU's photo at a time**, finish that product, then request the next.

Run from the Periwinkle repository with access to its iCloud operations folder.
A phone photo pasted into chat is sufficient image input; Mac Photos and a photo
export shortcut are not required. An iPhone-only chat without register file
access cannot run this whole workflow: explain that access gap rather than claim
that the Shopify connector can read iCloud. This skill does not start itself when
the client adds a row; the user's invocation starts a batch.

## Invocation and scope

- `$add-products`, `/add-products`, `process`, or “process the new products”:
  process the queue through publication. This is the requested publishing scope;
  do not add a draft-approval or manual-link step. Honor actual tool approvals.
- `status`, “what's waiting”, or a skill-maintenance request: read/report only.
- `process SKU`: process that eligible NEW or agent-owned unfinished SKU only.
- `list SKU`: prepare a draft and its images, record READY_TO_PUBLISH, then stop.
- `live SKU`: validate and publish an agent-owned prepared listing, then record LIVE.
- A pasted image during an active batch answers its current photo request. It is
  not an instruction to replace another SKU's image or publish unrelated products.

Only handle product submissions. Do not reset the register, process stock
requests, change store/theme settings, add tracking tags, or resurrect archived
products. Default batches leave existing LIVE products alone. An explicit request
to correct a named live product authorizes that correction only; preserve its
identity, price, stock, publication time and existing media unless asked otherwise.
Do not mark any product as a gift, add gift tags or place it in gift collections.
This applies to every category and price; gifting is deferred to a separate future
automation, not an intake decision or an additional question for the user.

For status-only requests, run read_register.py and compare exact SKUs with
Shopify without entering the processing flow. Report current statuses, pending
stock requests and mismatches in prices/costs, product links or publication.
Do not claim rows, request processing photos, or repair anything in this mode.

## Preflight and queue

1. Read [listing rules](references/shopify-listing.md) and the repository's
   [listing checklist](../../../docs/product-operations/listing-checklist.md).
   The process is described in [agent processing](../../../docs/product-operations/agent-processing.md).
   Read the [fast path](references/shopify-fast-path.md) for verified operation
   shapes and batch-level lookups. Reuse them instead of rediscovering the schema
   for every SKU; refresh only changed, unfamiliar or rejected fields.
2. Check that the intended store is Periwinkle By Sherry / periwinklebysherry.com,
   the Shopify read/write/upload tools are connected, image editing is available,
   and the register can be read. Report a missing capability accurately. Do not
   create products with missing images or pretend an unavailable tool succeeded.
3. Inspect the queue:

```bash
python3 .claude/skills/add-products/register_ops.py queue
```

It includes NEW rows and unfinished rows this helper previously claimed, ordered
by submission time. It excludes unrelated operator-owned work and LIVE rows.
`read_register.py` remains a read-only full-register/status report.
4. Report the real queue count and a compact SKU list. Freeze the candidate SKU
   list for this invocation; refresh each row before work and never revisit a
   skipped/blocked SKU in the same batch. Later client submissions can wait for
   the next invocation. Never claim all NEW rows in advance.
5. Resolve only helper-owned pending transactions using the recovery procedure
   below. Unexplained duplicate/conflict rows block the affected SKU. Flag
   pending stock requests; do not publish a SKU with an unresolved out-of-stock
   request. Continue other independent products where possible.

## One product at a time

**Read and claim.** Obtain a fresh snapshot (`snapshot --sku SKU`). Current row
prices include corrections; the original submission's prices are not authoritative.
Selling price must be positive and above cost, and stock must be IN_STOCK. Claim
only the current NEW SKU with `start --sku SKU --expected-sha256 HASH`. This logs
PROCESSING_STARTED and moves it to IN_PROGRESS. A resumed agent-owned row needs
no duplicate start. Do not adopt unrelated IN_PROGRESS work automatically.

**Ask for its photo.** Use ordinary chat so the user can attach an image, not a
text-only question widget. For example:

> First: **PBS-SAR-001**. Please paste its photo from your Register / Work on
> Product preview. I'll prepare and publish this product before asking for the next.

Wait for the photo. Do not ask for all nine images at once, guess which SKU an
ambiguous attachment belongs to, search album comments, or require a new photo
shortcut. An explicit SKU caption overrides the assumed queue association: if it
names a different product, clarify before using it. If the user skips this SKU,
checkpoint `stage: blocked` with a short reason and advance to the next candidate.

**Inspect and prepare images.** Inspect the actual attached file first. Identify
only visible features and client-provided facts. Do not invent fabric, dimensions,
origin, a reverse side or packaging. Omit optional unknowns; ask only when a
required fact or usable photo is missing. Read the matching category prompt in
[product imagery](references/product-imagery.md). For apparel, make a premium
4:5 editorial hero with an adult Indian model showcasing the actual product;
for jewellery use the appropriate model detail, and for objects use the styled
product hero. A fabric close-up or detail crop is a supporting image, not the
storefront hero. Also prepare a genuine supporting view/detail from the source.
The merchant authorizes editorial model/drape styling, not an invented textile:
lock the actual colour, motifs, border, texture, garment details and included
pieces. Do not transfer Banarasi/zari/silk claims from a style example to another
product. Inspect the outputs against the source, check the portrait dimensions,
and verify the actual featured media ID after upload. If the source cannot
support a faithful hero, request a better source instead of guessing its design.
Manual Gemini editing is no longer required. The user reviews finished listings,
so do not impose an image approval step for routine, faithful results.

Use ignored `product-ops/local/processing/<sku>-<submission-identity>/` for working
files. `submission-identity` is the first 12 hex characters of SHA-256 of
`sku + newline + submittedAt`. Preserve interrupted working files only while
needed to resume; keep photo bytes out of the shared register and public Git.
If a fresh session still has valid working files or verified uploaded media,
reuse them. Otherwise request this SKU's photo again, not every earlier photo.

**Create/reuse the listing.** Follow the listing reference, checking exact and
legacy SKU forms before creating anything. Complete content, taxonomy,
collections, category metafields, variant, price/cost and inventory. Exclude gift
tags and gift collections for every category. Use ordinary
write tools, not a panel that requires the user to press Save. Checkpoint product
and media IDs immediately after successful external writes. Check current Shopify
state after a timeout before retrying. Never create a second product or upload
another copy merely because the prior tool response was lost. Never restock an
already active product on retry.

**Upload and record its link.** Upload the finished images from chat/local files
using the connector's working file-reference path; do not open a manual file picker.
The first live run verified upload_image(imageFile=the original generated path)
without merchant clicks; see the fast path for the bounded upload_file fallback.
Attach uploaded file IDs to the product using the connector's documented
reference-attachment operation, avoiding a second upload by URL. Reuse known
file IDs on resume. Audit the completed draft, reread the register and record
its canonical store URL through `ready --sku SKU --expected-sha256 HASH --url URL`.
This logs SHOPIFY_URL_RECORDED and moves it to READY_TO_PUBLISH. The user does
not paste the link or run an additional status shortcut.

**Publish and verify.** Unless the user requested draft-only, recheck the listing,
current prices/stock and newly arrived pending out-of-stock requests. Then activate
and publish to the Online Store, then read Shopify
again to confirm its publication, exact SKU and listing fields. An ACTIVE status
alone, a draft admin link or an HTTP 200 page is not proof of Online Store
publication. Build a fresh verification receipt from the actual tool results as
specified below; never fabricate it to satisfy the helper. Use `publish --sku SKU
--expected-sha256 HASH --receipt FILE` to log PRODUCT_PUBLISHED and record LIVE.
If Shopify succeeded but the register update failed, report that exact split and
resume the record update after re-verification; do not create/publish again.

**Advance.** Give a brief success line with the product link, clean the temporary
source and generated working copies after Shopify media is verified, and ask for
only the next SKU's photo. Keep going until the frozen queue is finished or the
user stops. Final report: live product links, drafts/blocked SKUs and exact reasons,
and any remaining image/print checks. Do not claim actual B1 printing occurred.

## Logged register updates and checkpoints

Use `register_ops.py`; do not hand-edit rows, CSVs or invent status flags in
Shopify. The helper archives previous rows, writes the existing activity events,
uses current-row fingerprints and journals multi-file changes for recovery.
It preserves SKU, prices, stock fields, notes, submission identity and source
photo links. Its lock coordinates local helper processes, not all iCloud devices.
Do not have the client/operator simultaneously edit the same SKU during a run.

See [register helper](references/register-helper.md) for exact commands, checkpoint
fields, publication receipts and interruption recovery. Keep job state in
`agent/jobs/` and transaction intents in `agent/transactions/` within the shared
operations root so a new session can resume. These contain metadata only.

For missing information, invalid media or SKU collisions, block only the affected
SKU and explain the specific need. Honor connector approval prompts; this skill
cannot suppress host-enforced confirmations. Never turn a failed read, unknown
quantity or missing permission into an assumed success.
After two targeted retries with the same unresolved image/tool failure, preserve
the partial state, block that SKU and report it rather than loop indefinitely.
