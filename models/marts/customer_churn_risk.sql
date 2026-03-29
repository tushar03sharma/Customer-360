create or replace table marts.customer_churn_risk as
with scored as (
    select
        customer_id,
        acquisition_channel,
        completed_orders,
        lifetime_revenue,
        days_since_last_order,
        total_tickets,
        high_priority_tickets,
        avg_csat_score,
        refunded_amount,
        cancelled_orders,
        failed_payments,
        least(
            100,
            coalesce(
                case
                    when completed_orders = 0 then 45
                    when days_since_last_order >= 180 then 55
                    when days_since_last_order >= 120 then 42
                    when days_since_last_order >= 75 then 28
                    when days_since_last_order >= 45 then 16
                    else 6
                end,
                45
            )
            + case when refunded_amount >= 150 then 16 when refunded_amount > 0 then 8 else 0 end
            + case when failed_payments >= 2 then 12 when failed_payments = 1 then 6 else 0 end
            + case when total_tickets >= 4 then 10 when total_tickets >= 2 then 5 else 0 end
            + case when high_priority_tickets >= 2 then 8 when high_priority_tickets = 1 then 4 else 0 end
            + case when avg_csat_score > 0 and avg_csat_score <= 2.5 then 12 when avg_csat_score <= 3.5 then 6 else 0 end
        ) as churn_risk_score
    from (
        select
            c360.*,
            coalesce(summary.failed_payments, 0) as failed_payments
        from marts.customer_360 c360
        left join core.customer_order_summary summary on c360.customer_id = summary.customer_id
    )
)
select
    customer_id,
    acquisition_channel,
    completed_orders,
    lifetime_revenue,
    days_since_last_order,
    total_tickets,
    avg_csat_score,
    churn_risk_score,
    case
        when churn_risk_score >= 70 then 'High'
        when churn_risk_score >= 40 then 'Medium'
        else 'Low'
    end as churn_risk_band,
    case
        when completed_orders = 0 then 'Activate with onboarding and first-order offers'
        when churn_risk_score >= 70 then 'Trigger win-back journey with support follow-up'
        when churn_risk_score >= 40 then 'Use targeted bundles before inactivity deepens'
        else 'Keep in loyalty flow and cross-sell'
    end as recommended_action
from scored;

