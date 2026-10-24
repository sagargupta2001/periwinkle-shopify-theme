# Store status

A living snapshot of the Periwinkle store: what is still open before and after
launch, and how the store is set up today. Rewrite it as things change. For
*why* the store is set up this way, see [decisions.md](decisions.md).

Last updated: 25 October 2026. The store is still behind its password page.

## Open items

Tick an item when it's done and leave it for one update so the change is
visible, then delete it. Add new items with an owner and the date added.

### Blocking launch

- [ ] **Product weights.** Every variant weighs 0 kg, so every order pays the
      ₹249 minimum and Shiprocket can't book couriers. Waiting on average
      weights for sarees, dupattas and miniatures, which will be applied in
      bulk. Owner: Sagar. Added 24 Oct.
- [ ] **Policy placeholders.** Contact, Legal notice, Privacy and Terms still
      contain `[GSTIN]`, `[Registered address]`, `[Business type]` and
      `[Days and hours]`. Fill them in under Settings → Policies. Owner:
      client. Added 24 Oct.
- [x] **Store contact settings.** Settings → General now shows
      `support@periwinklebysherry.com` and +91 99726 95620 (done 25 Oct).
      Owner: client. Added 24 Oct.
- [ ] **Shipping location address.** "Shop location" has no address.
      Shiprocket uses it as the pickup point, and it matters for GST. Set it
      in Settings → Locations. Owner: client. Added 24 Oct.
