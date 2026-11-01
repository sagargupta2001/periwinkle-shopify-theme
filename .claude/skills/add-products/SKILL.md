---
name: add-products
description: Run the Periwinkle product-listing workflow (shared Apple Photos album → Shopify). Shows the status board of products tagged wf-needs-details / wf-needs-sku / wf-needs-photos, fills in details from draft photos, sets SKU, price and stock from the client's album replies with a store-wide clash check, and takes finished products live. Use when the user runs /add-products, pastes the client's SKU and price replies, says "photos done for …", or asks what products are pending.
argument-hint: "[status | details | sku <replies> | live <Draft N or SKU>]"
---

# Add products

You are running the listing workflow described in
[docs/adding-products.md](../../../docs/adding-products.md). Read that doc
first if you haven't this session; it is the human-readable version and wins
if the two ever disagree. Everything happens in Shopify through the Shopify
Admin MCP tools (`graphql_query`, `graphql_mutation`). If those tools aren't
available, say so and stop.

**State lives in Shopify, not here.** Never keep a separate tracker. Work out
where every product is by reading its tags each time.

| Tag | Meaning | Who acts next |
|---|---|---|
| `wf-needs-details` (+ placeholder title "Album dupatta N") | Sagar created the draft from an album photo | Claude: `details` |
| `wf-needs-sku` | Details done | Client replies in the album; Sagar pastes it: `sku` |
| `wf-needs-photos` | SKU, price and stock set | Sagar adds Gemini photos, then: `live` |
| no `wf-` tag, Active | Listed | — |

`album-N` links a product to the "Draft N" comment on its album photo. Add it
in `details` (from the placeholder title, before renaming) and remove it in
`live`.

Saved product views "1 · Needs details", "2 · Needs SKU" and "3 · Needs
photos" exist in Shopify admin for Sagar.

## Pick the step

From `$ARGUMENTS` or the user's words:

- nothing, `status`, "what's pending" → **Status**
- `details`, "draft the products" → **Details**
- `sku`, pasted lines or a screenshot of album comments with codes and prices → **SKU**
- `live …`, "photos done for …" → **Live**

If unclear, show Status and ask which step.

## Status

Query products with `tag:wf-needs-details OR tag:wf-needs-sku OR tag:wf-needs-photos`
(title, status, tags, variant SKU and price, media count). Report counts and
names per stage, using "Draft N" and the title. Then flag mismatches:

- `wf-needs-sku` but the variant already has an SKU, or `wf-needs-photos` without one
- an Active product that still has a `wf-` or `album-` tag
- a draft titled "Album …" with no `wf-` tag
- two products with the same `album-N` tag

End with the single next action for each non-empty stage.

## Details

For each product tagged `wf-needs-details`:

1. Read its title for N (from "Album dupatta N"; ask if there's no number)
   and look at its images.
2. Write a **title** describing what is visible: colour, craft, fabric only
   if clearly identifiable, motif, type. For example "Teal Pattachitra
   Dupatta with Tree of Life". No brand names, no "(Copy)".
3. Write a **description** in the store's style: one or two short `<p>`
   paragraphs about the piece and its craft. **State only what the photo
   shows** (decision 17). Leave out fabric, length or dye if unsure; never
   guess.
4. In one `productUpdate`: title, `descriptionHtml`, a `handle` built from the
   new title (with `redirectNewHandle: true`), `productType` (Dupatta for the
   dupatta rebuild), and tags: keep existing ones, add `album-N`, remove
   `wf-needs-details`, add `wf-needs-sku`. Keep status DRAFT.
5. Add it to the category's manual collection with `collectionAddProducts`:
   - Dupatta → Periwinkle Dupattas `gid://shopify/Collection/485522309143` (its handle is `frontpage`)
   - Saree → Periwinkle Sarees `gid://shopify/Collection/487135739927`
   - Miniature → Periwinkle Miniatures `gid://shopify/Collection/492680544279`
6. With `productVariantsBulkUpdate`: `inventoryPolicy: DENY`,
   `inventoryItem: {tracked: true}`.

Then give Sagar a list, "Draft N → new title", and point out anything you were
unsure of (for example "fabric not stated, looks like cotton"). Remind him to
ask the client for the SKU and price under each "Draft N" comment.

## SKU

Parse each reply into Draft N, SKU, price and optional quantity (default 1).
Accept typed lines ("Draft 12 = PBS-DUP-001, ₹2,850") or screenshots of the
album thread, where Sagar's "Draft N" comment and the client's reply sit
together. If you can't tell which draft a reply belongs to, ask. Never guess
the match from the photo alone.

Before any write, check **every** SKU:

1. **Format:** `PBS-<CODE>-<NNN>`, uppercase, hyphens, at least three digits,
   and the code is listed in [docs/sku-codes.md](../../../docs/sku-codes.md).
   Fix obvious formatting (`pbs dup 1` → `PBS-DUP-001`) but tell Sagar.
   Unknown code → stop and ask.
2. **Clash:** query `productVariants(query: "sku:<SKU>")` across the whole
   store, drafts included. Any hit on a different product → stop for that
   one and report which product holds it. Also check for duplicates within
   the batch.
3. **Sequence:** note gaps or out-of-order numbers against the highest
   existing number for that code. A gap isn't an error, just mention it.
4. **Match:** the product has `album-N` and `wf-needs-sku`. If it's at
   another stage, ask before changing it.

Show Sagar the checked list, then for each product that passed:

- `productVariantsBulkUpdate`: `price`, `inventoryItem: {sku, tracked: true}`,
  `inventoryPolicy: DENY`.
- Set the quantity with `inventorySetQuantities` (name `available`, reason
  `correction`) at `gid://shopify/Location/102961152023` ("Shop location").
  Look the location up again if that ID fails.
- Tags: add `gift` if the type is in the gift set (Miniature, European
  jewellery, Ceramics, Wooden Antique Box, Dupatta, Saree) and the price is
  ₹5,000 or less (decision 2). Remove `wf-needs-sku`, add `wf-needs-photos`.

Report what was set and what was held back, and why.

## Live

Find the product by `album-N` or by SKU. Before activating, check:

- at least two images, and no album screenshot or app screenshot left in
  (ask Sagar if you can't tell which is the raw album photo)
- title isn't a placeholder; description present
- SKU set and unique, price > 0, quantity ≥ 1, tracked, policy DENY
- in its category collection; `gift` tag correct for its price

If anything fails, list it and don't activate. Otherwise, in one
`productUpdate`, remove `wf-needs-photos` and `album-N` and set
`status: ACTIVE`. The product must also be published to the Online Store; if
`publishedOnCurrentPublication`/`resourcePublications` shows it isn't, use
`publishablePublish`.

Give Sagar the storefront link and the album comment to paste:
`Listed · <SKU> · ₹<price> · <link>`. Remind him to print the label from
Shopify.

## Rules

- Only the requested step. No other store changes without asking.
- Use GraphQL variables for description HTML. Documents are limited to 16,384
  characters, so batch large updates.
- The API is 2026-10: use `sources`, not `ruleSet`, and `barcodes`, not
  `barcode`. Search filters such as `tracked:` are silently ignored, so filter
  in code.
- After a batch, if collection counts look stale, it's because smart
  collections recount asynchronously.
- If a step reveals something structural (a new code, a new category), say
  it should go in [docs/sku-codes.md](../../../docs/sku-codes.md) or
  [docs/decisions.md](../../../docs/decisions.md).
