# Product operations build scripts

Generates and signs two self-contained Apple Shortcuts: **Periwinkle - Operator**
and **Periwinkle - Client**. Their first menus contain the existing operations.
Modular Python builders remain the source of truth; no helper shortcuts need installation. The docs are in
[docs/product-operations/](../docs/product-operations/README.md), and
[building-and-signing.md](../docs/product-operations/building-and-signing.md) covers these
scripts.

`local/` holds signed shortcuts and folder references. They contain personal iCloud IDs, and
this repo is public, so git ignores that folder.

The complete rebuild sources are `build/build.py`, `build/shortcutlib.py` and
`build/label_printing.py`, and `build/photo_links.py`. Register and Work on
Product can preview linked Shared Album photos without saving image copies. New Product and Print Product Label include the
NIIMBOT PDF handoff. `build/stage_client_release.py` copies only the signed, client-account-bound Client
bundle to a versioned shared iCloud folder, with installation instructions and a
hash manifest. See the [release instructions](../docs/product-operations/building-and-signing.md#package-the-clients-file).

[Recovery](../docs/product-operations/recovery.md) documents the complete folder
layout, metadata restoration and rebuilding account references after deletion.
