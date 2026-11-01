import unittest
from datetime import date
from unittest.mock import patch

from src.data_loader import DataStore
from src.tools import check_order_status


class ReturnEligibilityTests(unittest.TestCase):
    def setUp(self):
        self.store = DataStore()

    @patch("src.tools.get_reference_date", return_value=date(2025, 10, 30))
    def test_return_window_starts_from_delivery_date(self, _get_reference_date):
        result = check_order_status(
            self.store,
            customer_identifier="pedro.oliveira@jmail.com",
            order_id=1,
        )

        order = result["orders"][0]
        self.assertTrue(order["return_eligible"])
        self.assertEqual(order["return_deadline"], "01/11/2025")
        self.assertEqual(order["return_eligibility_status"], "provisional")

    @patch("src.tools.get_reference_date", return_value=date(2025, 11, 1))
    def test_seventh_calendar_day_is_included(self, _get_reference_date):
        order = check_order_status(
            self.store, "pedro.oliveira@jmail.com", order_id=1
        )["orders"][0]
        self.assertTrue(order["return_eligible"])

    @patch("src.tools.get_reference_date", return_value=date(2025, 11, 2))
    def test_eighth_calendar_day_is_outside_provisional_window(self, _get_reference_date):
        order = check_order_status(
            self.store, "pedro.oliveira@jmail.com", order_id=1
        )["orders"][0]
        self.assertFalse(order["return_eligible"])
        self.assertEqual(order["days_since_delivery_estimate"], 8)

    @patch("src.tools.get_reference_date", return_value=date(2025, 10, 30))
    def test_missing_estimated_delivery_leaves_eligibility_unknown(self, _get_reference_date):
        row_index = self.store.orders.index[self.store.orders["order_id"] == 1][0]
        self.store.orders.loc[row_index, "estimated_delivery"] = None
        order = check_order_status(
            self.store, "pedro.oliveira@jmail.com", order_id=1
        )["orders"][0]
        self.assertIsNone(order["return_eligible"])
        self.assertEqual(order["return_eligibility_status"], "unknown")

    @patch("src.tools.get_reference_date", return_value=date(2025, 10, 24))
    def test_future_estimate_leaves_eligibility_unknown(self, _get_reference_date):
        order = check_order_status(
            self.store, "pedro.oliveira@jmail.com", order_id=1
        )["orders"][0]
        self.assertIsNone(order["return_eligible"])
        self.assertEqual(order["return_eligibility_status"], "unknown")


if __name__ == "__main__":
    unittest.main()
