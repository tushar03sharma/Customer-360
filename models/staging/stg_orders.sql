create or replace table staging.stg_orders as
select
    order_id,
    customer_id,
    cast(order_date as date) as order_date,
    lower(order_status) as order_status,
    cast(gross_amount as double) as gross_amount,
    cast(discount_amount as double) as discount_amount,
    cast(shipping_fee as double) as shipping_fee,
    cast(net_amount as double) as net_amount,
    cast(items_count as integer) as items_count
from raw.orders;

