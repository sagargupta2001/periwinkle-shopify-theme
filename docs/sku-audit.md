# SKU audit

The client keeps each product's unique ID in a notebook and types it into the
SKU field when she adds a product in Shopify. This page records what that
looks like in the store today, the proposed fix, and the questions to settle
with the client before any SKU is changed.

Audited 1 November 2026 across all 553 variants (533 active, 20 draft or
archived). **No SKUs have been changed yet.**

## Why it matters

The SKU appears on order emails and packing slips, Shiprocket prints it on
shipment labels, and admin search and inventory reports use it. When two
pieces share an SKU, an order for that number is ambiguous: which piece gets
packed?

## Inconsistencies found

### 1. Different pieces share the same SKU (48 numbers, 99 variants)

This is the most serious problem. Every case is two or three **different**
products, never variants of one product. For example, `PBS-DUP-001` is on both
Kantha Kavya and the Rani Pink Banarasi Zari Dupatta. The full list:

| SKU (normalised) | Products sharing it |
|---|---|
| DUP-001 | Kantha Kavya · Rani Pink Banarasi Zari Dupatta |
| DUP-005 | The Midnight Vine Kantha Dupatta · Lavender Banarasi Zari Dupatta |
| DUP-008 | The Tree of Life Kantha Stole – Grey · Slate Grey Banarasi Dupatta |
| DUP-010 | Neelambari Kantha Stole · Peach Banarasi Dupatta |
| DUP-023 | Rangeen Paan Red Moirangphee Dupatta · Safed Tarang Emerald Ikat Dupatta |
| MIN-010 | Handblown Murano Glass Dog figurines · Hand Blown Murano Glass Fish |
| MIN-011 | Handblown Murano Glass Dog figurines · Moonlit Bamboo Mini Folding Screen |
| MIN-012 | Handblown Murano Glass Dog figurines · Handpainted Koi Fish Bud Vase |
| MIN-017 | Glass Violets · Miniature Glass Flower Bouquet in Vase |
| MIN-021 | Tiny Writer's Corner · Forest Fairy Mushrooms |
| SAR-019 | Rangbahar · Orchid Purple Batik Silk Saree |
| SAR-033 | Hamsa Naukavihar · Rust Red Floral Print Silk Saree |
| SAR-034 | Kalapahad Noir · Sea Green Floral Print Chiffon Saree |
| SAR-035 | Emerald Green Pure Cotton Paithani · Magenta Leheriya Print Chiffon Saree |
| SAR-036 | Neel Chhaya · Royal Blue Chiffon Saree with Silver Leaf |
| SAR-043 | Blush Pink Organza Suit Set · Orchid Dabu Block Print Saree |
| SAR-049 | Odisha Sambalpuri Ikat Saree (Checked Body) · Aubergine Brown Odisha Santali Saree |
| SAR-050 | Turmeric Gold Banarasi Saree · Rust & Aubergine Sambalpuri Ikat Saree |
| SAR-052 | Nilanjana · Teal Blue Silk Saree with Scattered Zari Buti · Teal Blue Handloom Benarasi-Silk Saree |
| SAR-056 | Royal Blue Zari Silk Blend Kanjeevaram · Black Kota Doria Lumbini Saree |
| SAR-059 | Peacock Blue Benarasi Saree · Steel Blue Benarasi Silk Saree · Teal Blue Silk Benarasi Saree |
| SAR-060 | Multicolor Ombré Chiffon Saree · Turquoise Benarasi Silk Saree |
| SAR-063 | Rani — Magenta Raw Mango Saree · Mustard Gold Pure Silk-Style Saree |
| SAR-092 | Violet Banarasi Silk Saree · Amethyst Purple Banarasi Katan Silk Saree |
| SAR-093 | Rajani · Royal Purple Banarasi-Style Silk Saree |
| SAR-094 | Peacock Blue Banarasi Saree with Meenakari · Neelambari — Peacock Blue Banarasi Silk Saree |
| SAR-124 | Mayura Kanchi · Cream Kasavu Handblock Print Cotton Saree |
| SAR-137 | Ivory Block-Print Cotton Saree · Ivory Lotus Fan Handblock Cotton Saree |
| SAR-154 | Bansuri Green · Forest Green Handblock Print Cotton Saree |
| SAR-218 | Orchid Jaal · Nilambari Tulip Bagh |
| SAR-227 | Nilambari: Indigo Block-Print Saree · Madder & Indigo Block Print Saree |
| SAR-258 | Untitled Jul14 (draft) · Aqua Blue Saree with Zari Floral Buttis |
| SAR-265 | Emerald Green Banarasi Silk Saree · Olive Green Saree with Silver Zari Paisley |
| SAR-276 | Violet Paisley Hand Block Print Mul Cotton Saree · Mustard Yellow Kota Silk Saree |
| SAR-293 | Kajal & Haldi · Kesar Raat |
| SKU-007 | Odisha Sambalpuri Ikat Saree (Narrative Motifs) · Sea-Glass Booti Border Dupatta · Wooden Trinket Boxes |
| SKU-029 | Charcoal Chitrakathi Dupatta · Smoke & Chikankari Kurta Set |
| SKZ-024 | Pink Chikankari Kurta with Keyhole Neckline · Rani Bloom Bandhani Kurta Set |
| SKZ-035 | Purple Parrot Motif Suit Set · Tota Tales Lavender Kurta Set |
| SKZ-041 | White Kota Doria Suit Set · Chikan Bloom |
| SKZ-047 | Mul Chanderi Pichwai Suit Set · Lotus Pond Ivory Kurta Set |
| SKZ-061 | Beige Mirror Work Suit Set · Wheat Kantha Kurta Set |
| SKZ-062 | Neelam Zaari Organza Suit Set · Nilaya Teal Zardozi Suit Set |
| SKZ-100 | Teal Blue Floral Embroidered Suit Set · Teal Reverie |
| SKZ-104 | White Chikankari Kurta with Kutch Mirror Work · Banjara Bloom Kurta Set |
| SKZ-132 | The Royal Kimkhab – Grey Edit · The Royal Kimkhab – Brick Red Edit |
| SKZ-139 | Nilaya Vine-Embroidered Kurta Set · Citron Bloom Straight Suit |
| SKZ-150 | Red Kota Suit Set · White and Pink Poppies |

