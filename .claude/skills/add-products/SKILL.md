---
name: add-products
description: List a product the client submitted through the Periwinkle shortcuts in Shopify. Reads the register in iCloud, compares it with Shopify, creates the draft listing from the register's SKU and prices and the photos provided, and takes finished listings live. Use when the user runs /add-products, asks what's waiting to be listed, pastes details copied from Work on Product, or says a product's photos are done.
argument-hint: "[status | list <SKU> | live <SKU>]"
---

# Add products

This is the Shopify half of the workflow in
[docs/product-operations/README.md](../../../docs/product-operations/README.md).
Every listing must meet the [listing checklist](../../../docs/product-operations/listing-checklist.md).
If this file and those docs disagree, the docs win.

## Who owns what

| | Owner | How it changes |
|---|---|---|
| SKU, prices, publication and stock status | The register in iCloud | Only the shortcuts, on an iPhone |
| Listing content, photos, quantity | Shopify | This skill and the admin |

- **Never write to the register.** Writing there would skip the activity log. Read it
  with the script below, then tell the user which shortcut to run.
- **Never keep status in Shopify.** No `wf-` or `album-` tags, or any other tracker
  (decision 22).
- **Run only the step asked for.** This skill doesn't change stock. Pending stock requests
  go through Process Stock Requests, and `status` only reports them.

Read the register with this script. It finds a product's real status, and lists anything a
stopped run left behind under `problems`.

```bash
python3 .claude/skills/add-products/read_register.py
python3 .claude/skills/add-products/read_register.py --sku PBS-DUP-004
```

If the Shopify Admin tools (`graphql_query`, `graphql_mutation`) aren't available, say so
and stop.

## Pick the step

- Nothing, `status`, "what's waiting": **Status**
- `list <SKU>`, or details pasted from Work on Product: **List**
- `live <SKU>`, "photos done for …": **Live**

If it's unclear, show Status and ask.

## Status

Run the script. Then look up every SKU in Shopify, in batches of up to 25, with
`productVariants(query: "sku:A OR sku:B")`. Report each group with its next action:

| Register | Shopify | Next action |
|---|---|---|
| `NEW` | Any | Run Work on Product → Start a new product |
| `IN_PROGRESS` | Not there | `/add-products list <SKU>` |
| `IN_PROGRESS` | Draft | Add photos if needed, then Work on Product → Add or fix a Shopify link |
| `IN_PROGRESS` | Active | Work on Product → Add or fix a Shopify link → I've checked it's live |
| `READY_TO_PUBLISH` | Draft | `/add-products live <SKU>` |
| `READY_TO_PUBLISH` | Active | Run Publish Products |

Flag these as mismatches, and don't fix them without asking:
- `READY_TO_PUBLISH` or `LIVE`, but the SKU isn't in Shopify
- `LIVE`, but the product isn't Active or isn't on the Online Store
- The register's selling price or cost differs from Shopify's
- The register's `shopifyUrl` handle differs from the product's handle
- `OUT_OF_STOCK` on record with a quantity above 0. `IN_STOCK` with a quantity of 0 may just
  mean it sold, so mention it without calling it an error.
- Any `problems` from the script

Also list pending stock requests with each product's Shopify quantity, and point to Process
Stock Requests. `LIVE` products with no mismatch only need a count.

## List

Run this once per SKU. It's safe to run again: step 3 finds the earlier draft.

**1. Check the register.** Run the script with `--sku`. Use the row's prices, because
`products/` keeps what was first submitted and the row has any corrections. Pasted details
only tell you which SKU to use.
- Not found: stop. It has to go through New Product first.
- `NEW`: stop, and ask the user to run Work on Product → Start a new product, so the register
  shows it's being worked on.
- `IN_PROGRESS`: continue.
- `READY_TO_PUBLISH` or `LIVE`: stop and report. It's already past this step.
- Selling price of 0, or not above cost: ask before continuing.

**2. Get the photos.** You can't see the Shared Album. The user has to attach a photo or give
a local path, and step 5 needs it. If there's none, ask, reminding them of the row's
`submittedAt` date so they can find it in the album. Never describe a piece you haven't seen.

**3. Look for the SKU in Shopify.** The register can't see older products, and older SKUs use
another format, so search for both forms: `sku:PBS-SAR-069 OR sku:PBS/SAR/069`. Shopify's
matching is loose, so compare the results in code, ignoring case.
- No match: continue.
- One match on a Draft with this exact SKU: it's the earlier attempt. Fill in only what's
  missing, and don't create a second product.
- Anything else: stop and report which product holds it. Two pieces sharing an SKU can mean
  the wrong one gets packed. The client may need Fix Product to cancel and resubmit.

**4. Find the category.** Take the code from the SKU, then look up the collection by handle
with `collections(query: "handle:<handle>")`.

| Code | Product type | Taxonomy category | Manual collection handle | Gift set |
|---|---|---|---|---|
| DUP | Dupatta | `aa-2-31-4` | `frontpage` | Yes |
| SAR | Saree | `aa-1-23-2-1` | `periwinkle-sarees` | Yes |
| SKZ | Unstitched Salwar Suit | `aa-1-19-4` | `periwinkle-salwar-suit-sets` | No |
| MIN | Miniature | `hg-3` | `periwinkle-miniatures` | Yes |
| HOM | Ceramics or Wooden Antique Box: ask | Ask | `periwinkle-ceramics` | Yes |
| JEW | European earrings, necklace or ring: ask | `aa-6-6` for earrings, otherwise search | `periwinkle-jewellery-india-hasn-t-seen-yet` | Only if European |
| RED | No type yet: ask | Ask | Ask | Ask |

