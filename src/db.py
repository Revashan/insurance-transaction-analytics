from __future__ import annotations
import os
from pathlib import Path
import psycopg2
import pandas as pd

PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", "/opt/airflow/project"))
DB_URL = os.getenv(
    "ANALYTICS_DB_URL",
    "postgresql://analytics:analytics@postgres:5432/insurance_analytics",
)

def get_connection():
    return psycopg2.connect(DB_URL)

def execute_sql_file(path: str | Path) -> None:
    sql = Path(path).read_text(encoding="utf-8")
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()

def load_csv_replace(table: str, csv_path: str | Path) -> int:
    """Idempotent staging load: truncate then PostgreSQL COPY."""
    csv_path = Path(csv_path)
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE {table};")
        with csv_path.open("r", encoding="utf-8") as f:
            cur.copy_expert(
                f"COPY {table} FROM STDIN WITH CSV HEADER NULL ''",
                f
            )
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        count = cur.fetchone()[0]
        conn.commit()
    return count

def query_df(sql: str) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn)
