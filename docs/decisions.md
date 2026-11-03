# Store decisions

An append-only log of decisions about how the store is set up: catalogue,
collections, menus, shipping and content. Most of these live in the Shopify
admin, not in the theme code, so this is the only place the reasoning is
written down. For the current state and open items, see
[store-status.md](store-status.md).

Add new entries at the bottom. Don't edit old ones. If a decision changes, add
a new entry that says which one it replaces, and mark the old one
**Superseded by #N**.

Each entry records what was decided, why, what was rejected, and how to apply
it day to day.

---

### 1. Gifting uses one `gift` tag plus price-tier collections

24 October 2026

**Decision:** A product counts as a gift when it has the plain tag `gift`.
Four smart collections build the Gifting menu: `gifting` (tag `gift`), and
`gifts-under-1000`, `gifts-under-3000` and `gifts-under-5000`, which add a
price range. The tiers don't overlap: Under ₹3,000 means ₹1,001–3,000.

**Why:** The tag lets the client choose what is gift-worthy, and the price
rule sorts each product into its tier. When a product is repriced it moves
tier on its own, with no re-tagging. Non-overlapping tiers stop the same cheap
items filling all three pages.

**Rejected:**
- *Filter links* such as `?filter.v.price.lte=1000`: they are fragile, have no
  page title or description, and home page sections can't feature them.
- *Price-only collections:* they would pull in everything, including items
  that aren't giftable.

**How to apply:** Tag a new gift product `gift`; its tier follows from its
price. The tag is plain on purpose, to keep it apart from the customer-facing
`#hashtags`.

### 2. The gift set is objects, dupattas and sarees up to ₹5,000

24 October 2026

**Decision:** Every active product up to ₹5,000 of these types was tagged
`gift`: Miniature, European jewellery, Ceramics, Wooden Antique Box, Dupatta
and Saree. That was 282 products. Unstitched salwar suits are left out.

**Why:** Small objects are almost all under ₹1,000. Without textiles, the
₹5,000 tier would have been empty.

**Rejected:**
- *Objects and dupattas only:* only 6 products in the ₹5,000 tier.
- *Everything up to ₹5,000:* the least curated option.

**How to apply:** Tagging isn't automatic. New products of these types need
the `gift` tag added by hand.

### 3. Keep collections even when they leave the menu

24 October 2026

**Decision:** The menu can be simplified without deleting collections. A
collection can stay published and be used on the home page without appearing
in any menu.

**Why:** In October 2026, deleting the miniature, salwar and jewellery
collections broke the home page. Links returned 404s, Dawn's placeholder
products appeared, and collection tiles went blank.

**How to apply:** Before deleting or renaming a collection's handle, search
`templates/` and `sections/*.json` for the handle. To take something off the
menu, edit the menu, not the collection.

### 4. Miniature material collections are smart and reuse the old handles

24 October 2026

**Decision:** Glass, wooden and porcelain miniatures are smart collections:
product type Miniature plus a material tag. They reuse the deleted collections'
handles (`miniatures-hand-blown-glass-decor-items`, `miniatures-wooden`,
`miniatures-porcelain`).

**Why:** Reusing the handles made the home page tiles and editorial slider work
again with no theme change.

**How to apply:** Give a new miniature the type Miniature and its material tag,
and it appears in the right collection. There is no bone china tag yet, so the
Bone China tile is disabled in `templates/index.json`. Re-enable it once there
is stock.

### 5. Sarees and Miniatures stay manual collections

24 October 2026

**Decision:** Periwinkle Sarees and Periwinkle Miniatures stay manual. On
24 October, all active sarees and miniatures were added to them by hand.

**Why:** Shopify can't convert a manual collection to a smart one; it would
have to be deleted and recreated. Periwinkle Sarees also uses a hand-arranged
sort order that a smart collection would lose.

**Rejected:** Recreating both as smart collections based on product type. It
was considered, and deferred.

**How to apply:** Add each new saree or miniature to its collection by hand.

### 6. Accessories is hidden from menus until Bags has stock

24 October 2026

**Decision:** Accessories → Bags was removed from the main menu and the footer.
The collection stays, holding one product (Festival Canvas Tote).

