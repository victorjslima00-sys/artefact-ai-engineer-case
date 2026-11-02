"""
Unit tests for normalized category search and pricing calculations in src.tools.
"""

import unittest
from src.data_loader import DataStore
from src.tools import (
    search_products,
    get_product_details,
    _calculate_max_installments,
)


class TestToolsEnhancements(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = DataStore()

    def test_category_search_singular_plural_accents(self):
        # 'violão', 'violao', 'violões' should return the same active products
        res_accent = search_products(self.store, category="violão")
        res_plain = search_products(self.store, category="violao")
        res_plural = search_products(self.store, category="violões")

        self.assertGreater(res_accent["total_found"], 0)
        self.assertEqual(res_accent["total_found"], res_plain["total_found"])
        self.assertEqual(res_accent["total_found"], res_plural["total_found"])

        # 'bateria' vs 'baterias'
        res_bat_sing = search_products(self.store, category="bateria")
        res_bat_plur = search_products(self.store, category="baterias")
        self.assertGreater(res_bat_sing["total_found"], 0)
        self.assertEqual(res_bat_sing["total_found"], res_bat_plur["total_found"])

        # 'teclado' vs 'teclados'
        res_tec_sing = search_products(self.store, category="teclado")
        res_tec_plur = search_products(self.store, category="teclados")
        self.assertGreater(res_tec_sing["total_found"], 0)
        self.assertEqual(res_tec_sing["total_found"], res_tec_plur["total_found"])

    def test_calculate_max_installments_tiers(self):
        # Abaixo de 50 -> 1x
        self.assertEqual(_calculate_max_installments(45.0), 1)
        # 100 -> 2x (50 cada)
        self.assertEqual(_calculate_max_installments(100.0), 2)
        # 150 -> 3x (50 cada)
        self.assertEqual(_calculate_max_installments(150.0), 3)
        # 320 -> 4x (80 cada)
        self.assertEqual(_calculate_max_installments(320.0), 4)
        # 480 -> 6x (80 cada)
        self.assertEqual(_calculate_max_installments(480.0), 6)
        # 700 -> 7x (100 cada)
        self.assertEqual(_calculate_max_installments(700.0), 7)
        # 1200 -> 12x (100 cada)
        self.assertEqual(_calculate_max_installments(1200.0), 12)

    def test_non_promotional_product_has_pix_and_installments(self):
        # Product 81 has no active promotion
        res = get_product_details(self.store, product_id=81)
        item = res["results"][0]
        self.assertIn("pix_price", item)
        self.assertIn("max_installments", item)
        # 599.90 * 0.95 = 569.905 -> R$ 569,90 or R$ 569,91
        self.assertTrue(item["pix_price"].startswith("R$ 569,"))
        self.assertEqual(item["max_installments"], "6x sem juros")

    def test_promotional_product_omits_pix_price(self):
        # Find active promo product
        active_promos = self.store.promotions[self.store.promotions["is_active"] == 1]
        self.assertFalse(active_promos.empty)
        promo_pid = int(active_promos.iloc[0]["product_id"])

        res = get_product_details(self.store, product_id=promo_pid)
        item = res["results"][0]
        self.assertIn("promotion", item)
        self.assertNotIn("pix_price", item)


if __name__ == "__main__":
    unittest.main()
