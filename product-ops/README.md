# Product operations build scripts

Generates and signs the Periwinkle Apple Shortcuts. The docs are in
[docs/product-operations/](../docs/product-operations/README.md), and
[building-and-signing.md](../docs/product-operations/building-and-signing.md) covers these
scripts.

`local/` holds signed shortcuts and folder references. They contain personal iCloud IDs, and
this repo is public, so git ignores that folder.

The complete rebuild sources are `build/build.py`, `build/shortcutlib.py` and
`build/label_printing.py`. New Product and Print Product Label include the
NIIMBOT PDF handoff. `build/stage_client_release.py` copies only the signed client
set to a versioned shared iCloud folder, with installation instructions and a
hash manifest. See the [release instructions](../docs/product-operations/building-and-signing.md#rebuild-and-share-a-release).
