INSERT INTO warehouse.fact_transaction
(transaction_id, policy_id, transaction_date, transaction_type, transaction_amount,
 payment_method, payment_status, transaction_channel, processing_seconds, failure_reason,
 source_updated_at, dw_updated_at)
SELECT transaction_id, policy_id, transaction_date, transaction_type, transaction_amount,
       payment_method, payment_status, transaction_channel, processing_seconds, NULLIF(failure_reason,''),
       source_updated_at, CURRENT_TIMESTAMP
FROM staging.transactions
ON CONFLICT (transaction_id) DO UPDATE SET
    policy_id = EXCLUDED.policy_id,
    transaction_date = EXCLUDED.transaction_date,
    transaction_type = EXCLUDED.transaction_type,
    transaction_amount = EXCLUDED.transaction_amount,
    payment_method = EXCLUDED.payment_method,
    payment_status = EXCLUDED.payment_status,
    transaction_channel = EXCLUDED.transaction_channel,
    processing_seconds = EXCLUDED.processing_seconds,
    failure_reason = EXCLUDED.failure_reason,
    source_updated_at = EXCLUDED.source_updated_at,
    dw_updated_at = CURRENT_TIMESTAMP;

INSERT INTO warehouse.fact_claim
(claim_id, policy_id, claim_date, claim_type, claim_amount, approved_amount, claim_status,
 days_to_settle, fraud_score, fraud_flag, source_updated_at, dw_updated_at)
SELECT claim_id, policy_id, claim_date, claim_type, claim_amount, approved_amount, claim_status,
       days_to_settle, fraud_score, fraud_flag, source_updated_at, CURRENT_TIMESTAMP
FROM staging.claims
ON CONFLICT (claim_id) DO UPDATE SET
    policy_id = EXCLUDED.policy_id,
    claim_date = EXCLUDED.claim_date,
    claim_type = EXCLUDED.claim_type,
    claim_amount = EXCLUDED.claim_amount,
    approved_amount = EXCLUDED.approved_amount,
    claim_status = EXCLUDED.claim_status,
    days_to_settle = EXCLUDED.days_to_settle,
    fraud_score = EXCLUDED.fraud_score,
    fraud_flag = EXCLUDED.fraud_flag,
    source_updated_at = EXCLUDED.source_updated_at,
    dw_updated_at = CURRENT_TIMESTAMP;
