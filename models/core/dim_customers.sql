create or replace table core.dim_customers as
select
    customer_id,
    first_name,
    last_name,
    email,
    city,
    country,
    signup_date,
    acquisition_channel,
    date_diff('day', signup_date, current_date) as customer_age_days
from staging.stg_customers;

