from __future__ import annotations

import unittest

import duckdb

from warehouse.builder import WarehouseBuilder
from warehouse.config import DB_PATH


class WarehousePipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = WarehouseBuilder().build(regenerate_data=True)

    def test_quality_checks_pass(self) -> None:
        self.assertTrue(all(result["passed"] for result in self.summary["quality_results"]))

    def test_clv_contains_ranked_customers(self) -> None:
        with duckdb.connect(str(DB_PATH)) as conn:
            top_customer = conn.execute(
                """
                select customer_id, blended_clv
                from marts.customer_clv
                order by blended_clv desc
                limit 1
                """
            ).fetchone()
        self.assertIsNotNone(top_customer)
        self.assertGreater(top_customer[1], 0)

    def test_repeat_behavior_has_cohort_metrics(self) -> None:
        with duckdb.connect(str(DB_PATH)) as conn:
            cohort_count = conn.execute(
                """
                select count(distinct concat(cast(signup_cohort_month as varchar), acquisition_channel))
                from marts.repeat_purchase_behavior
                """
            ).fetchone()[0]
        self.assertGreater(cohort_count, 5)


if __name__ == "__main__":
    unittest.main()
