# Docs index

This page lists which doc to read for which task. `CLAUDE.md` imports it, so it
loads into every Claude Code session automatically. The docs themselves don't
load, so read only the ones your task needs.

## Before you start

- **Pull `main` first.** It syncs with the live theme both ways, and admin
  edits arrive as "Update from Shopify" commits.
- **Touching store data or the launch?** That covers products, collections,
  menus, tags, shipping, discounts, policies and payments. Read the *Open
  items* at the top of [docs/store-status.md](store-status.md) first, so you
  don't redo or contradict something in progress.

## Which doc for which task

| If you're… | Read | Focus on |
|---|---|---|
| New to the repo | [docs/project-overview.md](project-overview.md) | Sync workflow, directory map, what's on each page |
| Writing or editing a section, snippet, CSS or JS | [docs/conventions.md](conventions.md), then [docs/customizations.md](customizations.md) | The conventions, then the entry for the feature you're touching |
| Restyling anything: colours, type, spacing, motion | [docs/design-guide.md](design-guide.md) | Palette, colour schemes, typography |
| Changing the header, menu drawer, mega menu or slideshow | [docs/customizations.md](customizations.md) | Entries 1–5 and their gotchas |
| Working on the Our Story page | [docs/our-story-page.md](our-story-page.md) | Content model, layout, animation |
| Editing the home page or any template JSON | [docs/customizations.md](customizations.md), [docs/decisions.md](decisions.md) | Decisions 3–4; check collection handles in [docs/store-status.md](store-status.md#collections) |
| Changing collections, menus, tags or gifting | [docs/store-status.md](store-status.md), [docs/decisions.md](decisions.md) | Collections and Menus tables; decisions 1–8 |
| Listing, duplicating or renaming products | [docs/decisions.md](decisions.md) | Decisions 9–11: titles, handles, brand names |
| Changing shipping, discounts, weights or payments | [docs/store-status.md](store-status.md), [docs/decisions.md](decisions.md) | Shipping and Discounts sections; decisions 12–13 |
| Changing contact details or policies | [docs/store-status.md](store-status.md#contact-details), [docs/decisions.md](decisions.md) | The canonical details; decision 14 |
| Preparing for launch or running the test order | [docs/store-status.md](store-status.md) | Open items, Test order, Launch day |
| Answering "why is it set up like this?" | [docs/decisions.md](decisions.md) | Search for the topic |

## All docs

- [docs/project-overview.md](project-overview.md): the store, the GitHub ↔
  Shopify sync, the directory map, and what's on each page.
- [docs/customizations.md](customizations.md): every change from stock Dawn,
  with the reasoning and gotchas.
- [docs/design-guide.md](design-guide.md): colour palette, colour schemes,
  typography, spacing, shape, imagery and motion.
- [docs/conventions.md](conventions.md): section, CSS and JS conventions,
  accessibility, and how to verify a change.
- [docs/our-story-page.md](our-story-page.md): spec for the Our Story timeline
  page.
- [docs/store-status.md](store-status.md): open launch items, then a snapshot
  of how the store is set up today.
- [docs/decisions.md](decisions.md): an append-only log of store decisions and
  why they were made.

## Keeping docs current

- When a PR adds a section or changes a pattern, update the matching doc in
  the same PR.
- When you change store data in the Shopify admin, update
  `docs/store-status.md`. This covers collections, menus, tags, shipping and
  discounts.
- If the change is structural, also add an entry to `docs/decisions.md`.
- When you add a doc, add it to both tables on this page.
