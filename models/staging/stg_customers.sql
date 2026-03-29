create or replace table staging.stg_customers as
select
    customer_id,
    first_name,
    last_name,
    lower(email) as email,
    city,
    country,
    cast(signup_date as date) as signup_date,
    acquisition_channel
from raw.customers;

