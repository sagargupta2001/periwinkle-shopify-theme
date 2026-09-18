# Our Story page — spec

The brand story told as a vertical timeline, with a single periwinkle that
grows down the page as the reader scrolls and comes to rest in full bloom at the
closing chapter.

- **Live at:** `/pages/our-story` (locally, http://localhost:9292/pages/our-story)
- **Template:** [`templates/page.our-story.json`](../templates/page.our-story.json)
- **Section:** [`sections/periwinkle-story-timeline.liquid`](../sections/periwinkle-story-timeline.liquid) (editor name **Peri story timeline**)
- **Styles:** [`assets/section-periwinkle-story.css`](../assets/section-periwinkle-story.css)
- **Behaviour:** [`assets/periwinkle-story.js`](../assets/periwinkle-story.js) (`<periwinkle-story>` custom element)
- **Entry points:** the "Our Story" button in the second *Image with text*
  section on the homepage. There is no navigation menu link today.

Setup in admin: create a page with the handle `our-story` and assign it the
`page.our-story` template. The template holds one section and no others.

---

## 1. Purpose

1. Tell the founding story — a mother's love of handloom, and the daughter who
   opened the door she didn't get to — as a piece of writing, not a marketing
   band.
2. Reward scrolling. The growing plant turns the page's length into the story's
   passage of time.
3. End on a way into the catalogue (Explore Sarees / Shop all).

## 2. Content model

### Section settings

| Group | Setting | Type | Default |
|---|---|---|---|
| Hero | `botanical_illustration` | image | *(SVG, currently `periwinkle-coloured.svg`)* |
| | `eyebrow` | text | "Our Story" |
| | `heading` | inline richtext | "A Dream *Stitched in Time*" |
| | `intro` | richtext | opening line |
| | `scroll_label` | text | "Scroll to begin" |
| Colours | `background_color` | colour | `#EEE9DF` Linen |
| | `text_color` | colour | `#2E2C35` Ink |
| | `accent_color` | colour | `#4F4A70` Dusk |
| | `bloom_color` | colour | `#8B87D0` Bloom |
| | `stem_color` | colour | `#6E9A73` Leaf |
| Padding | `padding_top` / `padding_bottom` | range | 96 / 120 |

Colours are emitted as custom properties on `#PeriwinkleStory-{{ section.id }}`.
`--story-muted` (text at 72%), `--story-line` (text at 18%) and the deep/light
bloom and stem variants are derived in Liquid, so the merchant sets five colours
and gets eleven.

### Blocks

| Block | Limit | What it adds | Settings |
|---|---|---|---|
| **Chapter** | — | A prose chapter, optionally with a pull quote | `marker`, `eyebrow`, `heading`, `heading_size` (regular / large), `text`, `quote`, `image` |
| **Colour swatches** | — | A chapter plus three round colour swatches with labels | `marker`, `eyebrow`, `heading`, `text`, `color_1–3`, `label_1–3`, `image` |
| **List** | — | A chapter plus a list | `marker`, `eyebrow`, `heading`, `text`, `items`, `list_style` (Tags / Numbered), `image` |
| **Closing** | **1** | The final chapter, with up to two buttons. Carries no leaves; the flower rests here. | `eyebrow`, `heading`, `text`, `button_label_1/2`, `button_link_1/2` |

**`items` format.** One entry per line. With **Numbered**, a line may be split
with a pipe into a name and a note: `Hand block prints | An extraordinary twist…`.
With **Tags** the whole line is the chip.

**Markers** (`I`, `II`, `III`…) are typed by hand, not generated. Renumber them
yourself when inserting a chapter.

### Current content (9 blocks)

| # | Marker | Block | Chapter |
|---|---|---|---|
| 1 | I | swatches | The first thread — "It began in a mother's hands" |
| 2 | II | chapter | Cloth carries memory (pull quote) |
| 3 | III | chapter | A single beautiful place |
| 4 | IV | chapter | The door (heading size **large**) |
| 5 | V | list (tags) | What you'll find |
| 6 | VI | list (tags) | Gathered from across India |
| 7 | VII | list (numbered) | Ten crafts, one home |
| 8 | VIII | chapter | Given with love (pull quote) |
| 9 | — | finale | Welcome — Explore Sarees / Shop all |

## 3. Layout

**Hero.** Centred, max 88rem: botanical mark (8rem) → eyebrow → display heading
(`clamp(4.4rem, 5vw + 2rem, 9.6rem)`) → italic Cormorant intro (max 44ch) →
scroll cue with an animated 5.6rem line. 8rem of padding below it.

**Timeline, desktop (≥990px).** The spine runs down the centre
(`--story-spine-x: 50%`). Chapters alternate sides, each with its image
opposite. Nodes are 4rem and the bloom scale is 1.9.

**Timeline, below 990px.** The spine moves to the left edge
(`--story-spine-x: calc(var(--story-node-size) / 2)`), nodes are 3.2rem, bloom
scale 0.8, and every chapter hangs to the right of it in one column.

**Chapter images** are a hard 4:5 crop.

**Closing** is centred, with a primary and a secondary button.

## 4. The growing periwinkle

### Model

`<periwinkle-story>` measures the timeline and exposes two custom properties.
The CSS draws everything from them.

| Property | Meaning |
|---|---|
| `--story-track` | Full stem length in px: timeline top → the closing chapter's node |
| `--story-growth` | 0–1, how much of that length has grown |

| Class | When |
|---|---|
| `.periwinkle-story--growing` | JS is alive (set on connect) |
| `.periwinkle-story--animated` | Motion is allowed, so chapters start hidden and reveal |
| `.is-reached` (on a chapter) | The stem tip has passed its node — its leaves unfurl |
| `.is-revealed` (on a chapter) | Its content has scrolled into view |
| `.is-bloomed` (on the element) | `growth >= 0.995` — the flower is open and at rest |

The element also dispatches `periwinkle-story:progress` with `{ growth }`.

### Scroll mapping

The stem tip targets a point at **55% of the viewport height**, clamped to
`[0, track]`. The rendered position eases toward the target at **12% of the
remaining distance per frame**, so the plant feels grown rather than dragged,
and work happens in a single `requestAnimationFrame`.

### Growth is one-way

**The plant never shrinks back.** `peak` holds the furthest the tip has reached
and the target never falls below it, so scrolling up leaves the stem, the
unfurled leaves and the open flower exactly as they were. A flower that
un-blooms reads as a scrubbing widget rather than as something that grew, and it
undoes the reward for reaching the end.

Consequences to keep in mind when editing:
- `.is-reached` and `.is-bloomed` are effectively **latches** within a page view.
  They reset only on reload.
- Chapter reveals were already one-way (a chapter is removed from `pending` once
  revealed).
- On resize, or when images and fonts change the timeline's height, `measure()`
  rescales `peak` and `current` **proportionally** to the new track, so growth
  keeps its place in the story instead of jumping or resetting. Verified across
  a desktop → tablet reflow: 0.572 → 0.585 with the track changing from 17706px
  to 8015px.

### Fallbacks

| Condition | Behaviour |
|---|---|
| **No JS** | Every chapter is visible. No `--growing` class, so nothing is hidden waiting to reveal. |
| **`prefers-reduced-motion: reduce`** | Chapters get `.is-revealed` immediately, the target is pinned to the full track, and the flower is drawn fully grown. No transitions. |
| **Theme editor** (`Shopify.designMode`) | Content is visible immediately, and the flower still grows so the merchant can see it. The editor replaces the element on re-render, which `connectedCallback` / `disconnectedCallback` handle. |

## 5. Accessibility

- The botanical illustration and the plant are decorative: `aria-hidden`, with
  no alt text.
- Markers and eyebrows are plain text alongside the heading, so a screen reader
  reads the chapter in order.
- Content is never gated behind an animation: without JS or with reduced motion
  it is all in the DOM and visible.
- Contrast: Ink on Linen is 11.36:1, muted text at 72% is around 8:1, and the
  Dusk accent on Linen is 6.82:1 — all pass AA. The bloom and stem colours are
  around 2.7:1 and are used **only** for the illustration.

## 6. Performance

- One `scroll` listener (passive) and one rAF loop that exits when the target is
  reached. `render()` returns early when rounded growth is unchanged.
- A ResizeObserver on the element catches images and fonts changing the height.
- Chapter images are lazy-loaded; the hero illustration is an SVG.
- CSS and JS load only on this page, from the section.

## 7. Known constraints

- **Markers are manual.** Inserting a chapter means renumbering by hand.
- **No menu entry.** The only link in is the homepage button.
- **Labels are literal English**, not `t:` keys, so the section is not
  translatable through locale files.
- The page is long — about 24000px on desktop with the current nine blocks.
  Adding chapters lengthens the stem rather than compressing it.

## 8. Editing guide

To add a chapter: **Theme editor → Our Story page → Peri story timeline → Add
block**, choose Chapter, Colour swatches or List, set the marker to the next
numeral, and drag it into place before the Closing block. The Closing block must
stay last — the stem ends at its node.

To restyle: change the five colour settings rather than the CSS. To change the
pacing, the tip position (55%) and the easing (0.12) are both in
`periwinkle-story.js`.
