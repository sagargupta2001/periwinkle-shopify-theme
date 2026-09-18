# Customizations on top of Dawn

Everything that differs from stock Dawn 16.0.0, with the reasoning and the
non-obvious gotchas recorded in the commit history. Read the relevant entry
before touching one of these areas.

| # | Feature | Main files | PR / commit |
|---|---|---|---|
| 1 | Sticky announcement bar + slideshow overlay controls | `announcement-bar.liquid`, `header.liquid`, `slideshow.liquid`, `component-slideshow.css`, `base.css`, `global.js` | #1 · `0227073` |
| 2 | Header logo lockup (icon + wordmark) | `snippets/header-logo.liquid`, `settings_schema.json`, `base.css` | #2 · `805b557` |
| 3 | Mega menu with collection cards | `snippets/header-mega-menu-cards.liquid`, `component-mega-menu-cards.css`, `mega-menu-cards.js` | #3 · `760e7b9`, `376f8b2` |
| 4 | Full-height mobile nav drawer | `snippets/header-drawer.liquid`, `component-menu-drawer.css`, `base.css`, `global.js` | #3 · `4e5d906` |
| 5 | Slideshow dots at every width | `component-slideshow.css` | #4 · `ae36925` |
| 6 | Peri editorial slider section | `sections/periwinkle-editorial-slider.liquid` | first commit |
| 7 | Peri miniatures section | `sections/periwinkle-miniatures.liquid`, `section-periwinkle-miniatures.css` | #5 · `621111c` |
| 8 | Our Story timeline page | `sections/periwinkle-story-timeline.liquid`, `section-periwinkle-story.css`, `periwinkle-story.js`, `templates/page.our-story.json` | #6 · `99012f9` |
| 12 | Peri journal index (blog listing) | `sections/periwinkle-journal-blog.liquid`, `section-periwinkle-journal-blog.css`, `templates/blog.json`, `assets/icon-whatsapp.svg` | — |
| 11 | Peri journal article template | `sections/periwinkle-journal-article.liquid`, `section-periwinkle-journal.css`, `periwinkle-journal.js`, `templates/article.journal.json` | — |
| 10 | Peri coming soon section | `sections/periwinkle-coming-soon.liquid`, `section-periwinkle-coming-soon.css`, `periwinkle-coming-soon.js` | — |

Theme settings (colours, fonts, radii) are also customized, but those live in
`settings_data.json`. See [design-guide.md](design-guide.md).

---

## 1. Sticky announcement bar

- Opt-in section setting: **Sticky announcement bar** (`sticky`), currently on.
- The section wrapper is targeted with `:has(.utility-bar--sticky)`, because a
  section can't add a class to its own wrapper.
- `StickyHeader` (in `header.liquid`) publishes `--announcement-bar-height` and
  keeps `--header-height` current with a **ResizeObserver**. A breakpoint
  listener isn't enough: the bar wraps to two lines on mobile, text rewraps
  between breakpoints, and "reduce logo size" shrinks the header without a
  resize event.
- The on-scroll-up header tucks behind the bar. There is also a rule for the
  reverse section order, since the header group can be reordered in the editor.

### Slideshow overlay controls
- The controls used to be `custom_css` in `index.json`, where `z-index: 5` beat
  the header's 3 and media queries aren't available. They now live in
  `component-slideshow.css` behind `.slideshow__controls--overlay`, with a
  **Show controls over image** setting.
- `slideshow-component` has `isolation: isolate`, so no z-index inside it can
  compete with the header group. **Don't remove it.**
- The overlay rules are qualified with the `slideshow-component` element
  selector on purpose. They override `.slider-buttons` from
  `component-slider.css`, which later sections re-emit, so they have to win on
  specificity rather than load order.
- Bug fix in `global.js`: `SliderComponent.update()` now clamps `currentPage`
  and checks for divide-by-zero. It used to throw a TypeError on resize, because
  `scrollLeft` had not yet been re-clamped.

## 2. Header logo lockup

- `settings.logo` is still the full brand mark and is used on the password
  page, gift cards and JSON-LD. The new settings affect **only the header**:
  - `logo_text`: wordmark image (optional)
  - `logo_text_width`: its width
  - `logo_text_hide_mobile`: show only the icon on phones
- The logo markup moved from two copies in `header.liquid` into
  `snippets/header-logo.liquid`, which takes `logo_position` for the `sizes`
  hint and a `preload` flag, so the drawer's second copy doesn't preload twice.
