"""Shared Album previews using metadata-only SKU links, never image copies."""
from shortcutlib import CONTAINS, HAS_VALUE, IS, NO_VALUE, REPEAT_ITEM, attachment, named, text

PHOTO_DATE_FORMAT = "yyyy-MM-dd'T'HH:mm:ss.SSSZZZZZ"
DATE_FRACTION_RULE = r"\.[0-9]+(?=(?:Z|[+-][0-9]{2}:[0-9]{2})$)"
# Proposed names approved for the new testing setup. The client must create
# these Shared Albums and invite the operator before new intake can be verified.
CATEGORY_ALBUMS = {
    "SAR": "Periwinkle - Sarees",
    "SKZ": "Periwinkle - Salwar Kameez",
    "MIN": "Periwinkle - Miniatures",
    "RED": "Periwinkle - Readymades",
    "DUP": "Periwinkle - Dupattas",
    "HOM": "Periwinkle - Home Decor",
    "JEW": "Periwinkle - Jewellery",
}


def text_field(s, dictionary, key):
    """Give dictionary values a concrete Text type before iOS configures If."""
    value = s.field(dictionary, key)
    return s.compose(value, output=key + " text")


def photo_date(s, photo):
    date = s.add("properties.images", output="Date taken", WFInput=attachment(photo), WFContentItemPropertyName="Date Taken")
    s.add("setvariable", WFVariableName="photoDateKey", WFInput=attachment(s.literal("")))
    exists = s.if_(date, HAS_VALUE)
    formatted = s.add("format.date", output="Photo date key", WFDate=text(date),
                      WFDateFormatStyle="Custom", WFDateFormat=PHOTO_DATE_FORMAT)
    s.add("setvariable", WFVariableName="photoDateKey", WFInput=attachment(formatted))
    s.end_if(exists)
    return date, named("photoDateKey")


def find_album_photos(s, album, name=None):
    """Never fall back to a personal-library photo if album membership changes."""
    rows = [{"Property": "Album", "Operator": 4, "Removable": True,
             "Values": {"Enumeration": {"WFSerializationType": "WFStringSubstitutableState", "Value": text(album)}}}]
    if name is not None:
        rows.append({"Property": "Name", "Operator": 4, "Removable": True, "Values": {"String": text(name)}})
    return s.add("filter.photos", output="Shared Album photos", WFContentItemInputParameter="Library",
                 WFContentItemFilter={"WFSerializationType": "WFContentPredicateTableTemplate", "Value": {
                     "WFActionParameterFilterPrefix": 1, "WFContentPredicateBoundedDate": False,
                     "WFActionParameterFilterTemplates": rows}}, WFContentItemLimitEnabled=False)


def date_match_key(s, date):
    # Shared Album copies may report whole seconds even when the original
    # selection had fractional precision. Keep the saved original unchanged.
    return s.add("text.replace", output="Whole-second photo date", WFInput=text(date),
                 WFReplaceTextFind=DATE_FRACTION_RULE, WFReplaceTextReplace="",
                 WFReplaceTextRegularExpression=True, WFReplaceTextCaseSensitive=True)


