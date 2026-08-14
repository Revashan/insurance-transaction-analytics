from __future__ import annotations
from pathlib import Path
import os
from .db import execute_sql_file, load_csv_replace, query_df, get_connection
from .data_quality import run_checks

PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", "/opt/airflow/project"))
RAW = PROJECT_ROOT / "data" / "raw"
SQL = PROJECT_ROOT / "sql"
OUT = PROJECT_ROOT / "data" / "processed" / "powerbi"

RAW_TABLES = {
    "customers": "staging.customers",
    "agents": "staging.agents",
    "policies": "staging.policies",
    "transactions": "staging.transactions",
    "claims": "staging.claims",
}

def validate_raw_files() -> dict[str, int]:
    result = {}
    required_columns = {
        "customers": {"customer_id","state","risk_segment"},
        "agents": {"agent_id","sales_channel"},
        "policies": {"policy_id","customer_id","agent_id","product_type"},
        "transactions": {"transaction_id","policy_id","transaction_date","payment_status"},
        "claims": {"claim_id","policy_id","claim_date","claim_status"},
    }
    import pandas as pd
    for name, cols in required_columns.items():
        path = RAW / f"{name}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Missing required raw file: {path}")
        df = pd.read_csv(path, nrows=50)
        missing = cols - set(df.columns)
        if missing:
            raise ValueError(f"{name}.csv missing columns: {sorted(missing)}")
        result[name] = sum(1 for _ in path.open("r", encoding="utf-8")) - 1
        if result[name] <= 0:
            raise ValueError(f"{name}.csv has no data rows")
    return result

def initialize_database() -> None:
    for file in ["00_create_schemas.sql","01_create_staging.sql","02_create_warehouse.sql"]:
        execute_sql_file(SQL / file)

def load_staging() -> dict[str, int]:
    counts = {}
    for name, table in RAW_TABLES.items():
        counts[name] = load_csv_replace(table, RAW / f"{name}.csv")
    return counts

def build_warehouse() -> None:
    for file in ["03_upsert_dimensions.sql","04_upsert_facts.sql","05_marts.sql"]:
        execute_sql_file(SQL / file)

def data_quality() -> dict[str, int]:
    return run_checks()

def export_powerbi() -> list[str]:
    OUT.mkdir(parents=True, exist_ok=True)
    exports = {
        "transaction_detail.csv": "SELECT * FROM mart.vw_transaction_detail;",
        "claim_detail.csv": "SELECT * FROM mart.vw_claim_detail;",
        "monthly_kpis.csv": "SELECT * FROM mart.vw_monthly_kpi ORDER BY month;",
        "product_performance.csv": "SELECT * FROM mart.vw_product_performance ORDER BY product_type;",
        "dim_customer.csv": "SELECT * FROM warehouse.dim_customer;",
        "dim_agent.csv": "SELECT * FROM warehouse.dim_agent;",
        "dim_policy.csv": "SELECT * FROM warehouse.dim_policy;",
        "fact_transaction.csv": "SELECT * FROM warehouse.fact_transaction;",
        "fact_claim.csv": "SELECT * FROM warehouse.fact_claim;",
    }
    paths = []
    for filename, sql in exports.items():
        path = OUT / filename
        query_df(sql).to_csv(path, index=False)
        paths.append(str(path))
    return paths

def audit_success(dag_id: str = "insurance_transaction_analytics") -> None:
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""
        INSERT INTO audit.pipeline_run
        (dag_id,status,customers_count,policies_count,transactions_count,claims_count,notes)
        SELECT %s,'SUCCESS',
               (SELECT COUNT(*) FROM warehouse.dim_customer),
               (SELECT COUNT(*) FROM warehouse.dim_policy),
               (SELECT COUNT(*) FROM warehouse.fact_transaction),
               (SELECT COUNT(*) FROM warehouse.fact_claim),
               'All quality checks passed and Power BI exports created';
        """, (dag_id,))
        conn.commit()
