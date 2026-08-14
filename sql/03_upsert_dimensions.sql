INSERT INTO warehouse.dim_customer
(customer_id, gender, date_of_birth, state, city, income_band, risk_segment, customer_since, source_updated_at, dw_updated_at)
SELECT customer_id, gender, date_of_birth, state, city, income_band, risk_segment, customer_since, source_updated_at, CURRENT_TIMESTAMP
FROM staging.customers
ON CONFLICT (customer_id) DO UPDATE SET
    gender = EXCLUDED.gender,
    date_of_birth = EXCLUDED.date_of_birth,
    state = EXCLUDED.state,
    city = EXCLUDED.city,
    income_band = EXCLUDED.income_band,
    risk_segment = EXCLUDED.risk_segment,
    customer_since = EXCLUDED.customer_since,
    source_updated_at = EXCLUDED.source_updated_at,
    dw_updated_at = CURRENT_TIMESTAMP;

INSERT INTO warehouse.dim_agent
(agent_id, agent_name, sales_channel, region, tenure_years, source_updated_at, dw_updated_at)
SELECT agent_id, agent_name, sales_channel, region, tenure_years, source_updated_at, CURRENT_TIMESTAMP
FROM staging.agents
ON CONFLICT (agent_id) DO UPDATE SET
    agent_name = EXCLUDED.agent_name,
    sales_channel = EXCLUDED.sales_channel,
    region = EXCLUDED.region,
    tenure_years = EXCLUDED.tenure_years,
    source_updated_at = EXCLUDED.source_updated_at,
    dw_updated_at = CURRENT_TIMESTAMP;

INSERT INTO warehouse.dim_policy
(policy_id, customer_id, agent_id, product_type, policy_start_date, policy_end_date,
 annual_premium, sum_insured, payment_frequency, policy_status, renewal_flag, source_updated_at, dw_updated_at)
SELECT policy_id, customer_id, agent_id, product_type, policy_start_date, policy_end_date,
       annual_premium, sum_insured, payment_frequency, policy_status, renewal_flag, source_updated_at, CURRENT_TIMESTAMP
FROM staging.policies
ON CONFLICT (policy_id) DO UPDATE SET
    customer_id = EXCLUDED.customer_id,
    agent_id = EXCLUDED.agent_id,
    product_type = EXCLUDED.product_type,
    policy_start_date = EXCLUDED.policy_start_date,
    policy_end_date = EXCLUDED.policy_end_date,
    annual_premium = EXCLUDED.annual_premium,
    sum_insured = EXCLUDED.sum_insured,
    payment_frequency = EXCLUDED.payment_frequency,
    policy_status = EXCLUDED.policy_status,
    renewal_flag = EXCLUDED.renewal_flag,
    source_updated_at = EXCLUDED.source_updated_at,
    dw_updated_at = CURRENT_TIMESTAMP;
