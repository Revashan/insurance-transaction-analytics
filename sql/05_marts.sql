CREATE OR REPLACE VIEW mart.vw_transaction_detail AS
SELECT
    t.transaction_id,
    t.transaction_date,
    t.transaction_type,
    t.transaction_amount,
    t.payment_method,
    t.payment_status,
    t.transaction_channel,
    t.processing_seconds,
    t.failure_reason,
    p.policy_id,
    p.product_type,
    p.policy_status,
    p.renewal_flag,
    c.customer_id,
    c.state,
    c.city,
    c.income_band,
    c.risk_segment,
    a.agent_id,
    a.sales_channel,
    a.region AS agent_region
FROM warehouse.fact_transaction t
JOIN warehouse.dim_policy p ON p.policy_id = t.policy_id
JOIN warehouse.dim_customer c ON c.customer_id = p.customer_id
JOIN warehouse.dim_agent a ON a.agent_id = p.agent_id;

CREATE OR REPLACE VIEW mart.vw_claim_detail AS
SELECT
    cl.claim_id,
    cl.claim_date,
    cl.claim_type,
    cl.claim_amount,
    cl.approved_amount,
    cl.claim_status,
    cl.days_to_settle,
    cl.fraud_score,
    cl.fraud_flag,
    p.policy_id,
    p.product_type,
    c.customer_id,
    c.state,
    c.city,
    c.risk_segment,
    a.agent_id,
    a.sales_channel,
    a.region AS agent_region
FROM warehouse.fact_claim cl
JOIN warehouse.dim_policy p ON p.policy_id = cl.policy_id
JOIN warehouse.dim_customer c ON c.customer_id = p.customer_id
JOIN warehouse.dim_agent a ON a.agent_id = p.agent_id;

CREATE OR REPLACE VIEW mart.vw_monthly_kpi AS
WITH premium AS (
    SELECT
        DATE_TRUNC('month', transaction_date)::date AS month,
        SUM(transaction_amount) AS premium_collected,
        COUNT(*) AS premium_transactions,
        COUNT(*) FILTER (WHERE payment_status = 'FAILED') AS failed_transactions
    FROM warehouse.fact_transaction
    WHERE transaction_type = 'PREMIUM_PAYMENT'
    GROUP BY 1
),
claims AS (
    SELECT
        DATE_TRUNC('month', claim_date)::date AS month,
        SUM(approved_amount) FILTER (WHERE claim_status = 'APPROVED') AS approved_claim_amount,
        COUNT(*) AS claim_count,
        AVG(days_to_settle) FILTER (WHERE claim_status IN ('APPROVED','REJECTED') AND days_to_settle > 0) AS avg_settlement_days,
        COUNT(*) FILTER (WHERE fraud_flag = 1) AS fraud_flagged_claims
    FROM warehouse.fact_claim
    GROUP BY 1
)
SELECT
    COALESCE(p.month, c.month) AS month,
    COALESCE(p.premium_collected,0) AS premium_collected,
    COALESCE(c.approved_claim_amount,0) AS approved_claim_amount,
    CASE WHEN COALESCE(p.premium_collected,0) = 0 THEN NULL
         ELSE COALESCE(c.approved_claim_amount,0) / p.premium_collected END AS loss_ratio,
    COALESCE(p.premium_transactions,0) AS premium_transactions,
    COALESCE(p.failed_transactions,0) AS failed_transactions,
    COALESCE(c.claim_count,0) AS claim_count,
    c.avg_settlement_days,
    COALESCE(c.fraud_flagged_claims,0) AS fraud_flagged_claims
FROM premium p
FULL OUTER JOIN claims c ON c.month = p.month;

CREATE OR REPLACE VIEW mart.vw_product_performance AS
WITH premium AS (
    SELECT p.product_type,
           SUM(t.transaction_amount) FILTER (WHERE t.transaction_type='PREMIUM_PAYMENT' AND t.payment_status='SUCCESS') premium_collected
    FROM warehouse.fact_transaction t
    JOIN warehouse.dim_policy p ON p.policy_id=t.policy_id
    GROUP BY 1
), claims AS (
    SELECT p.product_type,
           SUM(c.approved_amount) FILTER (WHERE c.claim_status='APPROVED') approved_claim_amount,
           AVG(c.days_to_settle) FILTER (WHERE c.days_to_settle>0) avg_settlement_days
    FROM warehouse.fact_claim c
    JOIN warehouse.dim_policy p ON p.policy_id=c.policy_id
    GROUP BY 1
)
SELECT p.product_type,
       p.premium_collected,
       COALESCE(c.approved_claim_amount,0) approved_claim_amount,
       CASE WHEN p.premium_collected=0 THEN NULL ELSE COALESCE(c.approved_claim_amount,0)/p.premium_collected END loss_ratio,
       c.avg_settlement_days
FROM premium p
LEFT JOIN claims c USING(product_type);
