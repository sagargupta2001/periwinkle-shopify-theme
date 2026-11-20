"""Record safety and strict album membership for linked product photos."""
import json
import re
import unittest

from build import BLUE, CATEGORIES, Store, new_product
from photo_links import CATEGORY_ALBUMS, capture_album_snapshot, capture_intake_photo, link_product_photo, resolve_photo_reference, save_intake_photo_link, show_linked_photo
from shortcutlib import named
from test_build import action_name


class PreviewHarness:
    """Execute the preview's generated control flow with a small fake filesystem.

    No Photos or iCloud access. Empty Text deliberately counts as an item and
    Has Value accepts it, so missing-link safety cannot depend on those quirks.
    """
    def __init__(self, children, variables=None, photos=None):
        self.root = {"name": "root", "children": children}
        self.variables = dict(variables or {})
        self.outputs, self.searches, self.alerts, self.saves = {}, [], [], []
        self.photos, self.previews = list(photos or []), []
        self.exited = False

    def value(self, item):
        if not isinstance(item, dict):
            return item
        kind = item.get("WFSerializationType")
        if kind == "WFStringSubstitutableState":
            return self.value(item["Value"])
        if kind == "WFTextTokenAttachment":
            token = item["Value"]
            return self.outputs.get(token.get("OutputUUID")) if token["Type"] == "ActionOutput" else self.variables.get(token["VariableName"])
        if kind == "WFTextTokenString":
            value = item["Value"]["string"]
            for position, token in sorted(item["Value"]["attachmentsByRange"].items(), key=lambda x: int(re.findall(r"\d+", x[0])[0]), reverse=True):
                index = int(re.findall(r"\d+", position)[0])
                resolved = self.value({"WFSerializationType": "WFTextTokenAttachment", "Value": token})
                display = "\n".join(str(v) for v in resolved) if isinstance(resolved, list) else ("" if resolved is None else str(resolved))
                value = value[:index] + display + value[index + 1:]
            return value
        if item.get("Type") == "Variable" and "Variable" in item:
            return self.value(item["Variable"])
        return item

    def run(self, shortcut):
        actions, blocks, stack = shortcut.actions, {}, []
        for index, action in enumerate(actions):
            p = action["WFWorkflowActionParameters"]
            if "GroupingIdentifier" not in p:
                continue
            mode = p["WFControlFlowMode"]
            if mode == 0:
                stack.append(index); blocks[index] = [None, None]
            elif mode == 1:
                blocks[stack[-1]][0] = index
            else:
                blocks[stack.pop()][1] = index

        def execute(start, end, repeat_depth=0):
            index = start
            while index < end:
                a = actions[index]; p = a["WFWorkflowActionParameters"]; name = action_name(a)
                out = None
                if name == "choosefrommenu":
                    _, finish = blocks[index]
                    choice = p["WFMenuItems"][0]
                    self.outputs[actions[finish]["WFWorkflowActionParameters"]["UUID"]] = choice
                    index = finish + 1
                    continue
                if name == "conditional":
                    middle, finish = blocks[index]
                    actual = self.value(p["WFInput"])
                    expected = self.value(p.get("WFNumberValue", p.get("WFConditionalActionString")))
                    condition = p["WFCondition"]
                    if condition == 4:
                        passed = actual == expected
                    elif condition == 99:
                        passed = expected in actual
                    else:
                        passed = actual is not None if condition == 100 else actual is None
                    if passed:
                        execute(index + 1, middle if middle is not None else finish, repeat_depth)
                    elif middle is not None:
                        execute(middle + 1, finish, repeat_depth)
                    index = finish + 1
                    continue
                if name == "repeat.each":
                    _, finish = blocks[index]
                    # Apple gives nested loops distinct Repeat Item names. A
                    # plain Repeat Item reference remains bound to the outer loop.
                    repeat_name = "Repeat Item" if repeat_depth == 0 else f"Repeat Item {repeat_depth}"
                    previous = self.variables.get(repeat_name)
                    for value in self.value(p["WFInput"]) or []:
                        self.variables[repeat_name] = value
                        execute(index + 1, finish, repeat_depth + 1)
                    self.variables[repeat_name] = previous
                    index = finish + 1
                    continue
                if name == "file":
                    out = self.root
                elif name == "file.getfoldercontents":
                    out = self.value(p["WFFolder"])["children"]
                elif name == "properties.files":
                    out = self.value(p["WFInput"])["name"]
                elif name == "properties.images":
                    photo = self.value(p["WFInput"])
                    key = "name" if p["WFContentItemPropertyName"] == "Name" else "date"
                    out = [item[key] for item in photo] if isinstance(photo, list) else photo[key]
                elif name == "format.date":
                    out = self.value(p["WFDate"])
                elif name == "gettext":
                    out = self.value(p["WFTextActionText"])
                elif name == "setvariable":
                    out = self.value(p["WFInput"]); self.variables[p["WFVariableName"]] = out
                elif name == "text.match":
                    out = re.findall(self.value(p["WFMatchTextPattern"]), self.value(p["text"]) or "")
                elif name == "text.replace":
                    out = re.sub(self.value(p["WFReplaceTextFind"]), self.value(p["WFReplaceTextReplace"]), self.value(p["WFInput"]))
                elif name == "text.combine":
                    separator = p.get("WFTextCustomSeparator", "\n") if p.get("WFTextSeparator") == "Custom" else "\n"
                    out = separator.join(self.value(p["text"]) or [])
                elif name == "appendvariable":
                    out = list(self.variables.get(p["WFVariableName"]) or [])
                    out.append(self.value(p["WFInput"]))
                    self.variables[p["WFVariableName"]] = out
                elif name == "count":
                    value = self.value(p["Input"])
                    out = len(value) if isinstance(value, list) else (0 if value is None else 1)
                elif name == "detect.dictionary":
                    out = self.value(p["WFInput"])["data"]
                elif name == "getvalueforkey":
                    out = self.value(p["WFInput"]).get(p["WFDictionaryKey"], "")
                elif name == "filter.photos":
                    self.searches.append(p)
                    rows = p["WFContentItemFilter"]["Value"]["WFActionParameterFilterTemplates"]
                    out = [photo for photo in self.photos if all(
                        photo["album" if row["Property"] == "Album" else "name"] == self.value(next(iter(row["Values"].values())))
                        for row in rows)]
                elif name == "previewdocument":
                    preview = self.value(p["WFInput"])
                    self.previews.append(preview if isinstance(preview, list) else [preview])
                elif name == "setitemname":
                    out = {"name": p["WFName"], "data": self.value(p["WFInput"])}
                elif name == "documentpicker.save":
                    out = self.value(p["WFInput"])
                    path = self.value(p["WFFileDestinationPath"])
                    self.saves.append((path, out["data"]))
                    parts = path.split("/"); folder = self.root
                    for part in parts[:-1]:
                        existing = next((f for f in folder["children"] if f["name"] == part), None)
                        if existing is None:
                            existing = {"name": part, "children": []}; folder["children"].append(existing)
                        folder = existing
                    file = next((f for f in folder["children"] if f["name"] == parts[-1]), None)
                    if file is None:
                        file = {"name": parts[-1]}; folder["children"].append(file)
                    file["data"] = json.loads(out["data"])
                elif name == "alert":
                    self.alerts.append(self.value(p["WFAlertActionTitle"]))
                else:
                    raise AssertionError(f"Unexpected executed action: {name}")
                self.outputs[p["UUID"]] = out
                index += 1
        execute(0, len(actions))


