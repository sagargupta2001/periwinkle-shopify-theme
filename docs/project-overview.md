# Project overview

## What this is

The Shopify Online Store 2.0 theme for **Periwinkle**, a store selling clothing
and objects rooted in Indian textile traditions (sarees, salwar suits, and
miniature objects such as hand-blown glass).

The theme is a fork of **Dawn 16.0.0** (see `theme_info` in
`config/settings_schema.json`), restyled through theme settings and extended
with a handful of custom sections. The code is plain Liquid, CSS and vanilla JS.
There is no build step, no bundler, and no `package.json`.

## How changes flow

The repo is connected to the Shopify store through the **Shopify GitHub
integration** (theme `periwinkle-shopify-theme/main`):

- **Code changes** are made on a feature branch, opened as a PR against `main`,
  and merged. Shopify then pulls `main` into the connected theme.
- **Theme editor changes** made in Shopify admin (content, section order,
  settings, colours) are committed back to `main` automatically as
  `Update from Shopify for theme periwinkle-shopify-theme/main`.

Consequences:

- **Always pull before starting work.** Merchants edit JSON templates and
  `settings_data.json` in the admin, and those commits land on `main` at any
  time.
- Treat `templates/*.json`, `sections/*-group.json` and
  `config/settings_data.json` as **shared with the admin**. Keep edits to them
  minimal and targeted so they merge cleanly with admin-side commits.
- `config/settings_data.json` warns that it is auto-generated and may be
  overwritten.
- Prefer section **settings** to hard-coded content, so the merchant can change
  things without a code change.

## Running the theme locally

```bash
shopify theme dev --store periwinkle-by-sherry.myshopify.com
```

This serves the working copy at **http://localhost:9292** against live store data,
and hot-reloads CSS and section changes as you save. Useful paths:

| Page | URL |
|---|---|
| Home | http://localhost:9292/ |
| Our Story | http://localhost:9292/pages/our-story |
| A collection | http://localhost:9292/collections/sarees-benarasi-weaves |

Notes:
- The store is `periwinkle-by-sherry.myshopify.com`. The first run asks you to
  log in through the browser.
- Changes to `templates/*.json` and theme settings made **in the local editor
  preview** can be pushed back to the store. Keep local work to code and let the
  merchant own content, so the "Update from Shopify" commits stay clean.
- `shopify theme dev` creates a development theme on the store. It is not
  published, and it is removed after a period of inactivity.

## Directory map

| Path | What's there |
|---|---|
| `layout/theme.liquid` | Page shell: fonts, colour scheme → CSS variables, global scripts, header and footer groups |
| `layout/password.liquid` | Password page shell |
| `templates/*.json` | Page templates, meaning an ordered list of sections with their settings. `page.our-story.json` is custom. |
| `templates/gift_card.liquid` | Gift card page (Liquid template) |
| `sections/` | Dawn sections plus the custom `periwinkle-*` sections. `header-group.json` and `footer-group.json` define the header and footer. |
| `snippets/` | Reusable partials. Custom or heavily modified: `header-logo`, `header-mega-menu-cards`, `header-drawer` |
| `assets/` | CSS (`base.css`, `component-*`, `section-*`), JS (`global.js` plus per-feature files), SVG icons |
| `config/settings_schema.json` | Theme settings definition (adds the header wordmark settings) |
| `config/settings_data.json` | Current theme settings: colour schemes, fonts, radii, cart type… |
| `locales/` | Translations. Only `en.default*.json` has been updated for custom settings. |
| `docs/` | These docs |

## Page composition (as of 2026-09)

### Header group (`sections/header-group.json`)
1. **Announcement bar**: scheme-4 (Dusk), sticky.
2. **Header**: `main-menu`, desktop menu type **Mega menu with collection
   cards**, sticky "always", logo middle-left (centred on mobile), scheme-1.

### Footer group
- **Footer**: scheme-4, newsletter heading "Subscribe to our emails".

### Homepage (`templates/index.json`)
1. **Slideshow**: full-bleed hero, dots only.
2. **Collection list**: "Shop by Category" (centred via `custom_css`).
3. **Peri editorial slider** (`periwinkle-editorial-slider`): "The Art of
   Craft / Crafted by hand, made to last", with a carousel of craft collection
   cards.
4. **Featured collection**: "Timeless Fashion" (centred via `custom_css`).
5. **Peri miniatures** (`periwinkle-miniatures`): "Small Objects, *Beautiful
   Stories.*"
6. **Peri coming soon** (`periwinkle-coming-soon`): "Still *on the loom.*",
   previewing Bridal Trousseaus and The Cloth That Remembers, with an email
   sign-up.
7. **Image with text**: image first.
8. **Image with text**: text first. Its "Our Story" button links to
   `/pages/our-story`.

### Our Story (`templates/page.our-story.json`)
- A single **Peri story timeline** section titled "A Dream *Stitched in
  Time*", with chapter, colour swatch, list and closing blocks.
- The merchant must create a page in admin with handle `our-story` and assign
  it the `page.our-story` template.

### Product (`templates/product.json`)
Main product (sticky info, stacked gallery) → Disclosures → Related products
("You may also like").

### Collection
Collection banner → product grid.

## Key theme settings

| Setting | Value |
|---|---|
| Fonts | Cormorant (headings), DM Sans (body) |
| Page width | 1300px |
| Cart | Drawer, with notes enabled. Empty-cart collection: `ajrakh-vanaspati-dyed-in-plant-copy` |
| Animations | Reveal on scroll **off**. Hover **3D lift** |
| Corners | 4px buttons, inputs, pills, popups, badges. 0 on cards and media |
| Predictive search | On, shows price |
| Currency code | Off |
| Social links | None set |

See [design-guide.md](design-guide.md) for the full visual system.

## Store content notes

- **Menus**: `main-menu` has six top-level menus. Sarees is the only one where
  every child collection has a 4:5 poster image, so it is the only menu that
  currently renders as cards (see
  [customizations.md](customizations.md#mega-menu-with-collection-cards)).
- Collection "poster" artwork is portrait 4:5. Per-section upload sizes are in
  the [asset spec](design-guide.md#61-asset-spec).
- Miniatures section images were left unset for the merchant to upload.
