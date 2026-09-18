# Periwinkle design guide

The visual language of the Periwinkle storefront: colour, type, spacing, shape,
motion and the patterns the custom sections share. Use it when building a new
section or changing an existing one so the site keeps reading as one brand.

**Where the values live.** Nearly everything here is set in the theme editor and
saved to [`config/settings_data.json`](../config/settings_data.json). Custom
sections take their own colours from section settings, and their defaults are
listed below. If this guide and `settings_data.json` ever disagree, the JSON is
what the live site uses. Update this guide to match it.

---

## 1. Brand character

Periwinkle sells clothing and objects rooted in Indian textile traditions (the
store's own brand line is *"Thoughtfully crafted clothing and objects rooted in
Indian textile traditions, made for a contemporary way of living."*). The design
follows from that:

- **Editorial, not promotional.** Big serif headlines, small spaced-out
  eyebrows, plenty of warm negative space, and underlined text links in place of
  loud buttons.
- **Warm and natural.** Off-white and linen grounds, never pure white. Ink-plum
  text, never pure black. Colour comes from plants: periwinkle, leaf and sage.
- **Crafted and quiet.** Square-ish corners (4px), no drop shadows, hairline
  borders, portrait 4:5 photography, and slow, gentle motion.

---

## 2. Colour palette

### 2.1 Core palette

The names are working labels used in this guide. They are not official brand
names.

| Swatch | Name | Hex | RGB | Role |
|---|---|---|---|---|
| ![](https://placehold.co/24x24/FAF8F3/FAF8F3.png) | **Ivory** | `#FAF8F3` | 250, 248, 243 | Default page background (scheme 1). Light text on dark schemes. |
| ![](https://placehold.co/24x24/2E2C35/2E2C35.png) | **Ink** | `#2E2C35` | 46, 44, 53 | All body and heading text on light grounds. Dark shadow colour. |
| ![](https://placehold.co/24x24/4F4A70/4F4A70.png) | **Dusk Periwinkle** | `#4F4A70` | 79, 74, 112 | Primary brand colour: buttons, links, accents, eyebrows, the announcement bar and the footer. |
| ![](https://placehold.co/24x24/EEE9DF/EEE9DF.png) | **Linen** | `#EEE9DF` | 238, 233, 223 | Background for editorial sections (craft slider, miniatures, Our Story). Image placeholder fill. |
| ![](https://placehold.co/24x24/E8E6F2/E8E6F2.png) | **Lavender Mist** | `#E8E6F2` | 232, 230, 242 | Soft periwinkle-tinted background (scheme 2). |
| ![](https://placehold.co/24x24/65735B/65735B.png) | **Sage** | `#65735B` | 101, 115, 91 | Secondary accent: sage buttons (scheme 3) and sage background (scheme 5). |

### 2.2 Botanical accents (Our Story page)

Used by the growing-periwinkle illustration in
[`periwinkle-story-timeline`](../sections/periwinkle-story-timeline.liquid).

| Swatch | Name | Hex | Role |
|---|---|---|---|
| ![](https://placehold.co/24x24/8B87D0/8B87D0.png) | **Bloom** | `#8B87D0` | Petals. The CSS derives `--story-bloom-deep` (darkened 18) and `--story-bloom-light` (lightened 16) from it. |
| ![](https://placehold.co/24x24/6E9A73/6E9A73.png) | **Leaf** | `#6E9A73` | Stem and leaves. Derives `--story-stem-deep` (darkened 14) and `--story-stem-light` (lightened 18). |
| ![](https://placehold.co/24x24/F7E27C/F7E27C.png) | **Pollen light** | `#F7E27C` | Flower centre, start of the gradient. |
| ![](https://placehold.co/24x24/E8BF3F/E8BF3F.png) | **Pollen deep** | `#E8BF3F` | Flower centre, end of the gradient. |
| ![](https://placehold.co/24x24/FFFFFF/FFFFFF.png) | White | `#FFFFFF` | Flower highlight only. |

### 2.3 Story swatches (content colours)

These are editorial content set in the "Colour swatches" block on the Our Story
page. They are not UI colours, so don't use them for interface elements.

| Swatch | Label on site | Hex |
|---|---|---|
| ![](https://placehold.co/24x24/D9A21B/D9A21B.png) | Turmeric | `#D9A21B` |
| ![](https://placehold.co/24x24/6F8193/6F8193.png) | Monsoon sky | `#6F8193` |
| ![](https://placehold.co/24x24/B8323F/B8323F.png) | A bride's laughter | `#B8323F` |

### 2.4 Colour schemes

Dawn applies colour through five **colour schemes** (Theme settings > Colors).
Each section picks one, and [`layout/theme.liquid`](../layout/theme.liquid)
turns it into CSS variables on `.color-scheme-N`.

| Scheme | Background | Text | Button bg | Button label | Secondary button / link | Shadow | Use it for |
|---|---|---|---|---|---|---|---|
| **scheme-1** *(default, `:root`)* | Ivory `#FAF8F3` | Ink `#2E2C35` | Dusk `#4F4A70` | `#FFFFFF` | Dusk `#4F4A70` | `#000000` | Most pages and sections, header, cart, cards |
| **scheme-2** | Lavender Mist `#E8E6F2` | Ink | Dusk | `#FFFFFF` | Dusk | Dusk | Soft highlighted bands |
| **scheme-3** | Linen `#EEE9DF` | Ink | Sage `#65735B` | `#FFFFFF` | Sage | Sage | Earthy bands, **sold-out badge** |
| **scheme-4** | Dusk `#4F4A70` | Ivory | Ivory | Dusk | Ivory | Ink | **Announcement bar, footer, sale badge** |
| **scheme-5** | Sage `#65735B` | Ivory | Ivory | Sage | Ivory | Ink | Dark sage bands (see contrast note) |

Where each scheme is used today:

- scheme-1: header, header menu, cart, product, collection and blog cards, the
  password page, and every stock homepage section.
- scheme-4: announcement bar, footer, sale badge.
- scheme-3: sold-out badge.
- scheme-2 and scheme-5 are defined but no section currently uses them.

### 2.5 CSS variables from a scheme

Scheme values are stored as **bare RGB triplets** so you can control opacity:

```css
color: rgb(var(--color-foreground));               /* solid */
border-color: rgba(var(--color-foreground), 0.08); /* hairline */
```

| Variable | Comes from |
|---|---|
| `--color-background` | background |
| `--gradient-background` | background gradient, or background |
| `--color-foreground` | text |
| `--color-background-contrast` | background, darkened 25 (light) or lightened (dark) |
| `--color-button` / `--color-button-text` | button / button label |
| `--color-secondary-button` | background |
| `--color-secondary-button-text`, `--color-link` | secondary button label |
| `--color-shadow` | shadow |
| `--color-badge-foreground` / `-background` / `-border` | text / background / text |

Body copy is drawn at **75% opacity** of the text colour
(`rgba(var(--color-foreground), 0.75)`). Headings use the full colour.

### 2.6 Opacity conventions

| Value | Used for |
|---|---|
| `0.75` | Body text (Dawn default) |
| `0.72` | Muted text on the Our Story page (`--story-muted`) |
| `0.85` | Descriptions in the editorial slider |
| `0.7` | Eyebrows in the editorial slider, hover dimming on text links |
| `0.18` | Timeline spine and dividers (`--story-line`) |
| `0.08` | Hairline borders (disclosures, dividers) |
| `0.08–0.10` | Decorative botanical illustration watermark |

### 2.7 Contrast (WCAG 2.x)

| Pair | Ratio | Result |
|---|---|---|
| Ink on Ivory | 12.95 | AAA |
| Ink on Linen | 11.36 | AAA |
| Ink on Lavender Mist | 11.15 | AAA |
| Body text (Ink at 75%) on Ivory | 5.94 | AA |
| Body text (Ink at 75%) on Linen | 5.53 | AA |
| White on Dusk (primary button) | 8.25 | AAA |
| Dusk on Ivory (links, accent) | 7.77 | AAA |
| Dusk on Linen | 6.82 | AA |
| Ivory on Dusk (scheme 4) | 7.77 | AAA |
| Body text (Ivory at 75%) on Dusk | 5.19 | AA |
| White on Sage (scheme 3 button) | 5.05 | AA |
| Ivory on Sage (scheme 5 headings) | 4.76 | AA |
| ⚠️ Sage on Linen (scheme 3 secondary button or link) | 4.18 | **Fails AA for body-size text.** Passes for large text (18.66px bold or 24px and up). |
| ⚠️ Body text (Ivory at 75%) on Sage (scheme 5) | 3.47 | **Fails AA.** Don't set paragraph copy on scheme 5 without raising the text opacity. |
| ⚠️ Bloom or Leaf on Linen | about 2.7 | Decorative only. Never use for text. |

---

## 3. Typography

### 3.1 Typefaces

| Role | Font | Shopify handle | Weight | Notes |
|---|---|---|---|---|
| **Headings** | **Cormorant** (serif) | `cormorant_n4` | 400 | High-contrast display serif. Custom sections also load the **italic** for emphasis (Dawn only loads the upright). |
| **Body and UI** | **DM Sans** (geometric sans) | `dm_sans_n4` | 400, bold = 700 | Regular, bold, italic and bold italic are all loaded. |

Both are served from Shopify's font CDN with `font-display: swap`.

CSS variables: `--font-heading-family`, `--font-heading-weight`,
`--font-body-family`, `--font-body-weight`, `--font-body-weight-bold`.
Scale: `heading_scale` 100 and `body_scale` 100, so no scaling is applied.

> **Italic emphasis is a signature move.** Headlines put the emotional phrase in
> Cormorant italic with `<em>`, for example *Small Objects, <em>Beautiful
> Stories.</em>* and *A Dream <em>Stitched in Time</em>*. A section that uses it
> must load the italic face itself:
>
> ```liquid
> {%- assign heading_font_italic = settings.type_header_font | font_modify: 'style', 'italic' -%}
> {%- if heading_font_italic -%}{{ heading_font_italic | font_face: font_display: 'swap' }}{%- endif -%}
> ```

### 3.2 Base scale (Dawn, `assets/base.css`)

The root font size is 62.5%, so **1rem = 10px**.

| Class | Mobile | Desktop (≥750px) |
|---|---|---|
| `.hxxl` | `clamp(56px, 14vw, 72px)` | same |
| `.hxl` | 50px | 62px |
| `.h0` | 40px | 52px |
| `h1` / `.h1` | 30px | 40px |
| `h2` / `.h2` | 20px | 24px |
| `h3` / `.h3` | 17px | 18px |
| `h4` / `.h4` | 15px | 15px |
| `h5` / `.h5` | 12px | 13px |
| Body | 15px | 16px |

### 3.3 Editorial scale (custom sections)

The custom sections use a larger, fluid display scale on top of the base scale.

| Element | Size | Line height | Tracking | Other |
|---|---|---|---|---|
| **Hero display** (Our Story) | `clamp(4.4rem, 5vw + 2rem, 9.6rem)` | 1 | -0.015em | `text-wrap: balance` |
| **Section display** (Miniatures) | `clamp(4rem, 3.2vw + 1.6rem, 6.4rem)` | 1.02 | -0.01em | |
| **Section heading** (Craft slider) | `clamp(3.2rem, 4vw, 5rem)` | 1.05 | | |
| **Card title** | `clamp(2rem, 2.4vw, 3rem)` | | | Cormorant |
| **Pull intro** | `clamp(2rem, 0.8vw + 1.7rem, 2.6rem)` | 1.45 | | Cormorant *italic*, muted, max 44ch |
| **Eyebrow** | 1.2rem (12px) | 1.2–1.4 | **0.16–0.2em** | UPPERCASE, weight 500, accent colour |
| **Body, editorial** | 1.5–1.6rem | **1.65–1.7** | 0.01em | max-width 42ch |
| **Text link / CTA** | 1.4rem | 1.4 | 0.06em | weight 500, 1px underline border, arrow → |
| **Micro label** (scroll cue) | 1.1rem | | 0.24em | UPPERCASE, muted |

**Rules of thumb**
- Headings: Cormorant with tight leading (1–1.05) and slight negative tracking
  at display sizes.
- Eyebrows: DM Sans, small, uppercase, widely tracked, in the accent colour
  (Dusk).
- Paragraphs: DM Sans with generous leading (1.65+) and a line length kept
  near 42–44ch.

---

## 4. Layout and spacing

### 4.1 Global settings

| Setting | Value | Variable |
|---|---|---|
| Page width | **1300px** | `--page-width: 130rem` |
| Space between template sections | **48px** desktop, **34px** mobile (70%) | `--spacing-sections-desktop` / `-mobile` |
| Grid horizontal gap | **24px** | `--grid-desktop-horizontal-spacing` |
| Grid vertical gap | **32px** | `--grid-desktop-vertical-spacing` |

### 4.2 Breakpoints

These are Dawn's breakpoints, and custom code must reuse them:

| Name | Query |
|---|---|
| Mobile | `max-width: 749px` |
| Tablet | `min-width: 750px` and `max-width: 989px` |
| Desktop | `min-width: 990px` |
| Wide | `min-width: 1200px` (occasional) |

### 4.3 Section padding

Stock sections take `padding_top` and `padding_bottom` settings, applied at 75%
on mobile. The rhythm in use:

| Context | Top / bottom |
|---|---|
| Stock homepage bands | 64 / 64 |
| Shop by Category | 48 / 64 |
| Craft slider | 64 / 64 |
| **Miniatures** (feature band) | **88 / 88** |
| **Our Story** hero page | **96 / 120** |
| Product main / related | 36 / 12, 36 / 28 |
| Collection grid | 36 / 36 |
| Footer | 36 / 36 |
| Header | 0 / 0 (the logo lockup sets the height) |

Rule: the more editorial the section, the more air it gets.

### 4.4 Spacing values seen in custom CSS

The custom CSS mostly uses multiples of 4px (0.4rem):
`0.6 · 0.8 · 1.2 · 1.6 · 2 · 2.4 · 2.8 · 3.2 · 4 · 4.8 · 5.6 · 8` rem.
Typical uses: eyebrow to heading 1.6–2rem, heading to body 2–2.4rem, body to CTA
3–3.2rem, and content to gallery columns 4.8rem.

### 4.5 Editorial grid patterns

- **Copy + media split** (Craft slider): `minmax(280px, 0.8fr) minmax(0, 1.7fr)`
  with a 48px gap, and the copy capped at 440px. It stacks below 990px.
- **Asymmetric gallery** (Miniatures): copy beside five objects, one of them
  featured. The desktop grid uses 12 equal rows so the columns stagger. On
  tablet the featured card spans full width above a 2×2 grid. On mobile the
  cards stack with a left/right stagger.
- **Vertical timeline** (Our Story): the spine runs down the centre on desktop
  and chapters alternate sides. On mobile the spine moves to the left edge.

---

## 5. Shape, borders and elevation

The look is flat: **4px corners, 1px borders, and no shadows anywhere.**

| Component | Border | Radius | Shadow |
|---|---|---|---|
| Buttons | 1px, 100% opacity | **4px** | none |
| Inputs | 1px, 100% | **4px** | none |
| Variant pills | 1px, 100% | **4px** | none |
| Popups | 1px, 100% | **4px** | none |
| Drawers | 1px, 100% | — | none |
| Badges | — | **4px** (bottom-left position) | — |
| Product, collection and blog cards | none | **0** | none |
| Text boxes | none | 0 | none |
| Media | none | 0 | none |

Card style is **Standard**, not Card: the image has no frame, text is
left-aligned below it, the card uses scheme-1, and the image padding is 0.

**Exceptions**
- Circles are used for round icon controls (the slider arrows, 46px, or 42px on
  mobile), colour swatches (64px), and the timeline flower nodes.
- The story swatches have a ring: `box-shadow: 0 0 0 .5rem bg, 0 0 0 .6rem line`.
- Mega menu cards and miniatures have edge fades rather than shadows.

---

## 6. Imagery

**Portrait 4:5 is the house ratio.** It carries the fashion-editorial language
and is used for collection posters, craft slider cards, mega menu cards, story
images and most miniatures. Wide 16:9 is for full-bleed banners only, and 3:2
for blog and editorial photography.

### 6.1 Asset spec

"Upload" is what to hand the merchant or the AI generator. "What the theme does"
is how that file is actually displayed, which is the part that decides where the
crop falls.

| Section / asset | Upload | Example size | What the theme does with it |
|---|---|---|---|
| **Homepage hero (slideshow)** | 16:9 | 1920 × 1080 | Slide height is **Large**: a fixed band, `min-height` 72rem desktop and 46rem mobile, image `cover`-fitted. So the crop is wider than 16:9 on desktop (about 2:1 at 1440px) and **portrait on mobile**. Keep the subject in the central half of the frame and bake no text into the image. Overlay opacity is 20%. |
| **Full-width image banner** | 16:9 | 1920 × 1080 | Same `banner--*` heights as the hero (small 42rem, medium 56rem, large 72rem desktop). Not used on the homepage today. |
| **Promotional horizontal banner** | 3:1 | 1800 × 600 | ⚠️ No 3:1 slot exists yet. The announcement bar is text only. The closest is an image banner set to **Small** (42rem desktop, 28rem mobile), which crops a 3:1 source at the sides. Add a purpose-built section rather than forcing the ratio. |
| **Collection / category cards** (collection list, mega menu cards) | 4:5 | 1600 × 2000 | Collection list is set to **Adapt**, so the card takes the image's own ratio — consistency comes from the uploads, and one odd file shows. Mega menu cards are a hard 4:5 crop (20rem × 25rem). |
| **Product cards** (featured collection, collection grid, search) | 4:5 | 1600 × 2000 | Set to **Adapt**, so 4:5 uploads give portrait cards. Mixed source ratios give ragged rows. |
| **Related products, "All collections" page** | 4:5 | 1600 × 2000 | ⚠️ Both are set to **Square**, so a 4:5 file is centre-cropped to 1:1. Either switch them to Portrait for consistency with the rest of the site, or brief square-safe framing. |
| **Editorial / craft slider cards** | 4:5 | 1600 × 2000 | Hard 4:5 crop, two cards on desktop and one on mobile. |
| **Miniatures objects** | 4:5 | 1600 × 2000 | Deliberately varied per slot and breakpoint via `--miniatures-ratio`: quiet cards 4:5, the featured card 2:3 on desktop and 3:2 on tablet, and 1:1 for the quiet cards when only three objects are set. Expect side or top crop, so leave margin around the object. |
| **Our Story timeline images** | 4:5 | 1600 × 2000 | Hard 4:5 crop. |
| **Image with text** | 4:5 or 3:2 | 1600 × 2000 | Height is **Adapt**, so the image keeps its own ratio at medium column width. |
| **Blog / editorial imagery** | 3:2 | 1800 × 1200 | Blog image height is **Medium**: a fixed band (about 307px desktop, 220px mobile) `cover`-fitted, so it crops to a wider band than 3:2. |
| **Product images / model images** | 4:5 | 2048 × 2560 | The PDP gallery is **stacked** with lightbox zoom, and it shows the file's own ratio. Keep every image on a product the same ratio, or the gallery steps. |
| **Product fabric / detail images** | 4:5 | 2048 × 2560 | Same, for consistency within the PDP. |
| **Product thumbnails** | — | — | Generated by Shopify; `image_url` plus `widths` handles the responsive set. |
| **Decorative illustrations** | Original SVG ratio | SVG | Never force a ratio. Currently `periwinkle-coloured.svg`, at 80px in the Our Story hero and 260px (180px mobile) as the craft-slider watermark. |
| **Footer paper background** | Original artwork ratio | — | ⚠️ Not implemented. The footer is flat scheme-4 (Dusk) with no background image. It needs a section setting before an asset is worth preparing. |

**Adapt vs fixed, in one line:** where a Dawn section is set to **Adapt** the
uploaded ratio *is* the design, so 4:5 discipline in the media library is what
keeps the site tidy. Where it is fixed (Square, or a banner height) the theme
crops from the centre, so leave headroom.

### 6.2 Handling

- Images use `object-fit: cover` and have square corners.
- The placeholder or loading fill is **Linen `#EEE9DF`**.
- Hover zoom is slow and slight (`transform: scale(...)`, 600–700ms ease).
- **Botanical line illustrations** are a decorative motif. They appear as a
  small centred mark above the Our Story hero (80px) and as a faint watermark
  that bleeds off the bottom-left corner of the craft slider (opacity
  0.08–0.10, `pointer-events: none`, `aria-hidden`).
- Product photography often rests objects on pale stone in the lower third. So
  captions overlaid on it default to **dark text with no overlay**, because
  light text and a tint were illegible and dulled the glass. The overlay is an
  option: `rgb(46 44 53 / var(--miniatures-featured-overlay))`.
- The logo is a periwinkle flower icon plus a separate wordmark image, set side
  by side in the header (icon 50px wide).

---

## 7. Motion

### 7.1 Global

| Setting | Value |
|---|---|
| Reveal sections on scroll | **Off** |
| Hover effect | **3D lift** (cards tilt and lift on hover) |

Dawn duration tokens (`base.css`):
`--duration-short 100ms`, `--duration-default 200ms`, `--duration-medium 300ms`,
`--duration-long 500ms`, `--duration-extra-long 600ms`,
`--duration-extra-longer 750ms`, and `--ease-out-slow: cubic-bezier(0, 0, .3, 1)`.

### 7.2 Custom motion vocabulary

| Interaction | Timing |
|---|---|
| Link or colour hover | 200ms ease |
| CTA arrow nudge | `translateX(.3rem)`, 250ms ease |
| Carousel slide | `transform` 450ms ease |
| Image hover zoom | 600–700ms ease |
| Hero entrance ("rise") | 1100ms `cubic-bezier(.2, .7, .2, 1)`, staggered 120 / 240 / 360 / 600ms |
| Chapter reveal | opacity 900ms, transform 1000ms `cubic-bezier(.2, .7, .2, 1)` |
| Flower bloom (overshoot) | 900ms `cubic-bezier(.34, 1.45, .64, 1)` |
| Ambient loops | sway 4s, glow 3.2s, scroll-cue drip 2.4s, all ease-in-out |

**Motion principles**
1. Motion is slow, soft and organic, like growth rather than a snap.
2. **Motion is opt-in.** Animate only inside
   `@media (prefers-reduced-motion: no-preference)`, or add an "animated" class
   from JS only when motion is allowed. Every custom section has a
   `prefers-reduced-motion: reduce` fallback that removes transitions.
3. Content must be fully visible **without JS**, **with reduced motion**, and
   **in the theme editor** (`Shopify.designMode`).

---

## 8. Components and patterns

### Buttons
- **Primary:** a filled Dusk button with a white label and a 4px radius. Stock
  Dawn `.button`.
- **Secondary:** a scheme background with a Dusk label and a 1px Dusk border.
  Stock Dawn `.button--secondary`.
- **Editorial CTA (preferred in custom sections):** a text link with a 1px
  `currentColor` bottom border, 5–6px padding below, weight 500, and a trailing
  `→` arrow. On hover it dims to 0.7 opacity or turns the accent colour, and the
  arrow nudges right.

### Round icon button (carousel arrows)
46×46 circle with a 1px Ink border on Ivory and an Ink glyph. On hover it fills
Dusk with an Ivory glyph and scales to 1.05. Focus shows a 2px Dusk outline
offset by 3px.

> ⚠️ `periwinkle-editorial-slider.liquid` hard-codes these hex values instead of
> using the scheme variables. They match the palette today, but they will not
> follow a scheme change.

### Eyebrow + heading + body + CTA
This is the standard editorial copy block used by all three custom sections.
The eyebrow is uppercase and tracked in the accent colour. The heading is
Cormorant with optional italic `<em>`. The body is DM Sans at 1.5–1.6rem with
1.65–1.7 leading. The CTA is the underlined text link.

### Announcement bar and header
The announcement bar uses scheme-4 (Dusk) and is **sticky**. The header uses
scheme-1, is sticky (**always**), and sits directly under the bar. The logo is
middle-left on desktop and centred on mobile.

### Mega menu (collection cards)
Collections appear as a horizontal row of 4:5 poster cards (20rem wide) with the
title below. Edge fades use the scheme background, and arrows appear only while
there is somewhere to scroll.

### Mobile nav drawer
The drawer is full height, `min(80%, 40rem)` wide, and opens over the header. It
has its own logo bar and close button. The backdrop is a light blur with a flat
scrim as the fallback.

### Slideshow (homepage hero)
It is full-bleed. **Dots only**, with no arrows at any width. The controls
overlay the image.

### Badges
Sale uses scheme-4 (Dusk). Sold out uses scheme-3 (Linen with Ink text). Both
have a 4px radius and sit at the bottom left of the card.

### Cart
The cart is a **drawer** (scheme-1). Cart notes are on. The empty-cart state
suggests the *Ajrakh Vanaspati* collection.

---

## 9. Checklist for new sections

- [ ] Colours come from a colour scheme (`color_scheme` setting) **or** section
      colour settings that default to palette values
      (`#EEE9DF` / `#2E2C35` / `#4F4A70`). No off-palette hex values.
- [ ] Section colours are exposed as scoped custom properties
      (`--mysection-background` etc.), not repeated as literal hex values.
- [ ] Headings use `--font-heading-family`. If you use `<em>` italic, load the
      italic face.
- [ ] Eyebrow, heading, body and CTA follow the scale in §3.3.
- [ ] Only Dawn breakpoints (749 / 750 / 989 / 990).
- [ ] Padding top and bottom are section settings, following the §4.3 rhythm.
- [ ] Imagery follows the asset spec in §6.1 — 4:5 unless it's a full-bleed
      banner (16:9) or editorial photography (3:2) — with square corners and a
      Linen placeholder.
- [ ] Radius is 4px on controls and 0 on media and cards. No shadows.
- [ ] Motion is gated on `prefers-reduced-motion`, and content is visible
      without JS and in the theme editor.
- [ ] Text contrast is at least 4.5:1. Check against §2.7, and especially avoid
      Sage on Linen for small text.
