import unittest

from src.shopee_analyzer import _number, _price, is_shopee_url


class TestShopeeAnalyzer(unittest.TestCase):
    def test_valid_shopee_url(self):
        self.assertTrue(is_shopee_url("https://shopee.co.id/produk-i.123.456"))

    def test_rejects_other_hosts(self):
        self.assertFalse(is_shopee_url("https://example.com/produk"))
        self.assertFalse(is_shopee_url("javascript:alert(1)"))

    def test_localized_quantity_parsing(self):
        self.assertEqual(_number("10RB"), 10000)
        self.assertEqual(_number("1,5K"), 1500)
        self.assertEqual(_number("1.5K"), 1500)
        self.assertEqual(_number("2,3 JUTA"), 2300000)

    def test_plain_numbers_and_thousands(self):
        self.assertEqual(_number("10.000"), 10000)
        self.assertEqual(_number("10,000"), 10000)
        self.assertEqual(_number("793"), 793)

    def test_price_parser(self):
        self.assertEqual(_price("Rp17.476"), 17476)
        self.assertEqual(_price("Rp 84.000"), 84000)


if __name__ == "__main__":
    unittest.main()
