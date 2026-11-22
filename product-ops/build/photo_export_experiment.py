"""Mac-only diagnostic: return a named Shared Album photo to the CLI.

Input is a JSON file with albumName and photoName. The shortcut contains no
account references or product metadata. It never writes Photos or the register.
The caller chooses a temporary output path using shortcuts run --output-path.
This is an isolated experiment, not an operational release. On 22 November
2026 the CLI attempt returned no output; direct export through Photos worked.
Do not integrate this prototype until input/output execution is verified.
"""
import argparse
import plistlib

from build import BLUE, Store
from photo_links import find_album_photos, text_field
from shortcutlib import IS, Shortcut, Var, attachment, text


class ShortcutInput(Var):
    def __init__(self):
        super().__init__("Shortcut Input")

    def _value(self):
        return {"Type": "ExtensionInput"}


class PhotoExportCheck(Store):
    def __init__(self):
        # Reuse dictionary/Text builders without a bound iCloud folder action.
        Shortcut.__init__(self, "Periwinkle – Mac Photo Export Check", color=BLUE)

    def write(self, path):
        super().write(path)
        with open(path, "rb") as file:
            workflow = plistlib.load(file)
        # The operational builders take no input. This diagnostic must declare
        # Files explicitly, matching the input option used in the Mac editor.
        workflow["WFWorkflowInputContentItemClasses"] = ["WFGenericFileContentItem"]
        workflow["WFWorkflowOutputContentItemClasses"] = [
            "WFStringContentItem", "WFImageContentItem", "WFPhotoMediaContentItem",
            "WFGenericFileContentItem"]
        with open(path, "wb") as file:
            plistlib.dump(workflow, file, fmt=plistlib.FMT_BINARY)


def photo_export_experiment():
    s = PhotoExportCheck()
    request = s.add("detect.dictionary", output="Export request", WFInput=attachment(ShortcutInput()))
    album = text_field(s, request, "albumName")
    name = text_field(s, request, "photoName")
    mode = text_field(s, request, "mode")
    all_photos = find_album_photos(s, album)
    album_count = s.add("count", output="Album count", Input=attachment(all_photos), WFCountType="Items")
    # Preserve the Photos token in the output. The intended next step is CLI
    # image serialization; a literal filename is not usable image data.
    matches = find_album_photos(s, album, name)
    match_count = s.add("count", output="Filename matches", Input=attachment(matches), WFCountType="Items")
    inspect = s.if_(mode, IS, string="inspect")
    report = s.compose("Requested album: ", album, "\nRequested photo: ", name,
                       "\nAlbum count: ", album_count, "\nFilename matches: ", match_count)
    s.add("output", WFOutput=text(report))
    s.else_(inspect)
    single = s.if_(match_count, IS, number=1)
    s.add("output", WFOutput=text(matches))
    s.else_(single)
    report = s.compose("Export refused: expected one photo, found ", match_count)
    s.add("output", WFOutput=text(report))
    s.end_if(single)
    s.end_if(inspect)
    return s


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", help="Unsigned .shortcut path")
    args = parser.parse_args()
    photo_export_experiment().write(args.output)
