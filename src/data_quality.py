from __future__ import annotations
from dataclasses import dataclass
from .db import get_connection

@dataclass(frozen=True)
class Check:
    name: str
    sql: str
    expected: int = 0

CHECKS = [
    Check("null_transaction_keys",
          "SELECT COUNT(*) FROM warehouse.fact_transaction WHERE transaction_id IS NULL OR policy_id IS NULL;"),
    Check("duplicate_transaction_ids",
          """SELECT COUNT(*) FROM (
                 SELECT transaction_id FROM warehouse.fact_transaction
                 GROUP BY transaction_id HAVING COUNT(*) > 1
             ) x;"""),
    Check("invalid_payment_status",
          """SELECT COUNT(*) FROM warehouse.fact_transaction
             WHERE payment_status NOT IN ('SUCCESS','FAILED','PENDING');"""),
    Check("null_claim_keys",
          "SELECT COUNT(*) FROM warehouse.fact_claim WHERE claim_id IS NULL OR policy_id IS NULL;"),
    Check("invalid_claim_amount",
          "SELECT COUNT(*) FROM warehouse.fact_claim WHERE claim_amount < 0 OR approved_amount < 0;"),
    Check("invalid_fraud_score",
          "SELECT COUNT(*) FROM warehouse.fact_claim WHERE fraud_score < 0 OR fraud_score > 100;"),
    Check("orphan_transaction_policy",
          """SELECT COUNT(*) FROM warehouse.fact_transaction t
             LEFT JOIN warehouse.dim_policy p ON p.policy_id=t.policy_id
             WHERE p.policy_id IS NULL;"""),
]

def run_checks() -> dict[str, int]:
    results = {}
    with get_connection() as conn, conn.cursor() as cur:
        for check in CHECKS:
            cur.execute(check.sql)
            actual = int(cur.fetchone()[0])
            results[check.name] = actual
            if actual != check.expected:
                raise ValueError(
                    f"Data quality failed: {check.name}; expected {check.expected}, got {actual}"
                )

        for table in [
            "warehouse.dim_customer", "warehouse.dim_policy",
            "warehouse.fact_transaction", "warehouse.fact_claim"
        ]:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            if cur.fetchone()[0] == 0:
                raise ValueError(f"Data quality failed: {table} is empty")
    return results