def read_metadata_file(s, directory, lower, prefix):
    # Never Get File on a path that might not exist. On iPhone a missing-path
    # result/blank placeholder passed the old Has Value gate and reached Photos.
    # Only a positively matched, enumerated file can set this explicit flag.
    s.add("setvariable", WFVariableName=prefix + "Found", WFInput=attachment(s.literal("no")))
    s.add("setvariable", WFVariableName=prefix + "FolderFound", WFInput=attachment(s.literal("no")))
    folders = s.add("file.getfoldercontents", output="Root contents", WFFolder=attachment(s.root), Recursive=False)
    outer = s.each(folders)
    folder_name = s.add("properties.files", output="Folder name", WFInput=attachment(REPEAT_ITEM), WFContentItemPropertyName="Name")
    folder_match = s.if_(folder_name, IS, string=directory)
    s.add("setvariable", WFVariableName=prefix + "Folder", WFInput=attachment(REPEAT_ITEM))
    s.add("setvariable", WFVariableName=prefix + "FolderFound", WFInput=attachment(s.literal("yes")))
    s.end_if(folder_match)
    s.end_each(outer)
    # Separate loops: a plain Repeat Item in a nested loop still names the outer
    # item on iPhone. Enumerate files only after the folder loop has finished.
    folder_exists = s.if_(named(prefix + "FolderFound"), IS, string="yes")
    files = s.add("file.getfoldercontents", output="Photo link files", WFFolder=attachment(named(prefix + "Folder")), Recursive=False)
    inner = s.each(files)
    filename = s.add("properties.files", output="Link filename", WFInput=attachment(REPEAT_ITEM), WFContentItemPropertyName="Name")
    match = s.add("text.match", output="Matching link filename", text=text(filename),
                  WFMatchTextPattern=text("^", lower, "(?:\\.json)?$"), WFMatchTextCaseSensitive=True)
    count = s.add("count", output="Filename matches", Input=attachment(match), WFCountType="Items")
    file_match = s.if_(count, IS, number=1)
    s.add("setvariable", WFVariableName=prefix + "File", WFInput=attachment(REPEAT_ITEM))
    s.add("setvariable", WFVariableName=prefix + "Found", WFInput=attachment(s.literal("yes")))
    s.end_if(file_match)
    s.end_each(inner)
    s.end_if(folder_exists)
    return named(prefix + "File"), named(prefix + "Found")


def read_photo_link(s, lower):
    return read_metadata_file(s, "photo-links", lower, "photoLink")

def show_linked_photo(s, lower, *, explain_missing=True):
    """Re-query membership each run; zero matches never shows an old preview."""
    resolve_photo_reference(s, lower, allow_choose=False, notify=False)
    file, found = read_photo_link(s, lower)
    exists = s.if_(found, IS, string="yes")
    link = s.add("detect.dictionary", output="Photo link", WFInput=attachment(file))
    source = text_field(s, link, "source")
    pending = s.if_(source, IS, string="client_intake_pending")
    s.alert("Photo is still being linked", "The posted photo has not been confirmed yet. The client can use Fix Product → Finish photo linking after the album syncs. Do not submit the product again.")
    s.else_(pending)
    album, name, taken = text_field(s, link, "albumName"), text_field(s, link, "photoName"), text_field(s, link, "photoTakenAt")
    fields = s.compose(album, "\n", name, "\n", taken)
    valid = s.add("text.match", output="Complete photo link", text=text(fields),
                  WFMatchTextPattern=r"\A[^\r\n]+\n[^\r\n]+\n[^\r\n]+\Z", WFMatchTextCaseSensitive=True)
    count = s.add("count", output="Complete link matches", Input=attachment(valid), WFCountType="Items")
    complete = s.if_(count, IS, number=1)
    photos = find_album_photos(s, album, name)
    filename_count = s.add("count", output="Filename matches", Input=attachment(photos), WFCountType="Items")
    expected_date = date_match_key(s, taken)
    # Use a genuine empty match collection, not a blank Text item that could
    # count as a phantom photo after appending the first matching asset.
    empty = s.add("text.match", output="Empty photo collection", text=text(""),
                  WFMatchTextPattern=r"(?!)", WFMatchTextCaseSensitive=True)
    s.add("setvariable", WFVariableName="previewPhotos", WFInput=attachment(empty))
    s.add("setvariable", WFVariableName="candidatePhotoDates", WFInput=attachment(empty))
    candidates = s.each(photos)
    _, date = photo_date(s, REPEAT_ITEM)
    s.add("appendvariable", WFVariableName="candidatePhotoDates", WFInput=attachment(date))
    actual_date = date_match_key(s, date)
    same_date = s.if_(actual_date, IS, string=text(expected_date))
    s.add("appendvariable", WFVariableName="previewPhotos", WFInput=attachment(REPEAT_ITEM))
    s.end_if(same_date)
    s.end_each(candidates)
    count = s.add("count", output="Photo matches", Input=attachment(named("previewPhotos")), WFCountType="Items")
    missing = s.if_(count, IS, number=0)
    no_filename = s.if_(filename_count, IS, number=0)
    s.alert("Photo unavailable", "No photo named ", name, " was found in ", album,
            ". Check that the selected photo was posted to that Shared Album and has synced. "
            "Do not create the product again. Stock records are unchanged.")
    s.else_(no_filename)
    dates = s.add("text.combine", output="Album photo dates", text=attachment(named("candidatePhotoDates")), WFTextSeparator="New Lines")
    s.alert("Photo date differs", "Found ", name, " in ", album, ", but its date did not match.\nRecorded: ", taken,
            "\nAlbum date(s): ", dates, "\n\nKeep this message for troubleshooting. Do not create the product again. Stock records are unchanged.")
    s.end_if(no_filename)
    s.else_(missing)
    single = s.if_(count, IS, number=1)
    s.add("previewdocument", WFInput=attachment(named("previewPhotos")))
    s.else_(single)
    s.alert("Several photos share that name", "Choose the correct photo from this Shared Album. No image is selected automatically.")
    chosen = s.choose("Choose the product photo", "previewPhotos")
    s.add("previewdocument", WFInput=attachment(chosen))
    s.end_if(single)
    s.end_if(missing)
    s.else_(complete)
    s.alert("Photo link needs updating", "The saved link is incomplete. Use Link or change photo to select it again. No photo search was run.")
    s.end_if(complete)
    s.end_if(pending)
    s.else_(exists)
    if explain_missing:
        s.alert("Photo not linked yet", "Use Link or change photo in Register's product actions, "
                "or View or link product photo in Work on Product. Linking saves only photo metadata.")
    s.end_if(exists)