class PhotoLinks(unittest.TestCase):
    def test_new_product_saves_reference_before_sharing_without_another_photo_picker(self):
        actions = new_product({"filename": "test"}).actions
        share = next(i for i, a in enumerate(actions) if action_name(a) == "share")
        writes = [i for i, a in enumerate(actions) if action_name(a) == "documentpicker.save"
                  and a["WFWorkflowActionParameters"]["WFFileDestinationPath"]["Value"]["string"].startswith("photo-links/")]
        self.assertTrue(any(i < share for i in writes))
        self.assertTrue(any(i > share for i in writes))
        self.assertNotIn("choosefromlist", [action_name(a) for a in actions[:share]])

    def test_intake_automatically_saves_first_photo_reference_for_every_category(self):
        self.assertEqual(set(CATEGORY_ALBUMS), {code for _, code in CATEGORIES})
        for code, album in CATEGORY_ALBUMS.items():
            with self.subTest(category=code):
                s = Store("Intake", {"filename": "test"}, BLUE)
                sku = s.literal(f"PBS-{code}-001")
                reference = capture_intake_photo(s, named("selectedPhotos"), sku)
                snapshot = capture_album_snapshot(s, reference[0])
                save_intake_photo_link(s, s.literal(f"pbs-{code.lower()}-001"), sku, *reference, snapshot)
                photos = [{"name": "IMG_0340", "date": "2026-11-19T18:17:32.000+05:30"},
                          {"name": "IMG_0341", "date": "2026-11-19T18:17:33.000+05:30"}]
                harness = PreviewHarness([], {"selectedPhotos": photos})
                harness.run(s)
                self.assertEqual(len(harness.saves), 2)
                path, content = harness.saves[1]
                self.assertEqual(path, f"photo-links/pbs-{code.lower()}-001.json")
                data = json.loads(content)
                self.assertEqual(data["albumName"], album)
                self.assertEqual(data["photoName"], "IMG_0340")
                self.assertEqual(data["photoTakenAt"], photos[0]["date"])
                self.assertEqual(data["source"], "client_intake_pending")

    def inspect(self, children, variables=None, photos=None):
        s = Store("Preview", {"filename": "test"}, BLUE)
        show_linked_photo(s, s.literal("pbs-min-001"), explain_missing=False)
        harness = PreviewHarness(children, variables, photos)
        harness.run(s)
        return harness

    def pending_fixture(self, snapshot):
        link = {"sku": "PBS-MIN-001", "albumName": "Periwinkle - Sarees", "photoName": "IMG_0499",
                "photoTakenAt": "2026-11-19T21:32:28.548+05:30", "source": "client_intake_pending"}
        folders = [{"name": "photo-links", "children": [{"name": "pbs-min-001.json", "data": link}]}]
        if snapshot is not None:
            folders.append({"name": "photo-pending", "children": [{"name": "pbs-min-001.json", "data": snapshot}]})
        return folders

    def finish_pending(self, folders, photos):
        s = Store("Finish", {"filename": "test"}, BLUE)
        resolve_photo_reference(s, s.literal("pbs-min-001"), allow_choose=True, notify=True)
        harness = PreviewHarness(folders, photos=photos)
        harness.run(s)
        return harness

    def test_newly_posted_uuid_name_and_changed_date_replace_the_original_reference(self):
        before = {"version": 1, "state": "pending", "beforeNames": "␟old-photo␟"}
        old = {"album": "Periwinkle - Sarees", "name": "old-photo", "date": "2020-01-01T00:00:00.000+05:30"}
        posted = {"album": old["album"], "name": "7C8E0E8D-1633-49BF-8BC5-AC26EB68C6EB", "date": "2026-11-20T17:23:40.000+05:30"}
        folders = self.pending_fixture(before)
        result = self.finish_pending(folders, [old, posted])
        self.assertEqual(result.previews, [[posted]])
        references = [json.loads(content) for path, content in result.saves if path.startswith("photo-links/")]
        self.assertEqual(len(references), 1)
        self.assertEqual(references[0]["photoName"], posted["name"])
        self.assertEqual(references[0]["photoTakenAt"], posted["date"])
        self.assertEqual(references[0]["source"], "shared_album_confirmed")
        self.assertEqual(json.loads(result.saves[-1][1])["state"], "complete")
        viewed = self.inspect(folders, photos=[old, posted])
        self.assertEqual(viewed.previews, [[posted]])

    def test_empty_album_before_posting_can_confirm_one_new_photo(self):
        posted = {"album": "Periwinkle - Sarees", "name": "upload-uuid", "date": "2026-11-20T17:23:40.000+05:30"}
        result = self.finish_pending(self.pending_fixture({"state": "pending", "beforeNames": "␟␟"}), [posted])
        self.assertEqual(result.previews, [[posted]])

    def test_pending_sync_or_ambiguous_new_photos_never_silently_select_an_image(self):
        old = {"album": "Periwinkle - Sarees", "name": "old-photo", "date": "2020-01-01T00:00:00.000+05:30"}
        for photos in [[old], [old, {**old, "name": "new-a"}, {**old, "name": "new-b"}]]:
            result = self.inspect(self.pending_fixture({"state": "pending", "beforeNames": "␟old-photo␟"}), photos=photos)
            self.assertEqual(result.previews, [])
            self.assertEqual(result.saves, [])
            self.assertIn("Photo is still being linked", result.alerts)

    def test_client_can_resume_when_the_post_has_not_synced_yet(self):
        old = {"album": "Periwinkle - Sarees", "name": "old-photo", "date": "2020-01-01T00:00:00.000+05:30"}
        result = self.finish_pending(self.pending_fixture({"state": "pending", "beforeNames": "␟old-photo␟"}), [old])
        self.assertEqual(result.saves, [])
        self.assertIn("Photo is still syncing", result.alerts)

    def test_missing_or_completed_snapshot_cannot_treat_old_album_photos_as_new(self):
        old = {"album": "Periwinkle - Sarees", "name": "old-photo", "date": "2020-01-01T00:00:00.000+05:30"}
        for snapshot in [None, {"state": "complete"}, {"state": "pending", "beforeNames": ""}]:
            result = self.inspect(self.pending_fixture(snapshot), photos=[old])
            self.assertEqual(result.previews, [])
            self.assertEqual(result.saves, [])

    def test_verified_shared_name_repairs_date_from_the_actual_album_asset(self):
        photo = {"album": "Periwinkle - Sarees", "name": "verified-uuid", "date": "2026-11-20T17:23:40.000+05:30"}
        link = {"sku": "PBS-MIN-001", "albumName": photo["album"], "photoName": photo["name"],
                "photoTakenAt": "2026-11-19T21:32:28.548+05:30", "source": "verified_shared_name"}
        result = self.inspect([{"name": "photo-links", "children": [{"name": "pbs-min-001.json", "data": link}]}], photos=[photo])
        self.assertEqual(result.previews, [[photo]])
        self.assertEqual(json.loads(result.saves[0][1])["photoTakenAt"], photo["date"])

    def test_album_copy_can_drop_fractional_seconds_without_losing_the_photo(self):
        data = {"albumName": "Periwinkle - Sarees", "photoName": "IMG_0499", "photoTakenAt": "2026-11-19T21:32:28.548+05:30"}
        photo = {"album": data["albumName"], "name": data["photoName"], "date": "2026-11-19T21:32:28.000+05:30"}
        result = self.inspect([{"name": "photo-links", "children": [{"name": "pbs-min-001.json", "data": data}]}], photos=[photo])
        self.assertEqual(result.previews, [[photo]])

    def test_different_second_or_album_never_matches_the_reference(self):
        data = {"albumName": "Periwinkle - Sarees", "photoName": "IMG_0499", "photoTakenAt": "2026-11-19T21:32:28.548+05:30"}
        for album, date in [(data["albumName"], "2026-11-19T21:32:29.000+05:30"), ("Other Album", data["photoTakenAt"])]:
            photo = {"album": album, "name": data["photoName"], "date": date}
            result = self.inspect([{"name": "photo-links", "children": [{"name": "pbs-min-001.json", "data": data}]}], photos=[photo])
            self.assertEqual(result.previews, [])

    def test_first_use_without_metadata_folder_never_queries_photos(self):
        result = self.inspect([{"name": "products", "children": []}])
        self.assertEqual(result.searches, [])

    def test_missing_file_ignores_a_stale_previous_link(self):
        old = {"data": {"albumName": "Old Album", "photoName": "IMG_1", "photoTakenAt": "old"}}
        result = self.inspect([{"name": "photo-links", "children": []}], {"photoLinkFile": old})
        self.assertEqual(result.searches, [])

    def test_incomplete_links_never_query_an_empty_album(self):
        for missing in ["albumName", "photoName", "photoTakenAt"]:
            data = {"albumName": "Miniatures Available", "photoName": "IMG_0338", "photoTakenAt": "2026-11-19T18:17:00.000+05:30"}
            del data[missing]
            with self.subTest(missing=missing):
                result = self.inspect([{"name": "photo-links", "children": [{"name": "pbs-min-001.json", "data": data}]}])
                self.assertEqual(result.searches, [])
                self.assertIn("Photo link needs updating", result.alerts)

    def test_only_the_matching_product_link_can_start_a_photo_query(self):
        data = {"albumName": "Miniatures Available", "photoName": "IMG_0338", "photoTakenAt": "2026-11-19T18:17:00.000+05:30"}
        for filename in ["pbs-min-001", "pbs-min-001.json"]:
            result = self.inspect([{"name": "photo-links", "children": [{"name": "pbs-min-002.json", "data": {}}, {"name": filename, "data": data}]}])
            self.assertEqual(len(result.searches), 1)
            self.assertIn("Photo unavailable", result.alerts)

    def test_preview_cannot_persist_or_export_images(self):
        s = Store("Preview", {"filename": "test"}, BLUE)
        show_linked_photo(s, named("key"))
        for a in s.actions:
            self.assertNotIn(action_name(a), {"file.move", "file.delete", "share", "setclipboard"})
            if action_name(a) == "documentpicker.save":
                params = a["WFWorkflowActionParameters"]
                self.assertTrue(params["WFFileDestinationPath"]["Value"]["string"].startswith(("photo-links/", "photo-pending/")))

    def test_link_saves_only_json_metadata(self):
        s = Store("Link", {"filename": "test"}, BLUE)
        link_product_photo(s, named("key"), named("sku"))
        saves = [a["WFWorkflowActionParameters"] for a in s.actions if action_name(a) == "documentpicker.save"]
        self.assertEqual(len(saves), 1)
        self.assertTrue(saves[0]["WFFileDestinationPath"]["Value"]["string"].startswith("photo-links/"))
        named_files = [a["WFWorkflowActionParameters"]["WFName"] for a in s.actions if action_name(a) == "setitemname"]
        self.assertEqual(named_files, ["record.json"])
        content = [a["WFWorkflowActionParameters"]["WFTextActionText"]["Value"]["string"] for a in s.actions
                   if action_name(a) == "gettext"]
        self.assertTrue(any('"photoTakenAt"' in t and '"photoName"' in t and '"albumName"' in t for t in content))

    def test_all_photo_queries_require_album_membership(self):
        for flow in [lambda s: show_linked_photo(s, named("key")),
                     lambda s: link_product_photo(s, named("key"), named("sku"))]:
            s = Store("Photos", {"filename": "test"}, BLUE)
            flow(s)
            searches = [a["WFWorkflowActionParameters"] for a in s.actions if action_name(a) == "filter.photos"]
            self.assertTrue(searches)
            for search in searches:
                predicate = search["WFContentItemFilter"]["Value"]
                self.assertEqual(predicate["WFActionParameterFilterPrefix"], 1)
                self.assertIn("Album", [r["Property"] for r in predicate["WFActionParameterFilterTemplates"]])

    def test_preview_has_no_obsolete_quicklook_identifier(self):
        s = Store("Preview", {"filename": "test"}, BLUE)
        show_linked_photo(s, named("key"))
        actions = [action_name(a) for a in s.actions]
        self.assertNotIn("quicklook", actions)
        self.assertIn("previewdocument", actions)
