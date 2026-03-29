from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from warehouse.config import DB_PATH


class DashboardRepository:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = str(db_path or DB_PATH)

    def load_customer_view(self) -> pd.DataFrame:
        with duckdb.connect(self.db_path, read_only=True) as conn:
            return conn.execute(
                """
                select
                    c360.customer_id,
                    c360.first_name,
                    c360.last_name,
                    c360.city,
                    c360.country,
                    c360.signup_date,
                    c360.acquisition_channel,
                    c360.customer_age_days,
                    c360.orders_attempted,
                    c360.completed_orders,
                    c360.returned_orders,
                    c360.cancelled_orders,
                    c360.first_order_date,
                    c360.last_order_date,
                    c360.days_since_last_order,
                    c360.lifetime_revenue,
                    c360.avg_order_value,
                    c360.refunded_amount,
                    c360.total_tickets,
                    c360.high_priority_tickets,
                    c360.avg_resolution_hours,
                    c360.avg_csat_score,
                    c360.is_repeat_customer,
                    clv.monthly_order_frequency,
                    clv.projected_retention_months,
                    clv.projected_clv,
                    clv.blended_clv,
                    clv.clv_rank,
                    churn.churn_risk_score,
                    churn.churn_risk_band,
                    churn.recommended_action,
                    repeat.signup_cohort_month,
                    repeat.repeat_purchase_segment,
                    repeat.avg_days_between_orders,
                    repeat.second_order_gap_days,
                    repeat.cohort_repeat_rate_pct
                from marts.customer_360 c360
                left join marts.customer_clv clv on c360.customer_id = clv.customer_id
                left join marts.customer_churn_risk churn on c360.customer_id = churn.customer_id
                left join marts.repeat_purchase_behavior repeat on c360.customer_id = repeat.customer_id
                """
            ).fetchdf()

    def load_order_view(self) -> pd.DataFrame:
        with duckdb.connect(self.db_path, read_only=True) as conn:
            return conn.execute(
                """
                select
                    o.order_id,
                    o.customer_id,
                    o.order_date,
                    o.order_status,
                    o.payment_method,
                    o.items_count,
                    o.recognized_revenue,
                    o.refunded_amount,
                    c.acquisition_channel
                from core.fct_orders o
                left join core.dim_customers c on o.customer_id = c.customer_id
                """
            ).fetchdf()

    def load_support_view(self) -> pd.DataFrame:
        with duckdb.connect(self.db_path, read_only=True) as conn:
            return conn.execute(
                """
                select
                    customer_id,
                    created_at,
                    issue_type,
                    priority,
                    resolution_hours,
                    csat_score
                from core.fct_support_tickets
                """
            ).fetchdf()