def link_product_photo(s, lower, sku):
    """User confirms one album photo once; persist just its exact Name property."""
    album = s.ask("Exact Shared Album name (for example, Miniatures Available)")
    album = s.add("text.trimwhitespace", output="Shared Album name", WFInput=text(album))
    valid = s.add("text.match", output="Valid album name", text=text(album),
                  WFMatchTextPattern=r'^[^"\\\x00-\x1f]+$', WFMatchTextCaseSensitive=True)
    invalid = s.if_(valid, NO_VALUE)
    s.alert("Check the album name", "Enter a name without double quotes, backslashes or line breaks. No link has been saved.")
    s.stop()
    s.end_if(invalid)
    photos = find_album_photos(s, album)
    s.add("setvariable", WFVariableName="linkPhotos", WFInput=attachment(photos))
    s.stop_if_empty("linkPhotos", "No album photos found", "Check the exact Shared Album name, Photos access and sync. No link has been saved.")
    selected = s.choose(text("Choose the photo for ", sku), "linkPhotos")
    name = s.add("properties.images", output="Photo name", WFInput=attachment(selected), WFContentItemPropertyName="Name")
    raw_date, date = photo_date(s, selected)
    missing_date = s.if_(raw_date, NO_VALUE)
    s.alert("Photo date is missing", "This photo cannot be safely linked by name and date. No link has been saved.")
    s.stop()
    s.end_if(missing_date)
    valid = s.add("text.match", output="Valid photo name", text=text(name),
                  WFMatchTextPattern=r'^[^"\\\x00-\x1f]+$', WFMatchTextCaseSensitive=True)
    invalid = s.if_(valid, NO_VALUE)
    s.alert("Photo name cannot be linked", "The photo name is empty or contains unsupported characters. No link has been saved.")
    s.stop()
    s.end_if(invalid)
    # Persist the exact extensionless Name returned by Photos. Do not normalize it.
    s.add("previewdocument", WFInput=attachment(selected))
    answer = s.pick(text("Link this photo to ", sku, "?\nAlbum: ", album, "\nPhoto: ", name),
                    ["Save photo link", "Cancel"])
    save = s.if_(answer, IS, string="Save photo link")
    content = s.compose('{"version":1,"sku":"', sku, '","albumName":"', album, '","photoName":"', name,
                        '","photoTakenAt":"', date, '"}')
    s.save(content, "photo-links/", lower, ".json")
    s.alert("Photo link saved", "Only the album, photo name and date were saved. The image stays in the Shared Album. "
            "Future previews will check that album again.")
    s.end_if(save)


