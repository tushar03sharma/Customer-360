create or replace table staging.stg_support_tickets as
select
    ticket_id,
    customer_id,
    nullif(order_id, '') as order_id,
    cast(created_at as date) as created_at,
    issue_type,
    priority,
    cast(resolution_hours as double) as resolution_hours,
    cast(csat_score as integer) as csat_score,
    lower(ticket_status) as ticket_status
from raw.support_tickets;

