# Adding products

How a new piece goes from the client's hands to a live Shopify product. Sagar
lists products. The client supplies the piece, the photos and the facts.

## The flow

1. **The client fills the intake form**, one form per piece, on her phone.
   She chooses the category and adds photos, price, quantity, colour, fabric,
   craft, weight if known, whether it's gift-worthy, and a line on the story.
   Sarees also ask for length and blouse piece. Suit sets ask for the pieces
   included and the stitching.
2. **The sheet gets a row** in its *Products* tab, with an SKU assigned
   automatically (`PBS-SAR-409`) and Status = New.
3. **Sagar lists it:**
   - Set the row to In progress.
   - Refine the photos.
   - Write the title and description.
   - Create the product, following the checklist below.
4. **Sagar closes the row:** set Status to Listed and paste the Shopify link.

The form and sheet are created by
[`tools/product-intake-form.gs`](../tools/product-intake-form.gs). Setup steps
are at the top of that file.

## Listing checklist

Each line points to the decision behind it in [decisions.md](decisions.md).

- **SKU:** use the one from the sheet, exactly as written (`PBS-<CODE>-<NNN>`).
  Never reuse a number, and never leave the SKU blank. Duplicating a product
  in Shopify clears the SKU, so fill it in again. See
  [sku-audit.md](sku-audit.md).
- **Title:** describe the piece, for example "Teal Blue Handloom Saree with
  Peacock Motifs". No supplier or marketplace brand names, and no "(Copy)".
  When duplicating a listing, change the title, photos, description and URL
  handle before activating it (decisions 9–11).
- **Description:** state only what is known, from the form or the photo. If
  fabric, length or blouse piece is unknown, leave the line out rather than
  guess (decision 17).
- **Product type:** one of Saree, Dupatta, Unstitched Salwar Suit,
  Miniature, Ceramics, Bag, or European earrings / necklace / ring. Smart
  collections depend on it.
- **Collections:** add sarees to *Periwinkle Sarees* and miniatures to
  *Periwinkle Miniatures* by hand, because those collections are manual
  (decision 5). Gifting and material collections fill themselves.
- **Tags:**
  - `gift` if the client said "Good as a gift" and the price is ₹5,000 or
    less (decisions 1–2).
  - Material tags for miniatures (`#glass`, `#wooden`, `#porcelain`).
- **Inventory:**
  - Enter the quantity from the form.
  - Keep *Track quantity* on.
  - Keep *Continue selling when out of stock* off (decision 16).
- **Weight:** use the form value, or the category average once it's set
  (decision 13). Shipping charges and Shiprocket depend on it.
- **Photos:** use the client's own photos. Never use screenshots from
  shopping apps.

## After listing

Once a month, or after a big batch, run a quick audit for duplicate titles,
shared descriptions, blank or duplicate SKUs, missing product types and
zero weights. Record the results in [store-status.md](store-status.md).