- [ ] **Enter real stock for 36 sold-out products.** Every variant now stops
      selling at zero (see [decision 16](decisions.md#16-every-variant-tracks-stock-and-stops-selling-at-zero)),
      so these show "Sold out" until their quantity is entered in Products →
      Inventory. That includes **32 of the 44 jewellery pieces**, so the home
      page's "Explore Jewellery" links lead to a mostly sold-out collection.
      Grey Moirangphee Cotton Saree is at −1, which means it was oversold
      once. Owner: client. Added 24 Oct.
  - Ceramics: Blue & White Indian Cityscape Wall Plate; Japanese-Style Ceramic
    Dipping Bowl Set
  - Sarees: Grey Moirangphee Cotton Saree; Rust Red Hand Block Printed Cotton
    Saree with Floral Buta
  - Necklaces: Blue Ombre Square Link Pendant; Emerald & Navy Ombre and Sunset
    Ombre Multi-Strand Seed Bead
  - Ring: Silver Dual Rectangle Cabochon Open Ring
  - 28 earrings: every European earring except the handful that already had
    stock. The list is under Products, filtered by type "European earrings"
    and "Availability: Out of stock".
- [ ] **End-to-end test order.** See [Test order](#test-order) below. Owner:
      Sagar and client. Added 24 Oct.

### Should fix soon

- [x] **Copied descriptions (renamed copies).** On 24–25 Oct, the 6 renamed
      copies and the 11 Pattachitra dupattas got their own descriptions,
      written from their photos following
      [decision 17](decisions.md#17-product-descriptions-state-only-what-is-known).
      Owner: Sagar. Added 24 Oct.
- [ ] **More products sharing one description.** A full scan on 25 Oct found
      12 more groups (27 products) with identical descriptions. Most look like
      pieces listed by copying another product, so the text may describe a
      different piece. Owner: client. Added 25 Oct.
  - **Neel Kamal: Periwinkle Floral Saree with Ivory Procession Pallu** is
    listed twice, with the same title and description. This is a new
    duplicate; draft one of them.
  - Pattachitra Dupatta in Cotton – Rust Red Colour · in Chanderi Silk – Blue
    with Single Dancer motif · in Chanderi Silk – Black. The two Chanderi
    pieces carry the cotton dupatta's text.
  - Handblock Print On Cotton – Greyish green and Blue · Pink and Violet ·
    Yellow and Teal
  - Kantha Kavya · Suchimarga · The Cloth That Remembers
  - Mashru Ivory Kurta Set · Rosewater — Ivory Kurta Set
  - Dark Purple and Teal Kasuti Embroidered Cottonsilk Sarees
  - Miniature Glass Flower Bouquet in Vase (two listings)
  - Monochrome Paisley — Ivory Kurta Set · Banjara Bloom — White Kurta Set
  - Emerald Vine — Tissue Silk Saree · Magenta Kairi — Handloom Cotton Saree
  - Ivory Gajmala Saree · Teal Rajahamsa Saree
  - Kaala Rani Ikat Dupatta · Gajayatra off-White Kalamkari Dupatta
  - Japanese-Style Ceramic Dipping Bowl Set · Blue & White Indian Cityscape
    Wall Plate
- [ ] **Drafted listings need photos.** These 9 were set to draft because they
      had no image or duplicated another listing. Add photos and re-activate,
      or leave them as drafts. Owner: client. Added 24 Oct.
  - Pattachitra Dupatta in Chanderi Silk (Copy), black
  - Hand Enamelled Twist Drop Earrings (Copy)
  - Sage Green Pure Mul Cotton Unstitched Salwar Suit Material (Copy)
  - Banjara Bloom — White Kurta Set with Kutch-Embroidered Yoke (second listing)
  - Pattachitra Dupatta in Cotton - Rust Red Colour (Copy)
  - Blue Tulip Glass Drop Earrings (Copy)
  - Aubergine Odisha Handloom Silk Saree (Copy). It is priced ₹14,000 against
    the original's ₹17,500, so it may be a real second piece.
  - Forest Green Block-Printed Saree (Copy)
  - Handblown Murano-Style Glass Angelfish Figurines (identical duplicate; the
    live listing has 5 in stock)
- [ ] **App screenshots used as product photos.** These show a shopping app's
      buttons or size labels: the Teal Marbled necklace, the Pastel Patchwork
      studs, the Cloisonné Keepsake Pot and the Vintage Steel Kettle Miniature.
      The **Layered Multi-Hoop Pendant Necklace** photos are screenshots from
      the Temu app, with the app's logo and "Add to cart" button visible.
      Replace them before launch. Owner: client. Added 24 Oct.
- [ ] **Check names and facts given from photos.** These were named and
      described from their photos. On 25 Oct, three names were corrected after
      a closer look: Mustard Yellow "with Lotus Pond" (was "with Painted
      Border"), Cerulean Blue "with Tree and Peacocks" (was "Swans"), and
      **Blue Poppy Print** Rectangular Drop Earrings (was "Blue Floral Glass";
      they look printed, not glass). Old URLs redirect. Owner: client.
      Added 24 Oct.
  - Check the names of the 11 Pattachitra dupattas, the Layered Multi-Hoop
    Pendant Necklace and the Teal Enamel Open-Loop Drop Earrings.
  - **Classic Black & White — Warli-Style Print / — Leaf Buti Print:** is each
    a saree or a suit set? Both have no product type, so they don't appear
    in any type-based collection.
  - **Layered Multi-Hoop Pendant Necklace:** are the earrings in the photos
    included? The description currently says "Pictured with matching
    earrings".
- [ ] **Products without a description.** 63, including every miniature.
      Owner: client. Added 24 Oct.
- [x] **International shipping zone.** Deleted on 25 Oct; see
      [decision 18](decisions.md#18-ship-within-india-only). Owner: Sagar.
      Added 24 Oct.
- [ ] **Order email delivery.** The domain's SPF record only authorises
      GoDaddy (Microsoft 365 mail). Add Shopify's sender-email DNS records so
      order emails from `support@` don't land in spam. Owner: client.
      Added 24 Oct.
- [ ] **"Milano glass" in the journal article** "Jewellery India Hasn't Seen
      Yet". The well-known glass is Murano; confirm which was meant. Owner:
      client. Added 24 Oct.

### Launch day

- [ ] Switch Razorpay from test mode to live (Settings → Payments).
- [ ] Remove the storefront password (Online Store → Preferences).
- [ ] Place one small live order and refund it.

### Test order

Run this while Razorpay is still in test mode. It needs the storefront
password, and a person has to place it.

1. Buy something cheap, such as Small Floral Tin Boxes (₹150), with a Razorpay
   test card or `success@razorpay` as the UPI ID.
2. Check that the order and confirmation email arrive and the payment shows
   as captured.
3. In Shiprocket, check that the order synced with a sensible weight and
   shipping charge. Cancel the label instead of booking a pickup.
4. Mark the order fulfilled and check the tracking email.
5. Refund it to store credit, then sign in at checkout with the same email
   and confirm the credit appears as a payment option.
6. Archive the test order.

## How the store is set up

### Catalogue

- 501 active products and 21 drafts.
- Every variant tracks its quantity and stops selling at zero, so a product
  shows "Sold out" once nothing is available (on hand minus committed).
- The product type drives collections. The types are Saree, Dupatta,
  Unstitched Salwar Suit, Miniature, Ceramics, Wooden Antique Box, Bag, and
  European earrings/necklace/ring.
- Every product's URL handle is built from its title. Old `-copy` and
  `untitled-…` handles redirect (301) to the new ones.

### Collections

Automated (smart) collections update themselves. Manual ones need products
added by hand.

| Collection | Handle | Type | Rule or note | Products |
|---|---|---|---|---|
| Periwinkle Sarees | `periwinkle-sarees` | Manual | Manual sort order; add new sarees by hand | 218 |
| Periwinkle Salwar Suit Sets | `periwinkle-salwar-suit-sets` | Manual | | 123 |
| The Block Print Edit | `the-block-print-edit` | Manual | | 99 |
| Looms of Kashi – The Benaras Edit | `threads-of-benaras` | Smart | tag `#benarasisilk` | 71 |
| Periwinkle Dupattas | `frontpage` | Manual | Dawn's default handle, kept | 54 |
| Periwinkle Jewellery | `periwinkle-jewellery-india-hasn-t-seen-yet` | Manual | | 44 |
| Periwinkle Miniatures | `periwinkle-miniatures` | Manual | Add new miniatures by hand | 27 |
| Periwinkle Couture | `periwinkle-couture` | Manual | | 11 |
| Periwinkle Home Decor | `periwinkle-ceramics` | Manual | | 10 |
| Periwinkle Accessories | `accessories-bags` | Manual | Hidden from menus | 1 |
| Heirloom | `heirloom` | Smart | tag `#heirloom` | 23 |
| Hand-Blown Glass Miniatures | `miniatures-hand-blown-glass-decor-items` | Smart | type Miniature + tag `#glass` | 9 |
| Wooden Miniatures | `miniatures-wooden` | Smart | type Miniature + tag `#wooden` | 9 |
| Porcelain Miniatures | `miniatures-porcelain` | Smart | type Miniature + tag `#porcelain` | 2 |
| Gifting | `gifting` | Smart | tag `gift` | 281 |
| Gifts Under ₹1,000 | `gifts-under-1000` | Smart | tag `gift`, price < 1001 | 80 |
| Gifts Under ₹3,000 | `gifts-under-3000` | Smart | tag `gift`, 1000 < price < 3001 | 129 |
| Gifts Under ₹5,000 | `gifts-under-5000` | Smart | tag `gift`, 3000 < price < 5001 | 72 |

### Menus

- **Main menu:** Sarees · Dupattas & Stoles · Home Decor · Heirloom ·
  Miniatures · Gifting (Gifts under ₹1,000 / ₹3,000 / ₹5,000).
- **Footer — Shop:** Miniatures · Sarees · Dupattas & Stoles · Home Decor ·
  Gifting.
- **Footer — Help:** Shipping & Delivery · Returns & Refunds · Privacy Policy ·
  Terms of Service. Each links to its policy page.
- **Footer — Explore:** Our Story · Blogs · Contact Us · Community.

### Shipping

One profile, shipped from "Shop location".

| Zone | Order weight | Rate |
|---|---|---|
| Domestic (India) | 0–0.5 kg | ₹249 |
| | 0.5–1 kg | ₹299 |
| | 1–1.5 kg | ₹349 |
| | 1.5–2 kg | ₹399 |
| | 2–3 kg | ₹449 |
| | over 3 kg | ₹499 |

### Discounts

- **Free shipping on orders of ₹10,000 and above:** automatic, active since
  24 October 2026. It combines with product and order discounts.

### Payments, fulfilment and accounts

- **Payments:** Razorpay, prepaid only, no cash on delivery. It is believed to
  be in test mode; confirm in Settings → Payments.
- **Fulfilment:** the Shiprocket app is installed. Shipping rates come from
  Shopify, not from Shiprocket.
- **Customer accounts:** the newer customer accounts, with guest checkout
  allowed. This supports store credit, which change-of-mind returns are
  refunded as under the refund policy.
- **Taxes:** prices include GST, and shipping is not taxed.

### Contact details

Use these everywhere customers see them:

| Detail | Value |
|---|---|
| Email | support@periwinklebysherry.com |
| Phone / WhatsApp | +91 99726 95620 |
| Returns address | Saveri Mohanty, Villa #6, Palm Meadows Extension, Adarsh Palm Meadows, Ramagodanahalli, Varthur Main Road, Whitefield, Bengaluru 560066 |
| Grievance Officer | Saveri Mohanty |

The theme shows them in the footer, the mobile menu drawer, the Contact page
and the community page.
