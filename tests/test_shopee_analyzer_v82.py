import unittest

from src.shopee_analyzer import _number, _extract_sales_and_reviews, is_shopee_url


class TestShopeeAnalyzerV82(unittest.TestCase):
    def test_localized_numbers(self):
        self.assertEqual(_number("10RB"), 10000)
        self.assertEqual(_number("1,5K"), 1500)
        self.assertEqual(_number("1.5K"), 1500)
        self.assertEqual(_number("10.000"), 10000)
        self.assertEqual(_number("10,000"), 10000)
        self.assertEqual(_number("2,3 JUTA"), 2300000)

    def test_sales_plus_is_lower_bound(self):
        sales, reviews, lower = _extract_sales_and_reviews("10RB+ terjual 1,2RB ulasan")
        self.assertEqual(sales, 10000)
        self.assertEqual(reviews, 1200)
        self.assertTrue(lower)

    def test_url_host_is_strict(self):
        self.assertTrue(is_shopee_url("https://shopee.co.id/foo-i.1.2"))
        self.assertFalse(is_shopee_url("https://evil.example/shopee.co.id"))
        self.assertFalse(is_shopee_url("javascript:alert(1)"))


if __name__ == "__main__":
    unittest.main()
