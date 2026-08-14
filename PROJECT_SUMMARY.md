# Project Summary — Insurance Transaction Analytics

## Business problem
An insurer needs one reporting layer for payment operations, premium collection, claims performance,
customer/policy segmentation and fraud-risk monitoring. Source files arrive daily and must be validated,
loaded into a governed warehouse, checked for quality and exposed to Power BI without manual notebook steps.

## Solution
- **Orchestration:** Apache Airflow 3.3.0 TaskFlow DAG
- **Windows runtime:** Docker Desktop + WSL2/Linux containers
- **Warehouse:** PostgreSQL 16 with staging, warehouse, mart and audit schemas
- **Transformation:** Python + PostgreSQL SQL
- **BI:** Power BI star-schema model and DAX measures
- **Quality:** schema checks, primary-key checks, domain checks, referential-integrity checks
- **Operational design:** retries, idempotent staging reloads, UPSERT facts/dimensions, audit table
- **Dataset:** deterministic synthetic insurance dataset designed for portfolio/learning use

## Dataset scale
- Customers: 6,000
- Agents: 80
- Policies: 9,000
- Transactions: 75,000
- Claims: 12,000

## Portfolio KPI snapshot
- Premium collected: RM 44,363,262
- Approved claim amount: RM 29,024,314
- Loss ratio: 65.4%
- Transaction success rate: 93.3%
- Active policies: 2,084
- Renewal rate (expired/renewed population): 53.7%
- Average settled-claim processing time: 13.4 days
- Fraud flagged claims: 381
- Fraud exposure: RM 1,696,102

## What this demonstrates in an interview
1. Designing an analytics pipeline rather than only analysing a CSV.
2. Airflow DAG orchestration with explicit dependencies and quality gates.
3. PostgreSQL staging -> dimensional warehouse -> marts.
4. Idempotent UPSERT patterns that are retry-safe.
5. Insurance domain KPIs: loss ratio, premium collection, claims, settlement SLA, fraud exposure, renewals.
6. Power BI semantic modelling and DAX.
7. Windows-compatible local engineering through Docker/WSL2.
