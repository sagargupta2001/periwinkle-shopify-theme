"""Keep the phone investigation read-only and restricted to the requested album."""
import unittest

from photo_lookup_experiment import photo_lookup_experiment
from test_build import action_name


class PhotoLookupSafety(unittest.TestCase):
    def test_only_reads_photos_and_displays_results(self):
        shortcut = photo_lookup_experiment()
        allowed = {"alert", "ask", "conditional", "exit", "choosefrommenu", "gettext",
                   "setvariable", "filter.photos", "text.trimwhitespace", "count", "choosefromlist",
                   "properties.images", "previewdocument"}
        self.assertTrue(all(action_name(a) in allowed for a in shortcut.actions))

    def test_filename_lookup_never_falls_back_to_the_whole_library(self):
        searches = [a["WFWorkflowActionParameters"] for a in photo_lookup_experiment().actions
                    if action_name(a) == "filter.photos"]
        self.assertEqual(len(searches), 2)
        for search in searches:
            predicate = search["WFContentItemFilter"]["Value"]
            self.assertEqual(predicate["WFActionParameterFilterPrefix"], 1)  # AND
            self.assertIn("Album", [r["Property"] for r in predicate["WFActionParameterFilterTemplates"]])
        self.assertIn("Name", [r["Property"] for r in searches[1]["WFContentItemFilter"]["Value"]["WFActionParameterFilterTemplates"]])
