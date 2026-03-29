create or replace table marts.customer_360 as
select
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    c.city,
    c.country,
    c.signup_date,
    c.acquisition_channel,
    c.customer_age_days,
    coalesce(o.orders_attempted, 0) as orders_attempted,
    coalesce(o.completed_orders, 0) as completed_orders,
    coalesce(o.returned_orders, 0) as returned_orders,
    coalesce(o.cancelled_orders, 0) as cancelled_orders,
    o.first_order_date,
    o.last_order_date,
    case when o.last_order_date is not null then date_diff('day', o.last_order_date, current_date) end as days_since_last_order,
    coalesce(o.lifetime_revenue, 0) as lifetime_revenue,
    coalesce(o.avg_order_value, 0) as avg_order_value,
    coalesce(o.refunded_amount, 0) as refunded_amount,
    coalesce(s.total_tickets, 0) as total_tickets,
    coalesce(s.high_priority_tickets, 0) as high_priority_tickets,
    coalesce(s.avg_resolution_hours, 0) as avg_resolution_hours,
    coalesce(s.avg_csat_score, 0) as avg_csat_score,
    case when coalesce(o.completed_orders, 0) > 1 then true else false end as is_repeat_customer
from core.dim_customers c
left join core.customer_order_summary o on c.customer_id = o.customer_id
left join core.customer_support_summary s on c.customer_id = s.customer_id;

