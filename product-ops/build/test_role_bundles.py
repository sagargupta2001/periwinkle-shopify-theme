"""Prove packaging preserves each operation without installed helper shortcuts."""
import re
import unittest

import build
from test_build import action_name


def normalize(actions, root_uuid):
    identifiers = {root_uuid: "ROOT"}

    def walk(value):
        if isinstance(value, dict):
            return {key: walk(value[key]) for key in sorted(value)}
        if isinstance(value, list):
            return [walk(item) for item in value]
        if isinstance(value, str) and re.fullmatch(r"[0-9A-F]{8}(?:-[0-9A-F]{4}){3}-[0-9A-F]{12}", value):
            identifiers.setdefault(value, f"ID-{len(identifiers)}")
            return identifiers[value]
        return value
    return walk(actions)


class RoleBundles(unittest.TestCase):
    def test_each_top_level_choice_preserves_the_complete_original_operation(self):
        folder = {"filename": "account-specific-test-folder"}
        for maker, operations in [(build.client_bundle, build.CLIENT_MENU), (build.operator_bundle, build.OPERATOR_MENU)]:
            bundle = maker(folder)
            root = bundle.actions[0]["WFWorkflowActionParameters"]
            menu = bundle.actions[1]["WFWorkflowActionParameters"]
            group = menu["GroupingIdentifier"]
            self.assertEqual(menu["WFMenuItems"], [label for label, _ in operations])
            self.assertIn(f"build {build.BUILD}", menu["WFMenuPrompt"])
            cases = [i for i, a in enumerate(bundle.actions)
                     if a["WFWorkflowActionParameters"].get("GroupingIdentifier") == group
                     and a["WFWorkflowActionParameters"].get("WFControlFlowMode") == 1]
            self.assertEqual(len(cases), len(operations))
            for index, (label, operation) in enumerate(operations):
                begin = cases[index]
                end = cases[index + 1] if index + 1 < len(cases) else len(bundle.actions) - 1
                self.assertEqual(bundle.actions[begin]["WFWorkflowActionParameters"]["WFMenuItemTitle"], label)
                body = bundle.actions[begin + 1:end]
                self.assertEqual(action_name(body[-1]), "exit")
                original = operation(folder)
                old_root = original.actions[0]["WFWorkflowActionParameters"]["UUID"]
                self.assertEqual(normalize(body[:-1], root["UUID"]), normalize(original.actions[1:], old_root), label)

    def test_each_role_has_one_binding_and_no_run_shortcut_dependencies(self):
        for maker in build.BUNDLES:
            folder = {"filename": maker.__name__}
            bundle = maker(folder)
            bindings = [a["WFWorkflowActionParameters"]["WFFile"] for a in bundle.actions if action_name(a) == "file"]
            self.assertEqual(bindings, [folder])
            self.assertNotIn("runworkflow", [action_name(a) for a in bundle.actions])
            self.assertEqual(bundle.questions, [])

    def test_client_has_no_operator_menu_or_delete_action(self):
        bundle = build.client_bundle({"filename": "test"})
        self.assertEqual(bundle.actions[1]["WFWorkflowActionParameters"]["WFMenuItems"],
                         ["New Product", "Update Stock", "Fix Product", "Print Product Label"])
        self.assertNotIn("file.delete", [action_name(a) for a in bundle.actions])

    def test_only_the_operator_register_case_can_delete_a_derived_view(self):
        bundle = build.operator_bundle({"filename": "test"})
        group = bundle.actions[1]["WFWorkflowActionParameters"]["GroupingIdentifier"]
        current = None
        for action in bundle.actions:
            p = action["WFWorkflowActionParameters"]
            if p.get("GroupingIdentifier") == group and p.get("WFControlFlowMode") == 1:
                current = p["WFMenuItemTitle"]
            if action_name(action) == "file.delete":
                self.assertEqual(current, "Register")
