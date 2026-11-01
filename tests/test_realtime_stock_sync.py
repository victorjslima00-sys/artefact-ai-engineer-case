import unittest
from src.data_loader import DataStore
from src.agent import EmporioChatbot
from src.tools import get_product_details, search_products


class RealTimeStockSyncTests(unittest.TestCase):
    def setUp(self):
        self.store = DataStore()
        self.bot = EmporioChatbot(store=self.store)

    def test_stock_mutation_reflects_in_agent_tools(self):
        # Product 81 (Yamaha C40) starts with 12
        initial_details = get_product_details(self.store, product_id=81)
        self.assertEqual(initial_details["results"][0]["stock"], 12)

        # Mutate stock to 56 (as specified in user scenario)
        self.store.update_product_stock(81, 56)

        # Query via agent's tool mapping
        tool_result = self.bot._tool_map["get_product_details"](product_id=81)
        self.assertEqual(tool_result["results"][0]["stock"], 56)

    def test_stock_decrement_simulates_cart_purchase(self):
        # Product 82 starts with 8
        self.store.adjust_product_stock(82, -2)
        tool_result = self.bot._tool_map["get_product_details"](product_id=82)
        self.assertEqual(tool_result["results"][0]["stock"], 6)

    def test_zero_stock_marks_product_as_unavailable(self):
        # Deplete stock of product 83
        self.store.update_product_stock(83, 0)
        tool_result = self.bot._tool_map["get_product_details"](product_id=83)
        self.assertEqual(tool_result["results"][0]["stock"], 0)
        self.assertEqual(
            tool_result["results"][0].get("note"),
            "Produto temporariamente fora de estoque.",
        )


if __name__ == "__main__":
    unittest.main()
