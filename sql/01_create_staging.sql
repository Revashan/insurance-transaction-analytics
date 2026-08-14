CREATE TABLE IF NOT EXISTS staging.customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    gender VARCHAR(20),
    date_of_birth DATE,
    state VARCHAR(100),
    city VARCHAR(100),
    income_band VARCHAR(30),
    risk_segment VARCHAR(20),
    customer_since DATE,
    source_updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.agents (
    agent_id VARCHAR(20) PRIMARY KEY,
    agent_name VARCHAR(100),
    sales_channel VARCHAR(50),
    region VARCHAR(50),
    tenure_years INTEGER,
    source_updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.policies (
    policy_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20),
    agent_id VARCHAR(20),
    product_type VARCHAR(50),
    policy_start_date DATE,
    policy_end_date DATE,
    annual_premium NUMERIC(14,2),
    sum_insured NUMERIC(16,2),
    payment_frequency VARCHAR(30),
    policy_status VARCHAR(30),
    renewal_flag INTEGER,
    source_updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.transactions (
    transaction_id VARCHAR(30) PRIMARY KEY,
    policy_id VARCHAR(20),
    transaction_date DATE,
    transaction_type VARCHAR(40),
    transaction_amount NUMERIC(16,2),
    payment_method VARCHAR(40),
    payment_status VARCHAR(30),
    transaction_channel VARCHAR(40),
    processing_seconds NUMERIC(12,2),
    failure_reason VARCHAR(200),
    source_updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.claims (
    claim_id VARCHAR(30) PRIMARY KEY,
    policy_id VARCHAR(20),
    claim_date DATE,
    claim_type VARCHAR(60),
    claim_amount NUMERIC(16,2),
    approved_amount NUMERIC(16,2),
    claim_status VARCHAR(30),
    days_to_settle INTEGER,
    fraud_score NUMERIC(7,2),
    fraud_flag INTEGER,
    source_updated_at TIMESTAMP
);
