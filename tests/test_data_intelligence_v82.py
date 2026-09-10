import unittest

from src.data_intelligence import data_quality, detect_suspicious_data, enrich_product, estimate_competition


class TestDataIntelligenceV82(unittest.TestCase):
    def base(self):
        return {"name": "Gamis Rayon Airflow", "category": "Gamis", "description": "gamis praktis dan nyaman", "price": 100000, "rating": 4.8, "sales": 10000, "review_count": 1000, "competition": -1}

    def test_infers_missing_fields(self):
        product = enrich_product(self.base())
        self.assertTrue(product["problem"])
        self.assertTrue(product["benefit"])
        self.assertTrue(product["target"])

    def test_manual_fields_are_preserved(self):
        product = enrich_product(self.base() | {"problem": "masalah manual", "benefit": "manfaat manual", "target": "target manual"})
        self.assertEqual(product["problem"], "masalah manual")
        self.assertEqual(product["benefit"], "manfaat manual")
        self.assertEqual(product["target"], "target manual")

    def test_lower_bound_sales_flag(self):
        flags = detect_suspicious_data(self.base() | {"sales_is_lower_bound": True})
        self.assertTrue(flags)

    def test_quality_stays_bounded(self):
        quality, _ = data_quality(self.base())
        self.assertGreaterEqual(quality, 0)
        self.assertLessEqual(quality, 100)

    def test_competition_heuristic_is_bounded(self):
        score, source = estimate_competition(self.base())
        self.assertEqual(source, "heuristic")
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 10)


if __name__ == "__main__":
    unittest.main()