Many pairs are near-identical designs in different colours (the Royal
Kimkhab Grey and Brick Red Edits, the Banarasi dupattas, the teal Benarasi
sarees). The notebook number may sometimes stand for a design or a purchase
lot rather than a single piece. See question 1 below.

### 2. Missing SKUs (84 variants, 68 of them active)

| Product type | Active variants with no SKU |
|---|---|
| Saree | 35 |
| Dupatta | 13 |
| Unstitched Salwar Suit | 10 |
| European earrings | 6 |
| Miniature | 3 |
| Bag | 1 |

16 of the missing ones are new "(Copy)" listings. Duplicating a product in
Shopify clears the SKU, and it wasn't filled in again.

### 3. Seven different ways of writing the same format

Only about 1 in 7 SKUs is written in a single consistent style. Examples of what's in the
store:

- `PBS/SAR/092`, `PBS-SAR-013`, `pbs/sar/020`, `PBS/Sar/117`
- spaces in the middle: `pbs /sar/271`, `PBS/sar /302`, `PBS - sar- 041`,
  `PBS-sku- 083`
- separators mixed in one SKU: `PBS/SAR-255`

Counts: 341 use hyphens and 130 use slashes. 189 have lowercase letters and
31 contain spaces.

### 4. The letter O typed instead of zero (39 SKUs)

All the `USS` suit SKUs from 004 to 074 use the letter O: `PBS-USS-OO4`,
`PBS-USS-O07`, `PBS-USS-O20`. They look right but won't match a search for
`PBS-USS-004`. Correcting them creates two more clashes, because `USS-017`
and `USS-030` would then each appear twice.

### 5. A price typed into an SKU

`PBS-SAR-160-4850,7500` has what look like two prices appended.

### 6. More than one code per category, and codes that don't match the product

| Category | Codes in use |
|---|---|
| Sarees | SAR (211), plus 2 sarees coded SKZ and 1 coded SKU |
| Dupattas | DUP (29), plus 14 coded SKU and 1 coded SAR |
| Suits | SKZ (78), USS (48), SKR (1), plus 6 coded SKU and 1 coded SAR |
| Jewellery | EPJ (32), JEW (9) |
| Miniatures | MIN (24), plus 3 coded SKU |
| Home decor | CMS (10) |
| Other | 2 SKUs start `SKU-` instead of `PBS-`, and 25 coded products have no product type |

`SKU` is used as if it were a category, on 26 products of five different
types.

### 7. Numbers that jump or look mistyped

- Suits (SKZ) run 001–230, then `PBS-SKZ-1850`. That's probably 185 or 150.
- Sarees (SAR) run up to 302, then jump to 407 and 408.

