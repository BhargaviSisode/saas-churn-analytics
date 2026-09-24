-- sql/02_business_kpis.sql: Executive SaaS KPIs & Cohort Analysis

-- =========================================================================
-- KPI 1: Monthly Churn Rate & Net Revenue Retention (NRR) by Plan Tier
-- Evaluates logo churn vs. revenue churn
-- =========================================================================
WITH tier_metrics AS (
    SELECT 
        s.plan_tier,
        COUNT(s.customer_id) AS total_customers,
        SUM(CASE WHEN s.status = 'Churned' THEN 1 ELSE 0 END) AS churned_customers,
        SUM(s.mrr) AS total_potential_mrr,
        SUM(CASE WHEN s.status = 'Churned' THEN s.mrr ELSE 0 END) AS lost_mrr,
        SUM(CASE WHEN s.status = 'Active' THEN s.mrr ELSE 0 END) AS active_mrr
    FROM subscriptions s
    GROUP BY s.plan_tier
)
SELECT 
    plan_tier,
    total_customers,
    churned_customers,
    ROUND((churned_customers::numeric / total_customers) * 100, 2) AS logo_churn_pct,
    total_potential_mrr,
    lost_mrr,
    active_mrr,
    ROUND((lost_mrr::numeric / total_potential_mrr) * 100, 2) AS revenue_churn_pct
FROM tier_metrics
ORDER BY lost_mrr DESC;


-- =========================================================================
-- KPI 2: Customer Acquisition Cohort Retention Matrix
-- Uses window functions to track retention decay across sign-up cohorts
-- =========================================================================
WITH cohort_base AS (
    SELECT 
        c.customer_id,
        TO_CHAR(c.signup_date, 'YYYY-MM') AS signup_cohort,
        s.status,
        s.start_date,
        s.end_date,
        CASE 
            WHEN s.end_date IS NOT NULL THEN 
                (EXTRACT(YEAR FROM s.end_date) - EXTRACT(YEAR FROM s.start_date)) * 12 + 
                (EXTRACT(MONTH FROM s.end_date) - EXTRACT(MONTH FROM s.start_date))
            ELSE 999 
        END AS months_until_churn
    FROM customers c
    JOIN subscriptions s ON c.customer_id = s.customer_id
)
SELECT 
    signup_cohort,
    COUNT(customer_id) AS cohort_size,
    ROUND(SUM(CASE WHEN months_until_churn >= 1 THEN 1 ELSE 0 END)::numeric / COUNT(customer_id) * 100, 1) AS m1_retention_pct,
    ROUND(SUM(CASE WHEN months_until_churn >= 3 THEN 1 ELSE 0 END)::numeric / COUNT(customer_id) * 100, 1) AS m3_retention_pct,
    ROUND(SUM(CASE WHEN months_until_churn >= 6 THEN 1 ELSE 0 END)::numeric / COUNT(customer_id) * 100, 1) AS m6_retention_pct,
    ROUND(SUM(CASE WHEN months_until_churn >= 12 THEN 1 ELSE 0 END)::numeric / COUNT(customer_id) * 100, 1) AS m12_retention_pct
FROM cohort_base
GROUP BY signup_cohort
ORDER BY signup_cohort ASC;


-- =========================================================================
-- KPI 3: Behavioral Telemetry & Feature Drop-off Analysis
-- Shows the direct correlation between login frequency and churn risk
-- =========================================================================
SELECT 
    CASE 
        WHEN u.logins_last_30_days = 0 THEN '0 Logins (Dormant)'
        WHEN u.logins_last_30_days BETWEEN 1 AND 5 THEN '1-5 Logins (At Risk)'
        WHEN u.logins_last_30_days BETWEEN 6 AND 15 THEN '6-15 Logins (Moderate)'
        ELSE '16+ Logins (Highly Active)'
    END AS usage_engagement_tier,
    COUNT(c.customer_id) AS total_accounts,
    SUM(CASE WHEN s.status = 'Churned' THEN 1 ELSE 0 END) AS churned_accounts,
    ROUND((SUM(CASE WHEN s.status = 'Churned' THEN 1 ELSE 0 END)::numeric / COUNT(c.customer_id)) * 100, 2) AS churn_rate_pct,
    ROUND(AVG(u.reports_generated), 1) AS avg_reports_created,
    ROUND(AVG(u.api_calls), 0) AS avg_api_usage
FROM customers c
JOIN subscriptions s ON c.customer_id = s.customer_id
JOIN feature_usage u ON c.customer_id = u.customer_id
GROUP BY 1
ORDER BY churn_rate_pct DESC;


-- =========================================================================
-- KPI 4: Support Ticket Health & Customer Dissatisfaction Trigger
-- Evaluates if slow resolution times cause high-value account cancellations
-- =========================================================================
WITH ticket_summary AS (
    SELECT 
        customer_id,
        COUNT(ticket_id) AS total_tickets,
        AVG(resolution_time_hours) AS avg_resolution_hours,
        AVG(satisfaction_score) AS avg_csat
    FROM support_tickets
    GROUP BY customer_id
)
SELECT 
    c.segment,
    ROUND(AVG(ts.total_tickets), 1) AS avg_tickets_per_account,
    ROUND(AVG(ts.avg_resolution_hours), 1) AS avg_resolution_time_hrs,
    ROUND(AVG(ts.avg_csat), 2) AS avg_csat_score,
    ROUND((SUM(CASE WHEN s.status = 'Churned' THEN 1 ELSE 0 END)::numeric / COUNT(c.customer_id)) * 100, 2) AS segment_churn_pct
FROM customers c
JOIN subscriptions s ON c.customer_id = s.customer_id
LEFT JOIN ticket_summary ts ON c.customer_id = ts.customer_id
GROUP BY c.segment
ORDER BY segment_churn_pct DESC;