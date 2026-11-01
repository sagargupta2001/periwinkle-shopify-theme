# Adding products

How a new piece goes from the client's hands to a live Shopify product. Sagar
lists products, and the client supplies the piece, the photos, the SKU and the
price.

The **shared Apple Photos album** is where Sagar and the client talk about
each piece. **Shopify** is where the product and its status live. The album
can't filter or label photos, so status is never tracked there.

This replaced the Google Form workflow on 1 November 2026 (decision 21). The
form script is kept in
[`tools/product-intake-form.gs`](../tools/product-intake-form.gs) in case it's
needed again.

## The flow

| Step | Who | Where | Status tag after |
|---|---|---|---|
| 1. Post the piece's photos in the shared album (one album per category; dupattas first) | Client | Album | — |
| 2. Create a **draft** product in the Shopify iPhone app. Add the album photo straight from the photo picker, which shows shared albums, so nothing is saved to the laptop. Use a placeholder title such as "Album dupatta 12". | Sagar | Shopify app | `wf-needs-details` |
| 3. Fill in title, description, product type, collections, tags, weight and inventory from the photo, following the checklist below. Claude can do this step from the draft's photos. | Sagar / Claude | Shopify | `wf-needs-sku` |
| 4. Comment the draft title and a short summary on the photo in the album | Sagar | Album | — |
| 5. Reply with the **SKU and price** | Client | Album | — |
| 6. Check the SKU hasn't been used before (see below), then set the SKU and price | Sagar / Claude | Shopify | `wf-needs-photos` |
| 7. Make 2–3 refined 4:5 shots in Gemini and upload them to the product from the phone. Remove the raw album photo. | Sagar | Shopify app | — |
| 8. Remove the `wf-` tag, set the product **Active**, and comment "Listed · SKU · price · link" on the album photo | Sagar | Shopify + album | none |
| 9. Print the SKU label **from Shopify**, never from the comment, and attach it to the piece | Client | Retail Barcode Labels app | — |

### Status board

In Shopify admin → Products, save one view per tag (`wf-needs-details`,
`wf-needs-sku`, `wf-needs-photos`). Each view is a to-do list. A product with
no `wf-` tag that is Active is done.

### Working with Claude

To have Claude draft products, say which tag to work from. For example:
"draft the products tagged `wf-needs-details`". Claude reads each draft's
photos from Shopify, fills in the details, and moves the tag to
`wf-needs-sku`. It also gives you a short summary to paste into the album.

When the client replies, paste her SKU and price lines, such as
"Album dupatta 12 = PBS-DUP-001, ₹2,850". Claude checks each SKU against the
whole store before setting it.

## SKUs

- Format: `PBS-<CODE>-<NNN>`, uppercase, with hyphens and at least three
  digits. The codes are in [sku-codes.md](sku-codes.md).
- The client assigns the number: the next free number in her notebook for
  that category.
- **Dupattas restart at `PBS-DUP-001`** (November 2026). The old dupatta
  numbers are retired. The products that carried them are drafts with their
  SKUs cleared, recorded in
  [archive/dupattas-before-rebuild-2026-11.csv](archive/dupattas-before-rebuild-2026-11.csv).
- **Before setting an SKU, search for it in Shopify admin → Products.** If
  it's already in use, ask the client for another number. Two pieces sharing
  an SKU means the wrong piece can be packed (see [sku-audit.md](sku-audit.md)).
- Duplicating a product clears its SKU, so set it again.

## Listing checklist

Each line points to the decision behind it in [decisions.md](decisions.md).

- **Title:** describe the piece, for example "Teal Pattachitra Dupatta in
  Chanderi Silk with Tree of Life". No supplier or marketplace brand names,
  no "(Copy)", and no placeholder left behind (decisions 9–11).
- **Description:** state only what is known from the client's comment or the
  photo. If fabric, length or another detail is unknown, leave it out rather
  than guess (decision 17).
- **Product type:** Saree, Dupatta, Unstitched Salwar Suit, Miniature,
  Ceramics, Bag, or European earrings / necklace / ring.
- **Collections:** add dupattas to *Periwinkle Dupattas*, sarees to
  *Periwinkle Sarees* and miniatures to *Periwinkle Miniatures* by hand,
  because those collections are manual (decision 5).
- **Tags:**
  - `gift` for gift-worthy pieces at ₹5,000 or less (decisions 1–2).
  - Material tags for miniatures.
  - The current `wf-` status tag.
- **Inventory:**
  - Enter the quantity.
  - Keep *Track quantity* on.
  - Keep *Continue selling when out of stock* off (decision 16).
- **Weight:** use the category average once it's set (decision 13).
- **URL handle:** let Shopify build it from the final title. If the product
  was created under a placeholder title, update the handle too.
- **Photos:** use the client's own pieces, refined in Gemini at 4:5. Never
  use screenshots from shopping apps.

## After listing

After each batch, run a quick audit for duplicate titles, shared
descriptions, blank or duplicate SKUs, leftover `wf-` tags on active products,
missing product types and zero weights. Record the results in
[store-status.md](store-status.md).
