# Two role shortcuts

Build 19 packages the existing operations into two self-contained shortcuts.
Install one tile per role instead of maintaining eight separate operation tiles.

| Periwinkle - Client | Periwinkle - Operator |
|---|---|
| New Product | Register |
| Update Stock | Work on Product |
| Fix Product | Publish Products |
| Print Product Label | Process Stock Requests |

These are the first menu options. Existing operation menus and behaviour follow
unchanged. Choose one operation per run; launch the role shortcut again for the
next task. There is no menu loop around the operation's existing Repeat actions.
Cancel stops the run, and the role menu displays the build number.

## Source and account boundaries

Keep editing the operation builders in build.py and their shared photo/printing
modules. role_bundle() inlines those actions beneath a menu, replaces each
operation's root reference with one common folder binding and adds Stop after
each branch. No Run Shortcut actions or helper installations are required.
Regression tests compare each inlined branch with its standalone builder,
including variable and control-flow references.

Both roles use the same authoritative JSON records, photo-links and
photo-pending folders. No migration, reset or image copy is needed.
Client/Operator are workflow roles, not access control: everyone with access to
the shared data folder can read its files, including prices.

Sagar can install both roles, built using his operator folder reference. The
client receives only Client, built using her client folder reference. Although
both Client files have the same name, they contain different account bindings.
Never place the operator's testing copy in the client-shared folder. The staging
command requires the client reference and verifies that binding before writing.

## Install and migrate

1. Follow [Building and signing](building-and-signing.md) to generate the two
   operator-account files and one client-account file in separate directories.
2. On Sagar's phone, open the two files from the private **Periwinkle Operator
   Install - Build 19 - 2026-11-20** iCloud folder and add them. On the client's
   phone, open the one Client file from the shared **Periwinkle Product Operations
   → shortcuts → client-build-19** folder. Future same-name updates use Replace.
3. Keep the old operation tiles during the first check. Verify the build-19
   menu, then Operator → Register → an existing product's details/photo. Open
   Client and check all four first-menu choices. Do a dummy intake, photo
   confirmation/resume and client-to-operator handoff before live use. Verify
   label import and physical printing separately with the client's B1.
4. After those checks pass, remove the old role's operation tiles from Shortcuts.
   Remove only the eight operation tiles on Sagar's account and four on the
   client's account; preserve personal shortcuts and the two new role tiles.
   Keep a signed predecessor privately for rollback. Never delete the shared
   operations folder or Shared Albums as part of this migration.

The build-19 signing, installer staging and iPhone import/runtime checks are
pending. The folders above are installation targets. Existing build-18 tiles
remain available until the checks above pass. An automated action comparison
does not establish iOS import behaviour for the larger bundles.

## Rollback and recovery

If a bundle fails, use the retained old operation tile and record which menu
branch failed before changing source. Records remain in iCloud Drive. Avoid
retrying a write until the existing record/log has been checked.

Rebuild a lost installer from source and the account's saved folder reference.
If the data folder was recreated, generate fresh references on both accounts
before rebuilding. [Recovery](recovery.md) documents the entire operations tree,
including both metadata-only photo folders and preservation of SKU numbering.
