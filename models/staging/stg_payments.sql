create or replace table staging.stg_payments as
select
    payment_id,
    order_id,
    cast(payment_date as date) as payment_date,
    payment_method,
    lower(payment_status) as payment_status,
    cast(amount as double) as amount,
    cast(refunded_amount as double) as refunded_amount
from raw.payments;

