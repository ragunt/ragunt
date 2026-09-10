import unittest

from src.aae_strategist import affiliate_score, content_score, score_breakdown, score_product


class TestAAEStrategist(unittest.TestCase):
    def product(self, **overrides):
        data = {
            "name": "Produk test",
            "category": "Gamis",
            "price": 100000,
            "commission_percent": 10,
            "rating": 4.8,
            "sales": 10000,
            "review_count": 1000,
            "problem": "susah mencari gamis praktis",
            "benefit": "praktis dan nyaman",
            "target": "wanita muslim",
            "competition": 2,
        }
        data.update(overrides)
        return data

    def test_affiliate_score_is_normalized_to_100(self):
        score = affiliate_score(self.product())
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_missing_commission_does_not_create_fake_economics(self):
        breakdown = score_breakdown(self.product(commission_percent=0))
        self.assertEqual(breakdown["Affiliate Economics"], 0)

    def test_negative_numeric_inputs_are_safe(self):
        product = self.product(price=-100, sales=-500, rating=-1, commission_percent=-10)
        self.assertGreaterEqual(score_product(product), 0)
        self.assertGreaterEqual(affiliate_score(product), 0)

    def test_content_score_has_fixed_range(self):
        self.assertGreaterEqual(content_score(self.product()), 0)
        self.assertLessEqual(content_score(self.product()), 100)

    def test_unknown_competition_is_neutral(self):
        breakdown = score_breakdown(self.product(competition=-1))
        self.assertEqual(breakdown["Competition"], 5.0)


if __name__ == "__main__":
    unittest.main()