### 8. Related product data problems

- "Midnight Navy Hand-Painted Pattachitra Saree" has the product type
  **Dupatta**.
- 25 products with SKUs have no product type at all.

## Proposed solution

1. **The SKU field in Shopify is the register.** It replaces the notebook;
   no separate list is kept by hand.
2. **One format: `PBS-<CODE>-<NNN>`.** Uppercase, hyphens, no spaces, and at
   least three digits (`PBS-SAR-092`).
3. **One code per category.** Codes marked *confirmed* come from the client
   (1 Nov). The rest are proposals still to be confirmed.

   | Code | Category | Status |
   |---|---|---|
   | SAR | Saree | Confirmed |
   | SKZ | Salwar kameez (suit sets). Replaces USS, and SKR, which is a misspelling. | Confirmed |
   | RED | Readymade | Confirmed (no products use it yet) |
   | MIN | Miniatures | Confirmed |
   | GIFT | Gifts | Confirmed (no products use it yet) |
   | DUP | Dupatta / stole | Proposed |
   | EPJ | Jewellery (would absorb JEW) | Proposed |
   | CMS | Home decor / ceramics | Proposed |
   | BAG | Bag / accessory | Proposed |

   `PBS` stands for Periwinkle by Sherry.

4. **Every number is used once, for one piece.**
5. **Clean-up:**
   - **Automatic** (no client input needed): fix the format and case, and
     change the letter O to zero.
   - **USS and SKR become SKZ** (confirmed by the client). This can't be a
     plain rename. 20 USS numbers already exist as SKZ numbers on different
     suits (for example, PBS-USS-030 Ivory Azure Bloom and PBS-SKZ-030
     Chikankari Parinda), and USS also clashes with itself on 017, 030 and
     084. Those 23 suits need new SKZ numbers, and the notebook needs the
     old-to-new list. Decided on 1 Nov: do this as part of the full clean-up,
     not on its own.
   - **Needs the client:** decide which piece keeps each of the 48 shared
     numbers (the other gets a new number), confirm the IDs for the 68 missing
     ones, and confirm the SKZ-1850 outlier and the price-in-SKU case.
   - **New numbers continue from the highest number in each category.** That
     number goes into the intake form's "SKU counters" tab.
6. **From then on:** new products come in through the intake form, which
   assigns the next number automatically. See
   [adding-products.md](adding-products.md).

The automatic part should only run after the client has answered the
questions below, because her answers may change the code list or the meaning
of a number.

## Answers from the client (1 November)

- **Codes:** `PBS` = Periwinkle by Sherry, `SAR` = saree, `RED` =
  readymade, `MIN` = miniatures, `GIFT` = gifts, `SKZ` = salwar kameez.
- **USS and SKR** should both become SKZ. SKR is a misspelling.
- **The number is the next free number in her notebook.** It isn't a supplier
  or bill reference, so the intake form's per-category counter can take over
  from the notebook.

Still open: questions 1 and 4–7 below, and the codes not yet explained (DUP,
EPJ, JEW, CMS, and "SKU" used as a code).

New questions from the answers:

- **GIFT and RED:**
  - Is GIFT a category of its own (pieces sold only as gifts), or a code for
    things like miniatures that are also in the Gifting menu? Gift-worthiness
    is currently a tag, not a category.
  - Which products count as readymade (RED), as opposed to SKZ suit sets?
    Once confirmed, both codes get added to the intake form.

## Questions for the client

1. **Is a notebook number meant to be one physical piece, or can it cover a
   design that comes in several colours, or a purchase lot?** About a third
   of the shared numbers look like colour variants of one design.
2. **What do the codes mean, and are they all still in use?** Specifically:
   - SKZ vs USS vs SKR for suits;
   - EPJ vs JEW for jewellery;
   - "SKU" used as a code.
3. **Where does the notebook number come from?** Is it the next free number
   in each category, a supplier or purchase reference, or something else? If
   it's a supplier reference, it may be worth storing separately from the SKU.
4. **For the 48 shared numbers, which piece is the notebook entry actually
   for?** The other piece gets a new number.
5. **Do the 68 products without an SKU have notebook entries?**
6. **Is `PBS-SKZ-1850` a typo, and what is `-4850,7500` on `PBS-SAR-160`?**
7. **Does any SKU already appear somewhere outside Shopify** (supplier
   bills, Shiprocket, an accounting tool) that would need updating too?