- The wordmark has `alt=""` because the icon already announces the shop name.
- ⚠️ **Don't set a CSS `width` on the lockup images.** They are sized by their
  `width` attribute, and a CSS width overrides it and falls back to the file's
  intrinsic size.
- Gaps are controlled by `--logo-lockup-gap` (1.2rem) and
  `--logo-lockup-gap-mobile` (0.8rem).

## 3. Mega menu with collection cards

- A fourth option for **Menu type** (`menu_type_desktop: mega_cards`). The
  header uses it now.
- Second-level links resolve through `link.object` to their collection and
  render as a horizontal row of 4:5 poster cards.
- **Content decides card mode, not a setting.** A menu shows cards only if
  *every* child link is a collection with an image. Otherwise it falls back to
  the plain mega-menu text list. Today only **Sarees** qualifies. Menus upgrade
  themselves as artwork is uploaded.
- The row **scrolls natively** rather than wrapping. `mega-menu-cards.js` only
  adds affordances: edge fades and arrows driven by `data-overflows`,
  `data-at-start` and `data-at-end`. If the JS fails, the row still scrolls.
- The card CSS is only requested for this menu type.
- Desktop only. The mobile drawer still uses text links.
- ⚠️ A ResizeObserver doesn't work here: a closed `<details>` skips layout, so
  the observer never fires. Measure on connect and on the `toggle` event.
- ⚠️ Rotate the **caret**, not the arrow button. The standalone `rotate`
  property is composed before `transform`, so the centring translate would move
  along the rotated axis.

## 4. Mobile nav drawer

- The drawer is fixed, full height, `min(80%, 40rem)` wide, and sits over the
  header and announcement bar. The visible strip of page is the tap-to-close
  target.
- The backdrop is a small blur, with a flat scrim where `backdrop-filter` is
  unsupported. The radius is kept small for older Android.
- `.section-header` must outrank the announcement bar while `.menu-open` is
  set, which HeaderDrawer already toggles.
- ⚠️ **Naming trap:** the nav is `<header-drawer>`. The `<menu-drawer>` rules in
  `component-menu-drawer.css` are for the **facets filter drawer**. The nav
  backdrop belongs to `.header__icon--menu[aria-expanded='true']::before` in
  `base.css`.
- **Highlight on the last item tapped (fixed).** Dawn tinted
  `.menu-drawer__menu-item:focus`. A tap leaves DOM focus on the summary, and
  `closeSubmenu()` calls `removeTrapFocus(summary)`, which focuses it again — so
  the item the reader last opened stayed tinted as though it were the current
  page. The rule now uses `:focus-visible` (plus `.focused`, Dawn's fallback for
  browsers without it), so keyboard users keep the highlight and pointer users
  don't. `:hover` moved into `@media (hover: hover)` for the same reason, since a
  tap can leave a sticky hover state. `--active` still marks the real current
  section from `link.child_active`.
- Submenus position against the navigation container, not
  `.menu-drawer__inner-container`. Otherwise they cover the drawer's close bar.
- The drawer has its own bar: the logo lockup plus a close button.
- **Get in touch** sits under the last menu item: a Dusk eyebrow, a phone
  (`tel:`) link and a mail (`mailto:`) link, with `icon-phone.svg` and
  `icon-mail.svg`. The text comes from the header section's *Mobile menu
  contact* settings (`drawer_contact_*`), which default to the store's number
  and email. Clear both to hide the block. When the block is present, the
  navigation container switches to `grid-template-rows: auto 1fr auto`, so the
  block follows the menu directly and the social bar stays at the bottom.
- Social links in the drawer (and in `social-icons.liquid`) open in a new tab
  with `rel="noopener"`, and tell screen readers so.

## 5. Slideshow dots only

- Arrows are hidden at every width, and the dots overlay the image.
- ⚠️ The arrow and autoplay buttons **stay in the DOM** (hidden with
  `.slider-button`). `SlideshowComponent` moves between slides by clicking them,
  so removing them breaks dragging.

## 6. Peri editorial slider (`periwinkle-editorial-slider`)

- Homepage "The Art of Craft" band. The left side has an optional botanical
  watermark, an eyebrow, a heading, a description and a CTA. The right side is
  a carousel of **Craft card** blocks, each with a collection, image, title,
  description and link. Cards fall back to the collection's image and title.
- It shows 2 cards on desktop and 1 at 989px and below. Arrows appear only when
  there are more than 2 cards. Swipe or drag is supported.
- CSS and JS are **inline** in the section, scoped with
  `#periwinkle-editorial-{{ section.id }}`. This predates the other custom
  sections, which use separate asset files.
