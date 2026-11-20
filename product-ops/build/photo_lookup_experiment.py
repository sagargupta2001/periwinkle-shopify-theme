"""Read-only iPhone check: can Find Photos retrieve this Shared Album?

Not part of operational releases. No image files, records, links or caches are
saved. Run on the operator's phone before integrating any photo lookup.
"""
import argparse

from build import BLUE, Store
from shortcutlib import IS, NO_VALUE, Shortcut, attachment, named, text


class PhotoCheck(Store):
    def __init__(self):
        # Reuse prompt helpers without introducing an account-bound folder action.
        Shortcut.__init__(self, "Periwinkle – Photo Lookup Check", color=BLUE)


def photo_lookup_experiment():
    s = PhotoCheck()
    s.alert("Shared Album access check",
            "This test reads Photos only. It never saves pictures or changes the register. "
            "Enter the exact Shared Album name. An ordinary album with the same name would make this test inconclusive.")
    album = s.ask("Exact Shared Album name", default="Periwinkle")
    album = s.add("text.trimwhitespace", output="Album name", WFInput=text(album))
    empty = s.if_(album, NO_VALUE)
    s.stop()
    s.end_if(empty)
    mode = s.pick("What should we check?", ["Browse Shared Album", "Find filename in Shared Album"])
    filters = [{"Property": "Album", "Operator": 4, "Removable": True,
                "Values": {"Enumeration": {"WFSerializationType": "WFStringSubstitutableState",
                                           "Value": text(album)}}}]

    def find(rows):
        return s.add("filter.photos", output="Album photos", WFContentItemInputParameter="Library",
                     WFContentItemFilter={"WFSerializationType": "WFContentPredicateTableTemplate", "Value": {
                         "WFActionParameterFilterPrefix": 1, "WFContentPredicateBoundedDate": False,
                         "WFActionParameterFilterTemplates": rows}}, WFContentItemLimitEnabled=False)

    browse = s.if_(mode, IS, string="Browse Shared Album")
    result = find(filters)
    s.add("setvariable", WFVariableName="photoMatches", WFInput=attachment(result))
    s.else_(browse)
    filename = s.ask("Photo name reported by the first check (exactly as shown)")
    filename = s.add("text.trimwhitespace", output="Filename", WFInput=text(filename))
    empty = s.if_(filename, NO_VALUE)
    s.stop()
    s.end_if(empty)
    result = find(filters + [{"Property": "Name", "Operator": 4, "Removable": True,
                              "Values": {"String": text(filename)}}])
    s.add("setvariable", WFVariableName="photoMatches", WFInput=attachment(result))
    s.end_if(browse)
    count = s.add("count", output="Matches", Input=attachment(named("photoMatches")), WFCountType="Items")
    s.alert("Lookup result", "Album: ", album, "\nPhotos returned: ", count,
            "\n\nZero results or an album-not-found error means this route has not passed. "
            "A result is only useful if it is from the actual Shared Album.")
    empty = s.if_(count, IS, number=0)
    s.stop()
    s.end_if(empty)
    selected = s.choose("Choose one photo to inspect", "photoMatches")
    name = s.add("properties.images", output="Photo filename", WFInput=attachment(selected), WFContentItemPropertyName="Name")
    taken = s.add("properties.images", output="Photo date", WFInput=attachment(selected), WFContentItemPropertyName="Date Taken")
    s.alert("Photo metadata", "Filename: ", name, "\nDate taken: ", taken,
            "\n\nUse the name exactly as shown, even if it has no extension. Rerun Find filename in Shared Album. "
            "Do not delete an existing product photo for testing.")
    s.add("previewdocument", WFInput=attachment(selected))
    return s


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", help="Unsigned .shortcut path; sign with Apple's shortcuts sign tool")
    photo_lookup_experiment().write(parser.parse_args().output)
