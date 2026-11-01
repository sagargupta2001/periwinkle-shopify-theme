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

Run these with the `/add-products` skill
([`.claude/skills/add-products/SKILL.md`](../.claude/skills/add-products/SKILL.md)).
On its own it shows the status board; the steps marked **Claude** below are
its `details`, `sku` and `live` steps.

| Step | Who | Where | Tags after |
|---|---|---|---|
| 1. Post the piece's photos in the shared album | Client | Album | — |
| 2. Create a **draft** in the Shopify iPhone app. Title `Album dupatta N` (next number), photo from the shared album in the photo picker, tag `wf-needs-details`. Nothing is saved to the laptop. | Sagar | Shopify app | `wf-needs-details` |
| 3. Comment **"Draft N"** on that photo in the album | Sagar | Album | — |
| 4. `/add-products details`: title, description, type, handle, collection and stock settings from the photo. Sagar checks the list of new titles. | Claude | Shopify | `wf-needs-sku`, `album-N` |
| 5. Ask for SKU and price under the "Draft N" comment | Sagar | Album | — |
| 6. Reply under the same comment: `PBS-DUP-001, ₹2,850` (and quantity if more than one) | Client | Album | — |
| 7. `/add-products sku` with a screenshot of the thread, or lines like `Draft 12 = PBS-DUP-001, ₹2,850`. Claude checks each SKU against the whole store, then sets SKU, price, quantity and `gift`. | Sagar → Claude | Chat → Shopify | `wf-needs-photos` |
| 8. Make 2–3 shots at 4:5 in Gemini, add them to the product in the Shopify app, and remove the raw album photo **from the product** (the original stays in the album, which remains the source of truth) | Sagar | Gemini, Shopify app | — |
| 9. `/add-products live Draft N`: checklist, then Active, with the link | Claude | Shopify | none |
| 10. Comment `Listed · SKU · price · link` on the album photo | Sagar | Album | — |
| 11. Print the SKU label **from Shopify**, never from the comment | Client | Retail Barcode Labels app | — |

Sagar only ever types one tag (`wf-needs-details`, at step 2). Claude moves
the rest whenever a step is handed over. If you do a step without Claude,
change the tag in the app at the same time.

### Status board

- **Shopify:** admin → Products has saved views "1 · Needs details",
  "2 · Needs SKU" and "3 · Needs photos". An Active product with no `wf-` tag
  is done. `/add-products` shows the same board and flags tags that don't
  match the product.
- **Album:** no comment means not started, "Draft N" means in progress, and
  "Listed" means done.

`album-N` keeps the link between the product and its "Draft N" comment after
the placeholder title is replaced. It's removed when the product goes live.

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
`/add-products` fills everything here except what's marked *client* or
*Sagar*.

- **Title:** describe the piece, for example "Teal Pattachitra Dupatta with
  Tree of Life". No supplier or marketplace brand names, no "(Copy)", and no
  placeholder left behind (decisions 9–11).
- **Description:** state only what is known from the client's comment or the
  photo. If fabric, length or another detail is unknown, leave it out rather
  than guess (decision 17).
- **SEO:** leave the SEO title empty, since it falls back to the product
  title. Write a meta description of about 155 characters.
- **URL handle:** built from the final title, replacing the placeholder.
- **Vendor:** Periwinkle By Sherry.
- **Product type:** Saree, Dupatta, Unstitched Salwar Suit, Miniature,
  Ceramics, Bag, or European earrings / necklace / ring.
- **Category** (Shopify's standard taxonomy): for dupattas, *Apparel &
  Accessories > Clothing Accessories > Traditional Clothing Accessories >
  Dupattas*.
- **Category metafields:**
  - Colour from the photo, using a plain existing colour name.
  - Fabric only when the client states it.
- **Collections:** add dupattas to *Periwinkle Dupattas*, sarees to
  *Periwinkle Sarees* and miniatures to *Periwinkle Miniatures* by hand,
  because those collections are manual (decision 5).
- **Tags:**
  - `gift` for gift-worthy pieces at ₹5,000 or less (decisions 1–2).
  - Hashtags (`#pattachitra`, `#kanthastitch`…), only from those already in
    the store and only when the craft is clear.
  - Material tags for miniatures.
  - The current `wf-` status tag, and `album-N` until the product is live.
- **Variant:** one product, one variant. Use the single *Default Title*
  variant with no options such as "Color" or "Fabric". A one-value option
  makes the product page show a pointless picker.
- **SKU, price, quantity:** *client*. Usually 1.
- **Inventory:**
  - Keep *Track quantity* on.
  - Keep *Continue selling when out of stock* off (decision 16).
  - Taxable off, like the rest of the store.
- **Weight:** 0 until category averages are set, then the average for the
  type (decision 13).
- **Photos:** *Sagar*. Use the client's own pieces, refined in Gemini at 4:5.
  Never use screenshots from shopping apps.

## After listing

After each batch, run a quick audit for duplicate titles, shared
descriptions, blank or duplicate SKUs, leftover `wf-` tags on active products,
missing product types and zero weights. Record the results in
[store-status.md](store-status.md).