**Why:** An empty or near-empty page in the main menu looks unfinished at
launch.

**How to apply:** Add the menu item back once there are enough bags to fill a
page.

### 7. Heirloom links to a collection built from the `#heirloom` tag

24 October 2026

**Decision:** The Heirloom menu item, previously `#`, links to a new smart
collection, `heirloom` (tag `#heirloom`).

**Why:** 22 products already carried the tag, and a dead menu link isn't
acceptable at launch.

### 8. No dead links in menus

24 October 2026

**Decision:** Every menu item points to a real page. Footer Help links go to
the policy pages. FAQs was removed because there is no FAQ page.

**How to apply:** If an FAQ page is created, add FAQs back to Footer — Help.

### 9. Duplicated listings are renamed or drafted, never deleted

24 October 2026

**Decision:** Many products were listed by duplicating an existing product, so
they carried "(Copy)" or identical titles.
- Listings that are a different piece, with their own photos, were renamed
  after what the photo shows (31 products).
- Listings with no image, or identical to another listing, were set to draft
  (9 products).
- Nothing was deleted.

**Why:** Most pieces are one of a kind, with one unit each. Identical titles
confuse shoppers and search engines, but the listings are real stock.
Drafting can be undone; deleting can't.

**How to apply:** When duplicating a product to list a new piece, change the
title, photos and description before activating it.

### 10. Product handles follow titles, with redirects

24 October 2026

**Decision:** 338 product handles were rebuilt from the product title,
replacing `-copy`, `untitled-…` and handles named after a different product.
Long handles are cut at a word boundary to about 80 characters. Shopify
redirects (301) the old URLs.

**Why:** Clean URLs read better when shared and rank better. The redirects
keep any old links working.

**How to apply:** When duplicating a product, fix its handle too (Search engine
listing → URL handle).

### 11. No marketplace brand names in titles

24 October 2026

**Decision:** Supplier brand names were removed from product titles and
descriptions: Kalini, Krutikraft, WOODHANG, KPNG and AWOEZ.

**Why:** They make listings look resold from a marketplace. That clashes with
the curated, handmade positioning.

### 12. Shipping is weight-based, with free shipping from ₹10,000

24 October 2026

**Decision:** Domestic shipping stays weight-based (₹249–₹499). An automatic
discount makes shipping free on orders of ₹10,000 and above. It combines with
product and order discounts.

**Why:** The shipping policy and the announcement bar already promised free
shipping at ₹10,000, but nothing applied it.

**How to apply:** If the threshold changes, update the discount, the shipping
policy and the announcement bar text together.

### 13. Product weights are deliberately 0 for now

24 October 2026

**Decision:** Weights stay at 0 kg until average weights for sarees, dupattas
and miniatures are provided. They will then be set in bulk by product type.

**Why:** There's no per-item weight data yet. An average per type is accurate
enough for the shipping bands.

**Known effect:** Until then, every order pays ₹249 and Shiprocket can't book
couriers.

### 14. One set of contact details everywhere

24 October 2026

