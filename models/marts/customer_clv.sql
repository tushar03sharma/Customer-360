create or replace table marts.customer_clv as
with base as (
    select
        customer_id,
        acquisition_channel,
        completed_orders,
        first_order_date,
        last_order_date,
        lifetime_revenue,
        avg_order_value,
        case
            when first_order_date is null then 0
            else greatest(date_diff('month', first_order_date, coalesce(last_order_date, current_date)) + 1, 1)
        end as active_months,
        case
            when days_since_last_order is null then 3
            when days_since_last_order <= 45 then 18
            when days_since_last_order <= 90 then 12
            when days_since_last_order <= 180 then 8
            else 4
        end as projected_retention_months
    from marts.customer_360
)
select
    customer_id,
    acquisition_channel,
    completed_orders,
    lifetime_revenue as historical_clv,
    round(coalesce(completed_orders * 1.0 / nullif(active_months, 0), 0), 3) as monthly_order_frequency,
    avg_order_value,
    projected_retention_months,
    round(coalesce(avg_order_value, 0) * coalesce(completed_orders * 1.0 / nullif(active_months, 0), 0) * projected_retention_months, 2) as projected_clv,
    round(lifetime_revenue + (coalesce(avg_order_value, 0) * coalesce(completed_orders * 1.0 / nullif(active_months, 0), 0) * projected_retention_months), 2) as blended_clv,
    dense_rank() over (order by lifetime_revenue + (coalesce(avg_order_value, 0) * coalesce(completed_orders * 1.0 / nullif(active_months, 0), 0) * projected_retention_months) desc) as clv_rank
from base;

