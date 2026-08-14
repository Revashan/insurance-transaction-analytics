-- 1. Monthly premium, claims and loss ratio
SELECT * FROM mart.vw_monthly_kpi ORDER BY month;

-- 2. Products with highest loss ratio
SELECT product_type, premium_collected, approved_claim_amount,
       ROUND(loss_ratio * 100, 2) AS loss_ratio_pct
FROM mart.vw_product_performance
ORDER BY loss_ratio DESC;

-- 3. Payment failure reasons
SELECT failure_reason, COUNT(*) AS failures,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS failure_share_pct
FROM warehouse.fact_transaction
WHERE payment_status = 'FAILED'
GROUP BY failure_reason
ORDER BY failures DESC;

-- 4. Channel performance
SELECT transaction_channel,
       COUNT(*) AS transactions,
       ROUND(100.0 * AVG((payment_status='SUCCESS')::int),2) AS success_rate_pct,
       ROUND(AVG(processing_seconds),2) AS avg_processing_seconds
FROM warehouse.fact_transaction
GROUP BY transaction_channel
ORDER BY transactions DESC;

-- 5. High-risk fraud candidates
SELECT c.claim_id, c.policy_id, p.product_type, c.claim_amount, c.fraud_score,
       cu.state, cu.risk_segment
FROM warehouse.fact_claim c
JOIN warehouse.dim_policy p ON p.policy_id=c.policy_id
JOIN warehouse.dim_customer cu ON cu.customer_id=p.customer_id
WHERE c.fraud_flag=1
ORDER BY c.fraud_score DESC, c.claim_amount DESC
LIMIT 100;

-- 6. Customer segment claim behaviour
SELECT cu.risk_segment,
       COUNT(c.claim_id) AS claims,
       ROUND(AVG(c.claim_amount),2) AS avg_claim_amount,
       ROUND(100.0 * AVG((c.claim_status='APPROVED')::int),2) AS approval_rate_pct
FROM warehouse.fact_claim c
JOIN warehouse.dim_policy p ON p.policy_id=c.policy_id
JOIN warehouse.dim_customer cu ON cu.customer_id=p.customer_id
GROUP BY cu.risk_segment
ORDER BY claims DESC;

-- 7. Renewal performance by product
SELECT product_type,
       COUNT(*) AS expired_or_renewed,
       SUM(renewal_flag) AS renewed,
       ROUND(100.0 * AVG(renewal_flag),2) AS renewal_rate_pct
FROM warehouse.dim_policy
WHERE policy_status IN ('Expired','Renewed')
GROUP BY product_type
ORDER BY renewal_rate_pct DESC;
