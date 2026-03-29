create or replace table marts.repeat_purchase_behavior as
with completed_orders as (
    select
        customer_id,
        order_date,
        lag(order_date) over (partition by customer_id order by order_date) as previous_order_date
    from core.fct_orders
    where order_status = 'completed'
),
order_gaps as (
    select
        customer_id,
        avg(date_diff('day', previous_order_date, order_date)) as avg_days_between_orders,
        min(date_diff('day', previous_order_date, order_date)) as second_order_gap_days
    from completed_orders
    where previous_order_date is not null
    group by 1
)
select
    c.customer_id,
    date_trunc('month', c.signup_date) as signup_cohort_month,
    c.acquisition_channel,
    coalesce(c.completed_orders, 0) as completed_orders,
    case
        when coalesce(c.completed_orders, 0) >= 5 then 'Habit'
        when coalesce(c.completed_orders, 0) >= 3 then 'Repeat'
        when coalesce(c.completed_orders, 0) = 2 then 'Second-time'
        when coalesce(c.completed_orders, 0) = 1 then 'One-time'
        else 'No purchase'
    end as repeat_purchase_segment,
    round(g.avg_days_between_orders, 1) as avg_days_between_orders,
    g.second_order_gap_days,
    round(
        100.0
        * sum(case when coalesce(c.completed_orders, 0) > 1 then 1 else 0 end) over (
            partition by date_trunc('month', c.signup_date), c.acquisition_channel
        )
        / nullif(count(*) over (partition by date_trunc('month', c.signup_date), c.acquisition_channel), 0),
        2
    ) as cohort_repeat_rate_pct
from marts.customer_360 c
left join order_gaps g on c.customer_id = g.customer_id;

