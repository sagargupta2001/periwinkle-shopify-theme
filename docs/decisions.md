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
