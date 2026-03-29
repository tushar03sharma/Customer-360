create or replace table core.customer_order_summary as
select
    customer_id,
    count(*) as orders_attempted,
    count(*) filter (where order_status = 'completed') as completed_orders,
    count(*) filter (where order_status = 'returned') as returned_orders,
    count(*) filter (where order_status = 'cancelled') as cancelled_orders,
    count(*) filter (where payment_status = 'failed') as failed_payments,
    min(order_date) as first_order_date,
    max(order_date) as last_order_date,
    round(sum(recognized_revenue), 2) as lifetime_revenue,
    round(avg(case when order_status = 'completed' then recognized_revenue end), 2) as avg_order_value,
    round(sum(refunded_amount), 2) as refunded_amount
from core.fct_orders
group by 1;

