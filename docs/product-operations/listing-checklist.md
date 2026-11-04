# Listing checklist

What a Shopify listing needs. The `/add-products` skill follows this list, so it's also
the place to change what the skill checks. Each line points to the decision behind it in
[decisions.md](../decisions.md).

- **Title:** describe the piece, for example "Teal Pattachitra Dupatta with Tree of
  Life". No supplier or marketplace brand names, no "(Copy)", no placeholders
  (decisions 9–11).
- **Description:** state only what's known from the client or the photo. If fabric,
  length or another detail is unknown, leave it out rather than guess (decision 17).
- **SEO:** leave the SEO title empty, since it falls back to the product title. Write
  a meta description of about 155 characters.
- **URL handle:** built from the final title.
- **Vendor:** Periwinkle By Sherry.
- **Product type:** Saree, Dupatta, Unstitched Salwar Suit, Miniature, Ceramics, Bag,
  or European earrings / necklace / ring.
- **Category** (Shopify's standard taxonomy): for dupattas, *Apparel & Accessories >
  Clothing Accessories > Traditional Clothing Accessories > Dupattas*.
- **Category metafields:** colour from the photo, using a plain existing colour name.
  Fabric only when the client states it.
- **Collections:** add dupattas to *Periwinkle Dupattas*, sarees to *Periwinkle
  Sarees* and miniatures to *Periwinkle Miniatures* by hand, because those
  collections are manual (decision 5).
- **Tags:**
  - `gift` for gift-worthy pieces at ₹5,000 or less (decisions 1–2).
  - Hashtags (`#pattachitra`, `#kanthastitch`…), only from those already in the store
    and only when the craft is clear.
  - Material tags for miniatures.
- **Variant:** one product, one variant. Use the single *Default Title* variant, with
  no options such as "Color" or "Fabric", because a one-value option shows a pointless
  picker on the product page.
- **SKU, price, cost:** from the register's row, which includes any corrections. Cost goes
  in *Cost per item*. Search for the SKU in Shopify admin first, in both the `PBS-SAR-069` and
  `PBS/SAR/069` forms, because the register can't see SKUs on older products, and two pieces
  sharing one means the wrong piece can be packed.
- **Quantity:** usually 1.
- **Inventory:** keep *Track quantity* on and *Continue selling when out of stock* off
  (decision 16). Taxable off, like the rest of the store.
- **Weight:** 0 until category averages are set, then the average for the type
  (decision 13).
- **Photos:** use the client's own pieces, refined in Gemini at 4:5. Never use
  screenshots from shopping apps.

After each batch, audit for duplicate titles, shared descriptions, blank or duplicate
SKUs, missing product types and zero weights, and record the results in
[store-status.md](../store-status.md).
