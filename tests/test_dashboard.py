from __future__ import annotations

import unittest

from dashboard.data_access import DashboardRepository
from warehouse.builder import WarehouseBuilder


class DashboardDataAccessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        WarehouseBuilder().build(regenerate_data=True)
        cls.repo = DashboardRepository()

    def test_customer_view_has_expected_fields(self) -> None:
        customers = self.repo.load_customer_view()
        self.assertGreater(len(customers), 0)
        self.assertTrue({"customer_id", "blended_clv", "churn_risk_band", "repeat_purchase_segment"}.issubset(customers.columns))

    def test_order_and_support_views_are_available(self) -> None:
        orders = self.repo.load_order_view()
        support = self.repo.load_support_view()
        self.assertGreater(len(orders), 0)
        self.assertGreater(len(support), 0)


if __name__ == "__main__":
    unittest.main()