def capture_intake_photo(s, photos, sku):
    """Capture the first supplied photo's reference; never ask the operator to link."""
    code = s.add("text.match", output="Product category", text=text(sku),
                 WFMatchTextPattern=r"(?<=^PBS-)[A-Z]{3}", WFMatchTextCaseSensitive=True)
    code = s.compose(code)
    s.add("setvariable", WFVariableName="intakeAlbum", WFInput=attachment(s.literal("")))
    for category, album in CATEGORY_ALBUMS.items():
        matching = s.if_(code, IS, string=category)
        s.add("setvariable", WFVariableName="intakeAlbum", WFInput=attachment(s.literal(album)))
        s.end_if(matching)
    unknown = s.if_(named("intakeAlbum"), IS, string="")
    answer = s.ask("Exact Shared Album name you will choose when posting these photos")
    trimmed = s.add("text.trimwhitespace", output="Intake album", WFInput=text(answer))
    s.add("setvariable", WFVariableName="intakeAlbum", WFInput=attachment(trimmed))
    s.end_if(unknown)
    valid = s.add("text.match", output="Valid intake album", text=text(named("intakeAlbum")),
                  WFMatchTextPattern=r'^[^"\\\x00-\x1f]+$', WFMatchTextCaseSensitive=True)
    invalid = s.if_(valid, NO_VALUE)
    s.alert("Check the album name", "Enter the exact Shared Album name without double quotes, backslashes or line breaks. Nothing has been saved.")
    s.stop()
    s.end_if(invalid)

    s.add("setvariable", WFVariableName="intakePhotoCaptured", WFInput=attachment(s.literal("no")))
    loop = s.each(photos)
    first = s.if_(named("intakePhotoCaptured"), IS, string="no")
    name = s.add("properties.images", output="Intake photo name", WFInput=attachment(REPEAT_ITEM), WFContentItemPropertyName="Name")
    raw_date, date = photo_date(s, REPEAT_ITEM)
    valid = s.add("text.match", output="Valid intake photo name", text=text(name),
                  WFMatchTextPattern=r'^[^"\\\x00-\x1f]+$', WFMatchTextCaseSensitive=True)
    missing = s.if_(valid, NO_VALUE)
    s.alert("Photo reference unavailable", "Choose a photo with a name that has no double quotes, backslashes or line breaks. Nothing has been saved.")
    s.stop()
    s.end_if(missing)
    missing = s.if_(raw_date, NO_VALUE)
    s.alert("Photo date unavailable", "Choose a photo with a Date Taken value so it can be identified later. Nothing has been saved.")
    s.stop()
    s.end_if(missing)
    s.add("setvariable", WFVariableName="intakePhotoName", WFInput=attachment(name))
    s.add("setvariable", WFVariableName="intakePhotoDate", WFInput=attachment(date))
    s.add("setvariable", WFVariableName="intakePhotoCaptured", WFInput=attachment(s.literal("yes")))
    s.end_if(first)
    s.end_each(loop)
    return named("intakeAlbum"), named("intakePhotoName"), named("intakePhotoDate")


SNAPSHOT_SEPARATOR = "␟"


