# Shopify listing and publication rules

Read this during product processing. Discover operations and unfamiliar fields
with the connected Shopify schema tools; use the Shopify skill when available.
This file describes merchant rules, not a frozen API schema. Check mutation
userErrors and inspect state after timeouts before retrying.

## SKU identity and retries

Search current and legacy forms, for example PBS-SAR-069 and PBS/SAR/069, then
compare returned SKUs exactly, ignoring case. Shopify search matches loosely.

- No active/draft exact match: create one DRAFT product.
- A matching draft belonging to this job: reuse its ID and complete missing work.
- An ACTIVE match: verify whether this job already published it. If so, reconcile
  the register without changing inventory or duplicating uploads. Otherwise stop
  the affected SKU rather than adopting another product.
- Several active/draft matches, a different job's draft, or an existing link/ID
  mismatch: stop that SKU and report the collision.
- Sagar explicitly authorised rebuilding the archived catalogue with numbering
  restarted at 001. Archived legacy matches may remain historical during this
  rebuild, but must be reported and never edited/reactivated. Create a fresh
  listing only when there is no active/draft exact match. Outside that authorised
  rebuild, do not assume archived SKU reuse is permitted.

Persist productId, variantId, inventoryItemId, handle and media IDs through the
checkpoint helper as soon as each external write succeeds. If creation succeeded
but the checkpoint did not, inspect matching drafts, their creation time and
their actual content before recovering ownership. Ambiguity blocks the SKU.

## Product content

- Title: concise colour, visible motif/craft where certain, and product type.
  No supplier/marketplace brands, “Copy”, placeholders or unsupported claims.
- Description: one or two short HTML paragraphs, grounded in the photo and
  client facts. Fabric, dimensions, dye, origin and care claims need evidence;
  leave optional unknowns out instead of guessing.
- SEO: plain description of 140–155 characters, without price or “buy now”.
  Leave SEO title empty so Shopify uses the product title. Derive the handle
  from the final title and inspect Shopify's actual returned handle.
- Vendor: Periwinkle By Sherry.
- One Default Title variant, no one-value colour/fabric options.

Resolve category/collections against the current store. Existing baseline:

| Code | Product type / taxonomy baseline | Manual collection handle |
|---|---|---|
| SAR | Saree / aa-1-23-2-1 | periwinkle-sarees |
| DUP | Dupatta / aa-2-31-4 | frontpage |
| SKZ | Unstitched Salwar Suit / aa-1-19-4 | periwinkle-salwar-suit-sets |
| MIN | Miniature / hg-3 | periwinkle-miniatures |
| HOM | Actual visible object; discover taxonomy | periwinkle-ceramics for ceramics; verify other objects |
| JEW | Earrings/necklace/ring; aa-6-6 for earrings, discover others | periwinkle-jewellery-india-hasn-t-seen-yet |
| RED | Actual identifiable ready-made garment; discover taxonomy | Resolve existing appropriate collection |

Validate the baseline against live store/taxonomy data; IDs use the
gid://shopify/TaxonomyCategory/ prefix. Do not create a new collection or change
store structure during a listing run. If a required mapping cannot be resolved
from the photo, client information and existing store, block that SKU and ask a
focused question. Do not ask routinely when the object is identifiable.

Reuse existing product hashtags only when the visible craft/material is clear.
For miniatures add an established material tag where known, since it drives
smart collections. Add no gift tags and no gift-collection membership, regardless
of category or price. Sagar deferred all gifting to a separate future automation
on 22 November 2026. Do not apply the superseded blanket gift rule from decision 2
or ask for gift eligibility while processing intake.
Do not create wf-/album-/processing tags; iCloud remains the workflow authority.

Set plain colour category metafields using existing colour metaobjects. Create
a missing plain colour only when needed and supported by the current schema.
Do not create poetic shade names. Fabric metafields require client-stated fabric;
reuse an existing fabric metaobject. Follow current custom-data tool guidance.

## Price, inventory and media

Read sellingPrice and costPrice from the current register row before writing
and again before publishing. Configure tracked inventory, DENY overselling,
requiresShipping true and taxable false. Resolve the active “Shop location”
from the store rather than trusting a remembered location ID.

Initial quantity is 1 unless the user/client has specified another value. Read
current quantities, use the schema's compare-and-set quantity input and a stable
per-job idempotency key, and activate inventory at the location when needed.
Checkpoint inventoryInitialized after success. A resumed ACTIVE listing may have
sold: never set it back to 1. This skill does not process stock requests. Keep
the existing zero-weight convention until actual category averages are supplied;
report that unresolved shipping setup rather than invent a weight.

Attach a premium 4:5 editorial hero plus at least one genuine supporting detail.
Use an Indian model for apparel/jewellery and a styled product scene for objects,
following [the category prompts](product-imagery.md). Detail crops and plain
fabric photographs are supporting media. Preserve existing useful detail images
when adding a hero. Inspect the sold item's colour, pattern, border and shape
against the source; the model/setting must not introduce false product facts.
Use stable SKU/hash filenames and descriptive alt text. Put the hero first and
verify its actual featured media ID; adding it last does not feature it. Persist
file IDs; attach existing files using
reference attachment, not their CDN URL, so Shopify does not make another copy.

## Publication

Before publication verify content, SEO, variant/SKU, current cost/price, inventory
settings, quantity, at least two processed images, vendor, taxonomy, applicable
colour/fabric values, manual collection membership and absence of gift tags or
gift collections. Pending out-of-stock requests or an OUT_OF_STOCK register row block intake.

Set ACTIVE and publish to the Online Store only, then query the actual publication
state using the current schema. Do not publish other sales channels implicitly.
Build the canonical custom-domain link from the returned handle. Record the
verification receipt only from fresh tool results, then update the register through
the helper. If activation succeeded but publication failed, keep the accurate
partial state and resume publication rather than recreate the product.

After the batch audit duplicate titles/SKUs, reused descriptions, missing product
types and zero weights; report actual findings. Print/Add in NIIMBOT and physical
attachment of labels remain client actions; a generated image is not proof of print.
