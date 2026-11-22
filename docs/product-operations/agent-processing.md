# Processing products with one photo handoff per SKU

Sagar invokes **add-products** in a fresh agent session with the Periwinkle repo,
the iCloud operations folder, Shopify connector and image-editing tool available.
The skill reads the actual queue and asks for one product's photo at a time.
Sagar opens that SKU in the existing Register/Work on Product preview, copies or
shares its image into chat, and the agent finishes that product before asking
for the next. A count such as nine is an example, not a fixed batch size.

```text
Client submits → NEW
Agent claims current SKU → IN_PROGRESS
Sagar pastes that SKU's image → agent checks/edits/uploads and completes draft
Agent records verified store URL → READY_TO_PUBLISH
Agent publishes and verifies Online Store availability → LIVE
Agent requests the next SKU's photo
```

No manual Gemini editing, Shopify image upload, URL pasting or status shortcut
is part of the normal agent route. Physical label printing remains with the
client. The existing two role shortcuts remain available for submission,
preview, corrections and manual operation; no new shortcut installation is needed.

## Starting a new session

Use **$add-products** in Codex, **/add-products** in Claude Code, or explicitly
ask the agent to process the new register products. The canonical skill lives
in .claude/skills/add-products; .agents/skills/add-products links to it for Codex
repository discovery. See the official [Codex skill-discovery guide](https://learn.chatgpt.com/docs/build-skills).

The normal invocation requests processing through publication. `status` is
read-only; `list SKU` stops at a prepared draft; `live SKU` validates and publishes
an agent-owned prepared listing. Updating the skill does not itself run a batch.
The skill does not watch the register in the background.

This is a phone-based photo handoff, not a proven all-iPhone execution engine.
The session still needs access to iCloud register files and the relevant tools.
Pasting an image into a mobile chat does not by itself give that chat access to
the Mac's filesystem. If access is absent, the agent reports it before writing.
For the normal pasted-photo route, Mac Photos export and an unlocked Photos UI
are not required; the Mac/runtime hosting file access still has to be available.

Only the current SKU is claimed. Other NEW submissions stay editable until their
turn. The agent freezes a candidate list per invocation, refreshes each row and
uses the corrected register prices. Blocked/ambiguous items are reported while
independent items can continue. Pending stock requests are reported separately;
the skill does not process them or publish through an unresolved out-of-stock request.

## What the agent completes

The skill checks SKU collisions, observes product facts from the pasted source,
prepares a premium 4:5 editorial hero and genuine supporting image/detail, inspects
the files, fills the listing checklist, creates/reuses a draft, configures its
default variant, price/cost, inventory, category/metafields, tags and collections,
uploads and attaches finished media, publishes to the Online Store and verifies
the result. It then records the product URL, LIVE status and publishedAt with
the same activity-event schema used by the operator shortcuts.

The hero uses an Indian model for apparel/jewellery, and a styled product scene
for objects. Plain fabric and detail views remain later gallery images. The
skill includes [category prompts](../../.claude/skills/add-products/references/product-imagery.md)
and a [verified API fast path](../../.claude/skills/add-products/references/shopify-fast-path.md)
so each fresh session can reuse the successful operation shapes and resolve
store settings once per batch. The example Banarasi art direction does not
authorize Banarasi/silk/zari claims for unrelated products.

No product is marked as a gift, at any price or in any category. A separate
gifting automation is [deferred](improvements.md#deferred-gifting-automation).

Unknown optional fabric/dimension/origin details are omitted, not invented.
Missing required information or a misleading image blocks the affected SKU.
Connector-enforced approvals may still require a click; the skill does not add
routine draft/image approvals or pretend it can bypass host confirmations.

## Register writes and recovery

read_register.py remains read-only. register_ops.py is the authorised operator
writer for this workflow. It supports only start, ready/link, publish, metadata
checkpoint and transaction recovery. It does not change submission records,
cost/selling prices, stock fields, settings or photo mappings.

Before every mutation it checks the current row fingerprint. Earlier rows go
to register/_replaced/agent-UUID/, with PROCESSING_STARTED,
SHOPIFY_URL_RECORDED and PRODUCT_PUBLISHED logs attributed to operator. A
publication receipt derived from a fresh Shopify verification is required for
LIVE; the helper itself is not a Shopify API client.

agent/jobs/<sku>.json stores submission-bound checkpoints and Shopify/media IDs.
agent/transactions/<uuid>.json stores the intended before/after row and event.
agent/tmp/ is only for atomic metadata staging, not image caching. Restore the
entire agent directory with the other operational data after accidental deletion.

The helper uses atomic local file replacement and a local advisory lock. iCloud
is not a distributed database: another phone's simultaneous edit can still
arrive later. Maintain one editor per SKU. Unexplained changes/conflict copies
are preserved and reported rather than overwritten.

On interruption, inspect pending transaction intents and use the skill's
documented recover command. Publication recovery requires a fresh Shopify
receipt. Completed operations are no-ops on retry. A new session resumes
agent-owned unfinished rows, reuses verified draft/media IDs and never restocks
a product that may already have sold. It does not automatically adopt unrelated
manual IN_PROGRESS work. Temporary image files stay outside shared metadata and
are removed once final Shopify media is verified.

## Validation boundary

The helper is tested against isolated filesystem fixtures, including interruption
after each write phase, stale rows, publication receipts, link corrections,
conflict copies and retry behaviour. Those tests do not establish actual Shopify
creation or image quality on their own. The first live run on 22 November
published PBS-SAR-001 and logged its register transitions successfully. Merchant
review then replaced its fabric-first presentation with an Indian-model hero,
retained both detail images, and removed gift classification. Shopify verified
the hero first, all three media READY and only Sarees collection membership.
The second product, PBS-SAR-002, subsequently completed the full route with a
model-led hero and one supporting detail. Final Shopify/register reads verified
both products live, unique SKUs/titles/descriptions, correct prices and one-piece
tracked inventory, no gift membership and an empty processing queue. Zero shipping
weights remain the known store setup limitation. See [the batch audit](test-report.md#first-real-two-product-batch--22-november-2026).
