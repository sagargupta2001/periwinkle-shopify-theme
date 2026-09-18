# Development conventions

These are the conventions the custom work in this theme already follows. Match
them when adding or changing code.

## Workflow

1. `git pull` first. Admin edits land on `main` as "Update from Shopify"
   commits.
2. Branch (`feature/…` or a descriptive slug), commit, open a PR, and merge to
   `main`. Shopify deploys from `main`.
3. Keep diffs to `templates/*.json`, `sections/*-group.json` and
   `config/settings_data.json` small, because the admin writes these files too.
4. Commit messages have a short imperative subject. The body explains **why**
   and records gotchas for the next person. The history is the design log, so
   keep it useful.

## Sections

- Name custom sections `periwinkle-<feature>.liquid`, with the schema `name`
  **"Peri &lt;feature&gt;"** so they group together in the theme editor.
- Put styles in `assets/section-periwinkle-<feature>.css` and load them from the
  section with `stylesheet_tag`. Put behaviour in
  `assets/periwinkle-<feature>.js`, loaded with `defer`. (The editorial slider's
  inline `<style>` and `<script>` is the older pattern. Don't copy it.)
- Use BEM class names under a section root: `.periwinkle-<feature>__element--modifier`.
- Give the root a unique id (`PeriwinkleStory-{{ section.id }}`) and set the
  section's colour and spacing settings **as custom properties on that id** in a
  `{% style %}` block. The stylesheet then reads only
  `var(--<feature>-background)` and similar properties.
- Expose content, links, colours, and top and bottom padding as settings. Add a
  `presets` entry so the section can be added from the editor, and use sensible
  palette defaults (see the design guide checklist).
- Use blocks for repeatable items, and cap them with `max_blocks` where the
  layout depends on it.
- Stock Dawn sections use `t:` locale keys. When you add a setting to a *Dawn*
  section, add its label to `locales/en.default.schema.json`. Custom
  `periwinkle-*` sections currently use literal English labels.

## CSS

- 1rem = 10px. Use rem for type and spacing.
- Use Dawn breakpoints only: `max-width: 749px`, `min-width: 750px`,
  `max-width: 989px`, `min-width: 990px`.
- Take colours from scheme variables (`rgb(var(--color-foreground))`) or section
  custom properties, never literal hex values.
- Take fonts from `var(--font-heading-family)` and `var(--font-body-family)`.
- When you override Dawn component CSS, prefer **specificity** (for example an
  element-qualified selector) to relying on load order, because sections re-emit
  component stylesheets.
- Use `isolation: isolate` on components with internal z-index, so they can't
  compete with the sticky header group.
- Fix a rule in the place that actually owns it rather than adding a competing
  override, and leave a comment if the ownership is surprising.
- Comment blocks explain *why*, not *what*.

## JavaScript

- Use vanilla custom elements, following Dawn's style. Don't add frameworks.
- Progressive enhancement: the feature must work, or at least be fully readable,
  without JS. JS adds affordances such as arrows, fades and animation classes.
- Gate motion on `window.matchMedia('(prefers-reduced-motion: reduce)')` and
  skip it in the editor (`Shopify.designMode`).
- Prefer a ResizeObserver to breakpoint listeners for layout-dependent values,
  but note that it never fires for content inside a closed `<details>`.

## Accessibility

- Decorative images get `alt=""` and `aria-hidden="true"`. Don't announce the
  brand twice.
- Every control needs a visible `:focus-visible` style (2px outline, 3px offset).
- Icon-only buttons need an `aria-label`.
- Keep text contrast at 4.5:1 or above. See the table in the design guide.

## Verifying changes

There is no test suite. To verify a change, run the theme locally:

```bash
shopify theme dev --store periwinkle-by-sherry.myshopify.com
```

Then, at http://localhost:9292:
- Check it at 375px, 768px, 1024px and 1440px or wider.
- Check it with reduced motion on, with JS disabled where relevant, and inside
  the theme editor.
- Check the sticky announcement bar and header stacking still work, and that
  opening the mobile drawer still covers them.
