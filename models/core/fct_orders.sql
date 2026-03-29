create or replace table core.fct_orders as
with payment_rollup as (
    select
        order_id,
        max(payment_date) as payment_date,
        max(payment_method) as payment_method,
        max(payment_status) as payment_status,
        sum(amount) as payment_amount,
        sum(refunded_amount) as refunded_amount
    from staging.stg_payments
    group by 1
)
select
    o.order_id,
    o.customer_id,
    o.order_date,
    o.order_status,
    o.gross_amount,
    o.discount_amount,
    o.shipping_fee,
    o.net_amount,
    o.items_count,
    p.payment_date,
    coalesce(p.payment_method, 'Unknown') as payment_method,
    coalesce(p.payment_status, 'unpaid') as payment_status,
    coalesce(p.payment_amount, 0) as payment_amount,
    coalesce(p.refunded_amount, 0) as refunded_amount,
    case
        when o.order_status = 'completed' and coalesce(p.payment_status, 'unpaid') = 'paid' then greatest(o.net_amount - coalesce(p.refunded_amount, 0), 0)
        when o.order_status = 'returned' and coalesce(p.payment_status, '') in ('refunded', 'partially_refunded') then greatest(o.net_amount - coalesce(p.refunded_amount, 0), 0)
        else 0
    end as recognized_revenue
from staging.stg_orders o
left join payment_rollup p on o.order_id = p.order_id;

