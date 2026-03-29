create or replace table core.fct_support_tickets as
select
    ticket_id,
    customer_id,
    order_id,
    created_at,
    issue_type,
    priority,
    resolution_hours,
    csat_score,
    ticket_status,
    case when priority = 'High' then 3 when priority = 'Medium' then 2 else 1 end as priority_score
from staging.stg_support_tickets;