**Decision:** Customer-facing contact details are
`support@periwinklebysherry.com`, +91 99726 95620, and the Bengaluru returns
address, written as in [store-status.md](store-status.md#contact-details).

**Why:** The site mixed a Gmail address, two phone numbers, and both
"Bangalore" and "Bengaluru".

**How to apply:**
- In the theme, set the email explicitly, because some sections fall back to
  the store email (Gmail) when left blank.
- The store's own email and phone are in Settings → General.

### 15. Theme changes go through PRs; store data changes are logged here

24 October 2026

**Decision:**
- Theme code and template JSON change only through pull requests from a fresh
  branch off `main`.
- Store data (products, collections, menus, discounts) is changed directly in
  Shopify. Anything structural is recorded in this file.

**Why:** `main` syncs to the live theme both ways, so PRs are the review step
for theme changes. Store data has no version history. Without this log, the
reasoning behind it is lost.

### 16. Every variant tracks stock and stops selling at zero

24 October 2026

**Decision:** Every variant has **Track quantity** on and **Continue selling
when out of stock** off. On 24 October, 181 variants were changed:
- 161 were tracked but kept selling past zero;
- 17 weren't tracked at all;
- 3 were drafts set to keep selling.

**Why:** Most pieces are one of a kind. A storefront that keeps selling past
zero takes orders for pieces that are already gone.

**Known effect:** 36 products with 0 or less in stock now show "Sold out".
They include 32 of the 44 jewellery pieces, whose stock was probably never
entered. Their quantities need entering; see
[store-status.md](store-status.md#should-fix-soon).

**How to apply:** New products must keep both settings. Shopify tracks
quantity by default, but check that **Continue selling when out of stock** is
off before activating a product.

### 17. Product descriptions state only what is known

24 October 2026

**Decision:** On 24 October, drafting notes ("(confirm: …)", "[add details]",
"[please confirm …]") were removed from 31 descriptions:
- Fabric comes from the product title or variant name, which are already
  public.
- Unconfirmed details (blouse piece, length, dye type, exact weave) were
  removed, not guessed.
- Four descriptions that had lost their opening paragraph were given a short
  opening based on their title, photo and existing text.

**Why:** A wrong fabric or length on a product page is a returns and trust
problem. A missing line is not.

**How to apply:** When the client confirms a detail (blouse piece included,
5.5 m length, natural dye), add it back to that product's Details list.

### 18. Ship within India only

25 October 2026

**Decision:** The "International" shipping zone was deleted from the General
shipping profile. Only the Domestic (India) zone remains, with its six weight
bands.

**Why:**
- The shipping policy says the store ships within India only.
- The store only sells to India, so the zone was dormant.
- If international selling were ever turned on, the zone would have started
  charging a flat ₹1,800 that nobody had chosen on purpose.

**What was removed:** a flat ₹1,800 "International" rate to 28 countries.
- Europe: AT, BE, CH, CZ, DE, DK, ES, FI, FR, GB, IE, IT, NL, NO, PL, PT, SE
- Rest of world: AE, AU, CA, HK, IL, JP, KR, MY, NZ, SG, US

**How to apply:** To start shipping abroad:
1. Add the countries to a market (Settings → Markets).
2. Create a zone with rates in Settings → Shipping and delivery.
3. Update the shipping policy in the same change.

### 19. Shopify's SKU field is the product register, fed by an intake form

1 November 2026

**Superseded by #22**, which replaces the intake form and makes the shortcuts' register
the record of new products. The SKU format still applies.

**Decision:**
- The unique ID for each piece lives in its Shopify **SKU** field. No
  separate notebook or hand-kept sheet duplicates it.
- New products come in through a Google Form (one per piece) that feeds a
  Google Sheet. The sheet assigns the next SKU per category, and Sagar lists
  products from it. See adding-products.md (since removed).
- Target SKU format: `PBS-<CODE>-<NNN>`, with one code per category. This is
  confirmed once the client answers the questions in
  [sku-audit.md](sku-audit.md).

**Why:**
- The SKU already prints on packing slips and Shiprocket labels, drives admin
  search and groups inventory reports.
- A hand-kept list of IDs and links goes stale as products are renamed,
  duplicated or moved, and 338 URLs changed in October alone.
- The form also captures facts the photos can't show (fabric, length, blouse
  piece, quantity, weight), whose absence caused much of the October
  clean-up.

**Rejected:**
- *A Google Sheet of ID and product link, maintained by hand:* it's a second
  copy that drifts.
- *Carrying on with the notebook:* that's how 48 SKUs ended up shared by
  different pieces.

**How to apply:** Only the intake sheet hands out numbers. If a list is
needed, generate it from Shopify (an export or a sync app) rather than
typing it.

### 20. Heirloom is curated by tag, starting empty

1 November 2026. This supersedes the "22 products already carried the tag"
reasoning in decision 7.

**Decision:** The `#heirloom` tag was removed from all 38 products that
carried it, so the Heirloom collection starts empty. The collection keeps
its rule (tag `#heirloom`), its URL and its menu link. Pieces join it again
only when the tag is added on purpose.

**Why:** Sagar asked for the collection to be emptied without deleting or
otherwise changing the products. The tag had built up on 38 products,
including suit sets. In a smart collection, removing the tag is the only way
to take products out. Nothing else on the products was changed.

**Rejected:**
- *Replacing it with a hand-picked (manual) collection:* this would need a
  new collection and a repointed menu item.
- *Switching the rule to a new tag:* this would leave 38 stale `#heirloom`
  tags behind.

**How to apply:**
- Add `#heirloom` only to pieces that belong in Heirloom.
- Until it has stock, consider taking Heirloom out of the main menu, because
  the link currently leads to an empty page.

### 21. Dupattas are rebuilt from scratch, through the shared album

1 November 2026. This replaces the intake-form part of decision 19. The SKU
field is still the register.

**Partly superseded by #22.** The dupatta rebuild and the 4:5 photos still stand. The
album-comment workflow and `wf-` tags don't.

**Decision:**
- All 60 existing dupatta products were set to **Draft** and their SKUs
  cleared. Dupattas are being rebuilt from scratch, with SKUs restarting at
  `PBS-DUP-001`, as approved by the client.
- New products come in through the client's **shared Apple Photos album**,
  one per category, where the conversation about each piece happens. Products
  are created as drafts in the Shopify app straight from the album photos.
- Each product's status is a `wf-` tag in Shopify:
  - `wf-needs-details`
  - `wf-needs-sku`
  - `wf-needs-photos`
- Refined 4:5 photos (made in Gemini) replace the raw album photo before a
  product goes live.

**Why:**
- The store has never been live, so recreating loses nothing. The old
  dupattas had unoptimised photos and messy, partly shared SKUs anyway.
- The client already uses the album daily, so it adds no new tool for her.
- Adding photos to Shopify from the phone keeps images off Sagar's laptop,
  which is low on disk space.
- Albums can't filter or label photos, so status lives in Shopify, where admin
  views can filter by tag.

**Rejected:**
- *Google Form and sheet (decision 19):* another tool for the client to learn.
- *AirDropping photos to the laptop:* not enough disk space.
- *Deleting the old dupattas outright:* drafting keeps their record until
  the rebuild is done.

**How to apply:** Follow adding-products.md (since removed; see #22). The old
SKUs are kept in
[archive/dupattas-before-rebuild-2026-11.csv](archive/dupattas-before-rebuild-2026-11.csv),
not in Shopify. Delete the old drafts once every dupatta is rebuilt.

### 22. New products and stock changes run through Apple Shortcuts

4 November 2026. This replaces the album-comment workflow and `wf-` tags in decision 21,
and the intake form in decision 19.

**Decision:**
- The client submits products and stock changes on iPhone with Apple Shortcuts. The
  operator processes them with Shortcuts too. See
  [product-operations/](product-operations/README.md).
- Records live as small files in a shared iCloud Drive folder, one per event, with nothing
  deleted.
- Numbers shows tables rebuilt from those records on demand. It isn't where they live.
- Publication status and stock status are separate. A product can be `LIVE` and
  `OUT_OF_STOCK`.
- Shopify is still updated by hand. The shortcuts never change it.
- The shortcuts are generated by scripts in `product-ops/build/`, so they can be recreated.

**Why:**
- Both people can do everything on an iPhone, with no server or paid service.
- Duplicate SKUs are stopped at submission, and every change is logged.
- Numbers actions in Shortcuts reportedly only add rows, so a Numbers register couldn't
  check duplicates or change a status.
- One new file per event can't overwrite another during iCloud sync.

**Rejected:**
- *Numbers as the live register:* it can't be read or updated from Shortcuts, and hand edits
  wouldn't be logged.
- *A permanent shared Numbers workbook fed by Add Row:* offered on 3 November. Sagar chose
  rebuilt sheets instead.
- *`wf-` tags and `/add-products` alongside the shortcuts:* two records of the same status
  would drift. The skill, `docs/adding-products.md` and the form script were deleted. The
  listing checklist moved to
  [listing-checklist.md](product-operations/listing-checklist.md). Git history keeps the rest.

**Known effects:**
- Numbers tables are snapshots. Anything typed into them is lost at the next refresh.
- Photos search can't find SKUs in Shared Album captions, so the operator finds photos by
  submitted date.
- The register only knows products submitted through it, not older Shopify products.

**How to apply:** Change shortcuts through the scripts, not in the app. See
[building-and-signing.md](product-operations/building-and-signing.md).
