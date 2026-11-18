"""Check the experiment cannot touch the register or leak the intake caption."""
import unittest

from printing_experiment import APP_ID, TEST_SKU, build_pdf_test, build_print_test, label_pdf


class PrintingExperimentChecks(unittest.TestCase):
    def setUp(self):
        self.shortcut = build_print_test(b"synthetic image for structural tests")

    def test_only_handoff_actions_no_files_register_or_network(self):
        allowed = {"comment", "gettext", "choosefrommenu", "setclipboard", "openapp", "share",
                   "base64encode", "setitemname", "openin"}
        for action in self.shortcut.actions:
            self.assertIn(action["WFWorkflowActionIdentifier"].removeprefix("is.workflow.actions."), allowed)

    def test_each_route_copies_only_the_synthetic_sku(self):
        source = self.shortcut.actions[1]["WFWorkflowActionParameters"]
        self.assertEqual(source["WFTextActionText"]["Value"]["string"], TEST_SKU)
        clips = [a["WFWorkflowActionParameters"] for a in self.shortcut.actions
                 if a["WFWorkflowActionIdentifier"].endswith(".setclipboard")]
        self.assertEqual(len(clips), 5)
        for clip in clips:
            self.assertEqual(clip["WFInput"]["Value"]["OutputUUID"], source["UUID"])
            self.assertTrue(clip["WFLocalOnly"])

    def test_app_is_resolved_on_phone_not_rebound_on_mac(self):
        app_id = self.shortcut.actions[2]["WFWorkflowActionParameters"]
        self.assertEqual(app_id["WFTextActionText"]["Value"]["string"], APP_ID)
        handoffs = [a["WFWorkflowActionParameters"] for a in self.shortcut.actions
                    if a["WFWorkflowActionIdentifier"].endswith((".openapp", ".openin"))]
        self.assertEqual(len(handoffs), 3)
        for handoff in handoffs[:2]:
            self.assertEqual(handoff["WFSelectedApp"]["Value"]["OutputUUID"], app_id["UUID"])
            self.assertNotIn("WFApp", handoff)
            self.assertNotIn("WFAppIdentifier", handoff)
            self.assertNotIn("WFOpenInAppIdentifier", handoff)
        self.assertEqual(handoffs[2]["WFSelectedApp"]["Value"], {"Type": "Ask"})


class PdfPrintingChecks(unittest.TestCase):
    def test_pdf_routes_use_a_pdf_file_and_runtime_app_lookup(self):
        shortcut = build_pdf_test(b"synthetic PDF for wiring checks")
        actions = shortcut.actions
        params = [a["WFWorkflowActionParameters"] for a in actions]
        app_id = params[2]
        filename = params[5]
        self.assertEqual(filename["WFName"], TEST_SKU + ".pdf")
        routes = [a for a in actions if a["WFWorkflowActionIdentifier"].endswith((".openin", ".share"))]
        self.assertEqual(len(routes), 2)
        for route in routes:
            self.assertEqual(route["WFWorkflowActionParameters"]["WFInput"]["Value"]["OutputUUID"], filename["UUID"])
        self.assertEqual(routes[0]["WFWorkflowActionParameters"]["WFSelectedApp"]["Value"]["OutputUUID"], app_id["UUID"])
        allowed = {"comment", "gettext", "base64encode", "setitemname", "choosefrommenu", "setclipboard", "openin", "share"}
        for action in actions:
            self.assertIn(action["WFWorkflowActionIdentifier"].removeprefix("is.workflow.actions."), allowed)

    def test_pdf_is_one_label_sized_page_with_only_the_test_sku(self):
        import io
        from pypdf import PdfReader
        pdf = PdfReader(io.BytesIO(label_pdf()))
        self.assertEqual(len(pdf.pages), 1)
        page = pdf.pages[0]
        self.assertAlmostEqual(float(page.mediabox.width), 50 * 72 / 25.4, places=3)
        self.assertAlmostEqual(float(page.mediabox.height), 30 * 72 / 25.4, places=3)
        self.assertEqual(page.extract_text().strip(), TEST_SKU)


if __name__ == "__main__":
    unittest.main()
