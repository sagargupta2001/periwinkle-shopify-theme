# Exporting a Shared Album photo on the Mac

**22 November 2026 result:** direct export through the Photos UI works. A
Shortcut-only command-line export is still experimental and is not part of
Periwinkle - Operator. This test does not establish a complete unattended
product-creation workflow.

## What was verified

At Sagar's explicit approval, Photos → Settings → iCloud → Shared Albums was
enabled on his Mac. iCloud Photos stayed off. Shared albums appeared, including
Periwinkle - Sarees with five photos. Shared Albums can cache photos locally;
this setting is independent of syncing the personal library through iCloud Photos.

A previously confirmed test-photo reference was read from the private pre-reset
backup. Its album and date located the asset in Photos. File → Export → Export
Unmodified Original exported a JPEG into a temporary local directory, without
importing the photo into Library or changing the album. Its filename matched
the extensionless name saved by the iPhone. The file decoded successfully at
4032 × 3024 pixels, 2,114,628 bytes, and was visually inspected. This was an old
dummy image, not a real product submission or an image-generation exercise.

The temporary image and working directory were removed after verification.
A metadata/hash result and private diagnostic inputs/installers remain under
ignored product-ops/local/, with no exported image retained. The register,
Shopify, existing product shortcuts and source album were unchanged.

## Current agent-operated route

The Mac must be awake and unlocked, and Photos must have the intended Shared
Albums available. The agent operates the native UI through computer-use tools:

1. Read a confirmed photo-links reference for the intended SKU. A pending link
   must be finished by the client; do not silently select an arbitrary photo.
2. Open the exact Shared Album and locate the photo using the recorded date.
3. Choose File → Export → Export Unmodified Original. Use File Name, no
   subfolder grouping and a new private temporary working directory.
4. Verify the exported filename against the saved photoName and decode the
   image before using it. If the name differs or the match is uncertain, stop;
   a visually similar image is not evidence of identity.
5. Supply the actual file to the image editor, rather than a screenshot of
   Photos or a filename string. Remove the temporary source copy when processing
   is complete. Final Shopify media is a separate, intended publication output.

This UI route can be performed by the agent without the operator manually
exporting the image, but still depends on a usable unlocked desktop. The test
covered one confirmed photo on Sagar's account; other-account metadata matching,
large-album navigation and a full live-product batch remain unverified.

## Command-line experiment and its limits

Apple documents passing input files and collecting output with
[shortcuts run](https://support.apple.com/guide/shortcuts-mac/run-shortcuts-from-the-command-line-apd455c82f02/10.0/mac/27).
The installed Periwinkle role shortcuts were successfully listed using the CLI
outside the agent sandbox. Sandbox execution reported a helper-communication
error, so that failure alone does not establish a broken Mac installation.

The isolated photo_export_experiment.py accepts a JSON input containing
albumName, photoName and mode (inspect or export). It contains no account folder
reference or baked-in product metadata. It only queries the named album and
only attempts image output when exactly one filename matches. The diagnostic
does not write to Photos or the register.

The tested prototype returned exit code zero without the requested JPEG or
text-report file, both by name and by its installed identifier. Running it from
the editor without input produced an empty-album error. No accepted input types
were initially declared; enabling Files in the editor did not produce a successful
CLI result. The source now declares Files explicitly, but a fresh source rebuild
with that metadata has not passed an end-to-end run. The cause is unresolved.
Always verify actual output bytes; an exit code alone is insufficient.

Native Import stalled, while opening the signed file through Finder reached
Add Shortcut successfully. Replace briefly left two same-name diagnostic tiles;
the superseded one was removed before further runs. Both temporary installations
were deleted at the end, with the library back to the two role shortcuts and
five personal shortcuts. No diagnostic installer folder was added to iCloud.

Keep this separate from operational releases until JSON input, exact matching,
safe zero/ambiguous results and actual image output pass on the Mac. A future
integration should preserve the two-role installation model and validate the
saved photo date as well as album/name.