def capture_album_snapshot(s, album):
    """Remember names already in the target album, not copies of the images."""
    photos = find_album_photos(s, album)
    count = s.add("count", output="Album before count", Input=attachment(photos), WFCountType="Items")
    empty = s.if_(count, IS, number=0)
    snapshot = s.literal(SNAPSHOT_SEPARATOR + SNAPSHOT_SEPARATOR)
    s.add("setvariable", WFVariableName="intakeBeforeNames", WFInput=attachment(snapshot))
    s.else_(empty)
    names = s.add("properties.images", output="Existing album names", WFInput=attachment(photos), WFContentItemPropertyName="Name")
    joined = s.add("text.combine", output="Existing album names", text=attachment(names),
                   WFTextSeparator="New Lines")
    separated = s.add("text.replace", output="Snapshot name boundaries", WFInput=text(joined),
                      WFReplaceTextFind=r"\r?\n", WFReplaceTextReplace=SNAPSHOT_SEPARATOR,
                      WFReplaceTextRegularExpression=True, WFReplaceTextCaseSensitive=True)
    safe = s.json_safe(separated)
    snapshot = s.compose(SNAPSHOT_SEPARATOR, safe, SNAPSHOT_SEPARATOR)
    s.add("setvariable", WFVariableName="intakeBeforeNames", WFInput=attachment(snapshot))
    s.end_if(empty)
    return named("intakeBeforeNames")


def save_intake_photo_link(s, lower, sku, album, name, date, before_names):
    """Persist a pending reference and a small resumable album-name snapshot."""
    snapshot = s.compose('{"version":1,"state":"pending","beforeNames":"', before_names, '"}')
    s.save(snapshot, "photo-pending/", lower, ".json")
    content = s.compose('{"version":1,"sku":"', sku, '","albumName":"', album, '","photoName":"', name,
                        '","photoTakenAt":"', date, '","source":"client_intake_pending"}')
    s.save(content, "photo-links/", lower, ".json")


def save_confirmed_photo(s, lower, sku, album, photo):
    name = s.add("properties.images", output="Posted photo name", WFInput=attachment(photo), WFContentItemPropertyName="Name")
    raw_date, date = photo_date(s, photo)
    valid = s.add("text.match", output="Valid posted name", text=text(name),
                  WFMatchTextPattern=r'^[^"\\\x00-\x1f]+$', WFMatchTextCaseSensitive=True)
    invalid = s.if_(valid, NO_VALUE)
    s.alert("Photo reference needs attention", "The posted photo has no usable name. The product is saved; do not submit it again.")
    s.stop()
    s.end_if(invalid)
    missing = s.if_(raw_date, NO_VALUE)
    s.alert("Photo reference needs attention", "The posted photo has no date. The product is saved; do not submit it again.")
    s.stop()
    s.end_if(missing)
    content = s.compose('{"version":1,"sku":"', sku, '","albumName":"', album, '","photoName":"', name,
                        '","photoTakenAt":"', date, '","source":"shared_album_confirmed"}')
    s.save(content, "photo-links/", lower, ".json")