- Known cleanup candidates: the arrow colours are hard-coded hex values, not
  scheme or section variables. The CTA and card "Explore" strings are
  hard-coded English. There is a duplicated `if (!section) return;` line.

## 7. Peri miniatures (`periwinkle-miniatures`)

- "Small Objects, *Beautiful Stories.*" Editorial copy sits beside an
  asymmetric gallery of up to **5 Object blocks** (image, title, subtitle, link,
  and a "Feature this object" option).
- On desktop, a 12-row grid staggers the columns, and spacing sits on the cards
  rather than `row-gap`. On tablet the featured card spans full width above a
  2×2 grid. On mobile the featured card comes first, followed by a left/right
  stagger. Fewer than five objects re-flow without empty slots.
- Colours come in as `--miniatures-*` custom properties (background, text,
  accent, featured text, and featured overlay opacity).
- The featured caption defaults to **dark text with no overlay**. See the
  imagery notes in the design guide.

## 8. Our Story timeline (`periwinkle-story-timeline`)

- Blocks: **Chapter**, **Colour swatches** (3 colours + labels), **List**, and
  **Closing**.
- One periwinkle grows down the spine as the page scrolls. Leaves unfurl at each
  chapter (`.is-reached`), and the flower comes to rest open at the closing
  chapter (`.is-bloomed`). Adapted from the "Animated Blooming Flower" CSS demo.
- `periwinkle-story.js` sets `--story-track` (stem length in px) and
  `--story-growth` (0–1), and adds `.periwinkle-story--animated` **only when
  motion is allowed**. Without JS, with reduced motion, or in the theme editor,
  all content is plainly visible.
- **Growth is one-way.** The plant does not shrink back on scroll up: `peak`
  holds the furthest the tip has reached and the target never falls below it. On
  resize, `measure()` rescales `peak` and `current` proportionally to the new
  track. Full spec in [our-story-page.md](our-story-page.md).
- The Cormorant italic face is loaded in the section, because Dawn loads only
  the upright face.
- Colours come in as `--story-*` properties. Deep and light variants are derived
  in Liquid with `color_darken` and `color_lighten`.

## 9. Footer

- The styling lives in the **"Periwinkle footer"** block at the end of
  `assets/base.css`, not in `section-footer.css`. It was written in the admin
  era, so it uses hard-coded colours and `!important`. The block sets the torn
  paper background on `.footer__content-top`, the dashed column separators, and
  the botanical `::before`/`::after` illustrations.
- **"Connect with us"** is a stock *Text* block. Its rich text is set to match
  the menu links next to it (DM Sans 14px, regular weight). Older content used
  `<h6>`, which Dawn renders as tiny bold caps, so `h6` gets the same styling as
  `p`. Write plain paragraphs in the editor.
- **Columns:** at 750–989px the four blocks sit 2 × 2, and only the second
  column gets a separator. At 990px and up the columns size to their content,
  so the email address fits on one line.
- **Social icons** share the copyright row instead of Dawn's newsletter row
  (`sections/footer.liquid`). From 750px the copyright sits on the left and the
  icons on the right, and the row is capped at the paper's 1072px so its ends
  line up with the paper's edges. On phones the icons go below the copyright,
  centred. The URLs live in theme settings (*Social media*).
- `show_policy` is off, because the policies are already in the Help menu.

## 10. Peri coming soon (`periwinkle-coming-soon`)

- Homepage "Still *on the loom.*" band on Lavender Mist, previewing upcoming
  services. Today: **Bridal Trousseaus** and **The Cloth That Remembers**.
- Header (eyebrow with a pulsing dot, heading, italic intro), then up to 4
  **Concept** blocks: label, status tag, heading, description, highlights (one
  per line in a textarea), a 4:5 main image, an optional 4:5 **inset** image
  with caption, and an optional link. The big `01`/`02` numerals come from the
  block order.
- Rows alternate sides from 750px (`media_first` picks where the first image
  goes). Below 750px the image always comes first, with the frame pushed to
  alternate edges for rhythm.
- The inset is mounted over the frame's lower corner with a border in the
  section background. The frame gets `margin-bottom` equal to the inset's
  overhang, and a caption hangs *below* the inset (absolutely positioned, with
  padding reserved on the media) — otherwise it collides with the main photo.
