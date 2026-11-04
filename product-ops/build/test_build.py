#!/usr/bin/env python3
"""Checks every shortcut for mistakes that only show up on an iPhone. No signing or device needed.

    python3 -m unittest test_build
"""
import re
import unittest

import build

# Every action here has run on an iPhone. A new one needs testing there first: some identifiers
# exist in the system but not in the app (is.workflow.actions.folder shows "Unknown Action").
TESTED_ACTIONS = {
    "alert", "appendvariable", "ask", "calculateexpression", "choosefromlist", "choosefrommenu", "conditional", "count",
    "date", "detect.dictionary", "documentpicker.open", "documentpicker.save", "exit", "file", "file.delete",
    "file.getfoldercontents", "file.move", "format.date", "gettext", "getvalueforkey", "notification", "openin",
    "properties.files", "repeat.each", "selectphoto", "setclipboard", "setitemname", "setvariable", "share", "statistics",
    "text.changecase", "text.combine", "text.match", "text.replace", "text.trimwhitespace",
}
READS_FILE = {"detect.dictionary", "getvalueforkey"}
CHANGES_FILE_LOCATION = {"file.move", "file.delete"}
PREFIX = "is.workflow.actions."


def action_name(action):
    return action["WFWorkflowActionIdentifier"].replace(PREFIX, "")


def references(value):
    """Every action output a parameter uses."""
    if isinstance(value, dict):
        if "OutputUUID" in value:
            yield value["OutputUUID"]
        for item in value.values():
            yield from references(item)
    elif isinstance(value, list):
        for item in value:
            yield from references(item)


class ShortcutChecks(unittest.TestCase):
    def setUp(self):
        self.shortcuts = [builder({"filename": "test"}) for builder in build.CLIENT + build.OPERATOR]

    def test_names_are_unique_and_prefixed(self):
        names = [s.name for s in self.shortcuts]
        self.assertEqual(len(names), len(set(names)))
        for name in names:
            self.assertTrue(name.startswith("Periwinkle – "), name)

    def test_only_tested_actions_are_used(self):
        for s in self.shortcuts:
            for action in s.actions:
                self.assertIn(action_name(action), TESTED_ACTIONS, f"{s.name}: test this action on an iPhone first")

    def test_blocks_open_and_close_in_order(self):
        for s in self.shortcuts:
            stack = []
            for action in s.actions:
                params = action["WFWorkflowActionParameters"]
                group, mode = params.get("GroupingIdentifier"), params.get("WFControlFlowMode")
                if group is None:
                    continue
                if mode == 0:
                    stack.append(group)
                else:
                    self.assertEqual(stack[-1], group, s.name)
                    if mode == 2:
                        stack.pop()
            self.assertEqual(stack, [], s.name)

    def test_outputs_are_used_only_after_they_exist(self):
        for s in self.shortcuts:
            seen = set()
            for action in s.actions:
                params = action["WFWorkflowActionParameters"]
                for used in references(params):
                    self.assertIn(used, seen, f"{s.name}: {action_name(action)} uses a later output")
                seen.add(params["UUID"])

    def test_values_from_a_file_are_not_used_after_it_moves(self):
        """Doing so stops the run on iPhone with a ToolDialogHandler error, even through a Text action."""
        for s in self.shortcuts:
            from_file = set()
            for action in s.actions:
                params = action["WFWorkflowActionParameters"]
                if action_name(action) in READS_FILE or from_file.intersection(references(params)):
                    from_file.add(params["UUID"])
            for index, action in enumerate(s.actions):
                if action_name(action) not in CHANGES_FILE_LOCATION:
                    continue
                depth = 0
                for later in s.actions[index + 1:]:
                    params = later["WFWorkflowActionParameters"]
                    mode = params.get("WFControlFlowMode")
                    depth += {0: 1, 2: -1}.get(mode, 0)
                    if depth < 0:  # the block holding the move has ended
                        break
                    self.assertFalse(from_file.intersection(references(params)),
                                     f"{s.name}: {action_name(later)} uses a value read from a file after it moved")

    def test_records_are_never_deleted(self):
        """Only Register deletes, and only its rebuilt Numbers copy."""
        for s in self.shortcuts:
            if s.name != "Periwinkle – Register":
                self.assertNotIn("file.delete", [action_name(a) for a in s.actions], s.name)


class SkuRules(unittest.TestCase):
    def pad(self, number):
        return re.sub(build.PAD_FIND, build.PAD_REPLACE.replace("$", "\\"), "00" + number)  # Python writes $1 as \1

    def test_numbers_pad_to_at_least_three_digits(self):
        for number, padded in [("1", "001"), ("13", "013"), ("001", "001"), ("0004", "004"), ("999", "999"), ("1000", "1000")]:
            self.assertEqual(self.pad(number), padded)

    def test_only_positive_whole_numbers_are_accepted(self):
        for good in ["1", "001", "1000"]:
            self.assertRegex(good, build.NUMBER_RULE)
        for bad in ["", "0", "000", "1.5", "-1", "A1", "12 3"]:
            self.assertNotRegex(bad, build.NUMBER_RULE)

    def test_category_codes_are_three_capitals(self):
        # ask_category reads the code back out of the menu label
        for _, code in build.CATEGORIES:
            self.assertRegex(code, r"^[A-Z]{3}$")


if __name__ == "__main__":
    unittest.main()