def resolve_photo_reference(s, lower, *, allow_choose, notify):
    """Confirm the actual album asset after posting, including upload renaming."""
    s.add("setvariable", WFVariableName="photoResolved", WFInput=attachment(s.literal("no")))
    file, found = read_photo_link(s, lower)
    exists = s.if_(found, IS, string="yes")
    link = s.add("detect.dictionary", output="Pending photo reference", WFInput=attachment(file))
    source, sku, album = text_field(s, link, "source"), text_field(s, link, "sku"), text_field(s, link, "albumName")
    if allow_choose:
        pending = s.if_(source, IS, string="client_intake_pending")
        snapshot_file, snapshot_found = read_metadata_file(s, "photo-pending", lower, "photoSnapshot")
        has_snapshot = s.if_(snapshot_found, IS, string="yes")
        snapshot = s.add("detect.dictionary", output="Album snapshot", WFInput=attachment(snapshot_file))
        state, before_names = text_field(s, snapshot, "state"), text_field(s, snapshot, "beforeNames")
        is_pending = s.if_(state, IS, string="pending")
        valid = s.add("text.match", output="Valid album snapshot", text=text(before_names),
                      WFMatchTextPattern=r"\A␟[^\r\n]*␟\Z", WFMatchTextCaseSensitive=True)
        count = s.add("count", output="Snapshot matches", Input=attachment(valid), WFCountType="Items")
        valid_snapshot = s.if_(count, IS, number=1)
        empty = s.add("text.match", output="Empty new-photo list", text=text(""), WFMatchTextPattern=r"(?!)", WFMatchTextCaseSensitive=True)
        s.add("setvariable", WFVariableName="newAlbumPhotos", WFInput=attachment(empty))
        current = find_album_photos(s, album)
        loop = s.each(current)
        name = s.add("properties.images", output="Album photo name", WFInput=attachment(REPEAT_ITEM), WFContentItemPropertyName="Name")
        safe = s.json_safe(name)
        already_present = s.if_(before_names, CONTAINS, string=text(SNAPSHOT_SEPARATOR, safe, SNAPSHOT_SEPARATOR))
        s.else_(already_present)
        s.add("appendvariable", WFVariableName="newAlbumPhotos", WFInput=attachment(REPEAT_ITEM))
        s.end_if(already_present)
        s.end_each(loop)
        count = s.add("count", output="New album photos", Input=attachment(named("newAlbumPhotos")), WFCountType="Items")
        single = s.if_(count, IS, number=1)
        # A separate one-item loop binds the actual photo without a client picker.
        one = s.each(named("newAlbumPhotos"))
        s.add("setvariable", WFVariableName="postedProductPhoto", WFInput=attachment(REPEAT_ITEM))
        s.end_each(one)
        if allow_choose:
            s.add("previewdocument", WFInput=attachment(named("postedProductPhoto")))
            confirm = s.pick(text("Confirm the photo just posted for ", sku), ["Confirm photo", "Finish later"])
            confirmed = s.if_(confirm, IS, string="Confirm photo")
            s.add("setvariable", WFVariableName="photoResolved", WFInput=attachment(s.literal("yes")))
            s.end_if(confirmed)
        s.else_(single)
        nonempty = s.if_(count, IS, number=0)
        s.else_(nonempty)
        if allow_choose:
            selected = s.choose(text("Choose the newly posted photo for ", sku), "newAlbumPhotos")
            s.add("previewdocument", WFInput=attachment(selected))
            confirm = s.pick("Use this posted photo?", ["Confirm photo", "Finish later"])
            confirmed = s.if_(confirm, IS, string="Confirm photo")
            s.add("setvariable", WFVariableName="postedProductPhoto", WFInput=attachment(selected))
            s.add("setvariable", WFVariableName="photoResolved", WFInput=attachment(s.literal("yes")))
            s.end_if(confirmed)
        s.end_if(nonempty)
        s.end_if(single)
        ready = s.if_(named("photoResolved"), IS, string="yes")
        save_confirmed_photo(s, lower, sku, album, named("postedProductPhoto"))
        # Retain a tiny completion marker rather than a growing album-name snapshot.
        s.save(s.literal('{"version":1,"state":"complete"}'), "photo-pending/", lower, ".json")
        s.end_if(ready)
        s.end_if(valid_snapshot)
        s.end_if(is_pending)
        s.end_if(has_snapshot)
        if notify:
            unresolved = s.if_(named("photoResolved"), IS, string="no")
            s.alert("Photo is still syncing", "The product is saved. Wait for the posted photo to appear, then use Fix Product → Finish photo linking before creating another product in this album. Do not create this product again.")
            s.end_if(unresolved)
        s.end_if(pending)

    # One-off repair for an exact album name explicitly verified by the user.
    verified = s.if_(source, IS, string="verified_shared_name")
    name = text_field(s, link, "photoName")
    candidates = find_album_photos(s, album, name)
    count = s.add("count", output="Verified-name matches", Input=attachment(candidates), WFCountType="Items")
    single = s.if_(count, IS, number=1)
    one = s.each(candidates)
    s.add("setvariable", WFVariableName="verifiedProductPhoto", WFInput=attachment(REPEAT_ITEM))
    s.end_each(one)
    save_confirmed_photo(s, lower, sku, album, named("verifiedProductPhoto"))
    s.end_if(single)
    s.end_if(verified)
    s.end_if(exists)
