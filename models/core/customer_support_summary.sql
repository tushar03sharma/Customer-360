create or replace table core.customer_support_summary as
select
    customer_id,
    count(*) as total_tickets,
    count(*) filter (where priority = 'High') as high_priority_tickets,
    round(avg(resolution_hours), 1) as avg_resolution_hours,
    round(avg(csat_score), 2) as avg_csat_score
from core.fct_support_tickets
group by 1;