Taxonomy IDs are written `gid://shopify/TaxonomyCategory/<id>`. Search with
`taxonomy { categories(search:) }` when you need one that isn't here, and add it to this
table. An unknown code: stop and ask. See [docs/sku-codes.md](../../../docs/sku-codes.md).

**5. Write the content, from what the photo shows** (decision 17):
- **Title:** colour, craft, fabric if clearly identifiable, motif and type. For example, "Teal
  Pattachitra Dupatta with Tree of Life". No brand names or "(Copy)" (decisions 9–11).
- **Description:** one or two short `<p>` paragraphs. Leave out fabric, length or dye if you
  aren't sure. Never guess.
- **SEO description:** one plain sentence of 140–155 characters, with no price or "buy now".
  Leave the SEO title empty.
- **Hashtags:** only from `productTags(first: 250)`, and only when the craft or fabric is clear.
  Suggest a new one to the user instead of creating it. Miniatures also need their material
  tag where it's clear (`#glass`, `#wooden`, `#porcelain`), because it drives their smart
  collections (decision 4).
- **`gift` tag:** add it if the type is in the gift set and the selling price is ₹5,000 or
  less (decision 2).

**6. Create the draft** with `productCreate`, passing `status: DRAFT`, `title`, `handle` (from
the title), `descriptionHtml`, `seo: {description}`, `productType`, `vendor: "Periwinkle By
Sherry"`, `category`, `tags` and `collectionsToJoin`. Select the default variant's `id`, and its
inventory item's `id`.

Then set the category metafields with `metafieldsSet`, as `list.metaobject_reference` with a
JSON array of metaobject IDs:
- **Colour** (`shopify.color-pattern`): the main one or two colours you can see. Reuse a plain
  name from `metaobjects(type: "shopify--color-pattern")`. If a plain colour is missing, create
  it in the same shape. Don't create shade names like "dusty rose".
- **Fabric** (`shopify.fabric`): only if the client stated it. Reuse an existing
  `shopify--fabric` metaobject.

**7. Set the variant.** There's one product and one variant, the *Default Title*. Use
`productVariantsBulkUpdate` with `price` from `sellingPrice`, `taxable: false`,
`inventoryPolicy: DENY`, and `inventoryItem: {sku, cost, tracked: true, requiresShipping: true}`,
with `cost` from `costPrice`. Use the SKU exactly as the row has it. Leave the weight at 0 until
averages are recorded (decision 13).

**8. Set the quantity to 1**, unless the user says otherwise. Read the current quantity first,
then use this at `gid://shopify/Location/102961152023` ("Shop location"):

```graphql
mutation SetQuantity($input: InventorySetQuantitiesInput!, $key: String!) {
  inventorySetQuantities(input: $input) @idempotent(key: $key) {
    userErrors { code field message }
  }
}
```

Each quantity needs `changeFromQuantity`, set to the current quantity. `$key` is a new UUID from
`uuidgen`, reused only if you're retrying the same change. If the item isn't stocked there yet,
use `inventoryActivate` with `available`, which needs `@idempotent` too.

**9. Report.** Show:
- the title, colours, hashtags and whether it got the `gift` tag, plus anything you were unsure
  of, such as "fabric not stated, looks like cotton";
- the admin link;
- the store link: `https://periwinklebysherry.com/products/<handle>`.

Then tell the user what's left:
1. Add the client's photos, refined in Gemini at 4:5, in the admin. This skill doesn't
   upload them.
2. Run Work on Product → Add or fix a Shopify link, paste the store link, and choose
   *Not yet: mark READY_TO_PUBLISH*.
3. Run `/add-products live <SKU>`.

## Live

Run the script with `--sku`, and load the product by SKU. If it's already Active and on the
Online Store, change nothing and go to the last paragraph of this section.

The register must say `IN_PROGRESS` or `READY_TO_PUBLISH`. Then check all of these:

- At least two images, and no raw album photo or screenshot. Ask if you can't tell.
- The title isn't a placeholder, and the description and SEO description are there.
- `hasOnlyDefaultVariant` is true, and the SKU matches the register exactly.
- **Price and cost match the register's row now.** Either could have been corrected since the
  draft was made.
- Quantity of 1 or more, tracked, policy DENY, taxable off.
- Vendor and taxonomy category are set. Colour is set where the piece has a clear one.
- It's in its manual collection, and the `gift` tag is right for its current price.

If anything fails, list it and change nothing. Otherwise, use `productUpdate` to set
`status: ACTIVE`, then `publishablePublish` for the Online Store only. Find that publication with
`publications { nodes { id catalog { title } } }`, and confirm with
`publishedOnPublication(publicationId:)`.

Give the store link, and the one shortcut left to run:
- `READY_TO_PUBLISH`: run Publish Products.
- `IN_PROGRESS`: run Work on Product → Add or fix a Shopify link → *I've checked it's live*.

Remind the user to print the label from Shopify.

## Rules

- Check `userErrors` on every mutation. If a step fails, stop and report what's done and what
  isn't. Running the step again carries on from there.
- Use GraphQL variables for description HTML. Documents are limited to 16,384 characters.
- The Admin tools reject deprecated fields. Use `sources` rather than `ruleSet`,
  `publishedOnPublication` rather than `publishedOnCurrentPublication`, and `catalog { title }`
  rather than `Publication.name`. `onlineStoreUrl` comes back empty here, so build store links
  from the handle.
- Search filters such as `tracked:` are silently ignored, so filter in code.
- Smart collections recount asynchronously, so counts can look stale just after a change.
- Something structural, such as a new code or category, belongs in
  [docs/sku-codes.md](../../../docs/sku-codes.md) or
  [docs/decisions.md](../../../docs/decisions.md). Say so.
