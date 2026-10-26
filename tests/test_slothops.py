import unittest
from pathlib import Path
from slothops.engine.llm_client import LLMClient
from slothops.engine.summarizer import MorningBriefEngine
from slothops.engine.sorter import ClutterSorter
from slothops.engine.winddown import WindDownEngine

class TestSlothOps(unittest.TestCase):
    def test_llm_client_fallback(self):
        client = LLMClient(base_url="http://127.0.0.1:99999")
        status = client.check_availability()
        self.assertIn("provider", status)
        self.assertIn("models", status)

    def test_morning_brief_engine(self):
        client = LLMClient()
        engine = MorningBriefEngine(client)
        notes = "- urgent: fix production crash\n- buy groceries\n- explore new rust framework someday"
        result = engine.generate_brief(notes)
        
        self.assertIn("high_impact", result)
        self.assertIn("safe_to_ignore", result)
        self.assertIn("wisdom", result)
        self.assertTrue(len(result["high_impact"]) > 0)

    def test_clutter_sorter_classification(self):
        client = LLMClient()
        sorter = ClutterSorter(client)
        
        self.assertEqual(sorter.classify_file("invoice_october.pdf"), "Finance_Invoices")
        self.assertEqual(sorter.classify_file("server.py"), "Code_and_Dev")
        self.assertEqual(sorter.classify_file("photo.png"), "Media_and_Design")
        self.assertEqual(sorter.classify_file("dataset.csv"), "Data_and_Sheets")

    def test_clutter_sorter_scan(self):
        client = LLMClient()
        sorter = ClutterSorter(client)
        res = sorter.scan_directory("./demo_sandbox")
        
        self.assertIn("items", res)
        self.assertTrue(res["total_files"] >= 4)

    def test_winddown_engine(self):
        client = LLMClient()
        engine = WindDownEngine(client)
        res = engine.generate_winddown("Merged 3 pull requests and fixed critical auth bug")
        
        self.assertIn("recap", res)
        self.assertIn("permission_to_rest", res)
        self.assertIn("soundscape", res)

if __name__ == "__main__":
    unittest.main()
