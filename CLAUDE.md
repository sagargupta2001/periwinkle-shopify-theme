# Periwinkle Shopify theme

A Dawn 16.0.0 fork for the Periwinkle store (Indian textile clothing and
objects). It is written in plain Liquid, CSS and vanilla JS, with no build step.

Start with [docs/README.md](docs/README.md):
- [docs/project-overview.md](docs/project-overview.md): sync workflow, structure, page composition
- [docs/customizations.md](docs/customizations.md): every change from Dawn, with gotchas
- [docs/design-guide.md](docs/design-guide.md): palette, colour schemes, type, spacing, motion
- [docs/conventions.md](docs/conventions.md): how to write sections, CSS and JS here
- [docs/our-story-page.md](docs/our-story-page.md): spec for the Our Story timeline page

Run it locally (serves at http://localhost:9292):

```bash
shopify theme dev --store periwinkle-by-sherry.myshopify.com
```

Essentials:
- `main` syncs to Shopify both ways. Admin edits arrive as "Update from Shopify"
  commits, so pull first and keep JSON template and settings diffs minimal.
- The palette is Ivory `#FAF8F3`, Ink `#2E2C35`, Dusk `#4F4A70`, Linen
  `#EEE9DF`, Lavender Mist `#E8E6F2`, and Sage `#65735B`. Headings use
  Cormorant, body text DM Sans. Use 4px radius on controls and no shadows.
- Custom sections are named `periwinkle-*.liquid`, with CSS in
  `assets/section-periwinkle-*.css`. They are BEM-named, take colours through
  scoped custom properties, and gate motion on `prefers-reduced-motion`.
- Use Dawn breakpoints only (749/750, 989/990).