- **Before / after slider.** Each concept's *Image display* can switch to
  *Before / after slider*, which reuses the block's images: **Main image =
  After**, **Inset image = Before**. It needs both images and falls back to the
  inset layout otherwise. `<periwinkle-compare>` sets a unitless
  `--compare-position` (0–100). Before is clipped from the right with
  `clip-path`, and the tag opacities are derived from the same number in CSS.
  - A visually hidden native `range` input carries keyboard and screen
    reader support (arrows, Home/End, PageUp/Down, `aria-valuetext`). It has
    `pointer-events: none`; the frame handles the pointer.
  - Touch only takes over after a sideways move. The frame has
    `touch-action: pan-y`, so vertical swipes still scroll the page.
  - ⚠️ A mouse release outside the window can go unreported, which left the
    handle following the cursor. A buttonless `pointermove` and
    `lostpointercapture` both end the drag.
  - The knob is clamped 2.4rem inside the frame so it isn't cut off at 0 or
    100%, while the line tracks the true split.
  - Without JS it rests at a static 50/50 split, with no knob and no focusable
    input. A one-time sway hint plays when it comes into view, only with motion
    allowed, outside the editor, and before any interaction.
  - It works best with a matched pair (same camera and background, only the
    garment changed).
- Optional **email sign-up** uses `{% form 'customer' %}` with
  `contact[tags]` from the *Customer tags* setting (default
  `newsletter,coming-soon`), so launch emails can target that tag in Shopify
  admin.
- Muted, hairline and fill colours are derived in Liquid with `color_modify`
  because the colour settings are hex.
- `periwinkle-coming-soon.js` adds `.is-animated` (fade and rise on scroll)
  only when motion is allowed, outside the editor, and where
  IntersectionObserver exists.

## 11. Peri journal article (`article.journal`)

- An alternate article template. A post uses it when **Theme template** is set
  to `journal` on the post in admin. The stock `article.json` is untouched.
- Title, excerpt (shown as the italic standfirst), featured image, body,
  author, date and tags all come from the post. The first tag is the eyebrow
  unless the section sets one. Reading time is words ÷ 200.
- **Per-post extras are metafields** on Blog posts (Settings → Custom data):
  `custom.gallery` (list of files), `custom.shop_link` (URL) and
  `custom.shop_label` (single line text). Gallery captions are each image's
  **alt text**, so the caption is `aria-hidden` to avoid reading it twice. A
  theme can't create metafield definitions, so they're set up once in admin.
- Body content from the rich text editor is styled in place: drop cap on the
  first paragraph, `<blockquote>` as a Dusk pull quote, and body images at
  full column width.
- Share: round 42px icon buttons. The WhatsApp icon (`icon-whatsapp.svg`,
  monochrome in the ink colour, not WhatsApp green) is a plain link that works
  without JS. A second button that JS reveals sets `data-mode`: `share` shows
  Dawn's share icon and opens the native share sheet (phones), and `copy` shows
  the copy icon, swaps to a tick and shows a "Link copied" toast for 2s. The
  icon for each state is picked in CSS from `data-mode` and `data-state`.
- The byline ("By …") sits on its own line above date · read time. On one
  line it wrapped on phones with a `·` leading the second row.
- The `·` meta separator is written as `'\00B7'` in CSS so it can't be
  mis-decoded if the stylesheet is served without a charset.
- Comments aren't rendered. If a blog turns comments on, use the stock
  template for those posts or add them here.

## 12. Peri journal index (`templates/blog.json`)

- Replaces Dawn's `main-blog`, whose "collage" layout blew the newest post up
  to near full width, so the page read like an article instead of an index.
- Editorial header (eyebrow, italic-accent heading, intro), then topic filters
  built from `blog.all_tags` (shown only with at least two tags; the current
  one is marked `aria-current` and filled Dusk).
- On page 1 the newest story leads as a **split card**: the 3:2 image takes
  about 7/12 of the row, with the copy beside it ("Latest story · topic", title,
  date · read time, summary, "Read the story"). *Feature the latest story*
  turns it off.
- The rest are 3:2 cards (topic, title, date · read time, 3-line summary).
  The grid uses 3 columns only when there are at least 3 cards, otherwise 2,
  so a small journal doesn't leave a lonely third column. The title link is
  stretched over the card.
- Summary is the post's excerpt, or its first 32 words.
- Paginated with Dawn's `pagination` snippet (*Stories per page*, default 10).

---

## Other non-Dawn touches worth knowing

- `templates/index.json` has merchant-authored `custom_css` that centres the
  collection-list and featured-collection titles. `custom_css` can't contain
  media queries, so put anything responsive in an asset file instead.
- `layout/theme.liquid` loads Shopify's `standard-events.js` module and fires a
  `PageViewEvent`. `standard-actions-override.js` is loaded globally.
- The product **Disclosures** section, cart disclosure modal and tooltip, and
  `component-discounts.css` come with this Dawn version, not from this project.
