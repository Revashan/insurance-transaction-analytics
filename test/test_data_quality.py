from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def test_raw_primary_keys_unique():
    checks = {
        "customers.csv": "customer_id",
        "agents.csv": "agent_id",
        "policies.csv": "policy_id",
        "transactions.csv": "transaction_id",
        "claims.csv": "claim_id",
    }
    for filename, key in checks.items():
        df = pd.read_csv(ROOT / "data" / "raw" / filename)
        assert df[key].notna().all()
        assert not df[key].duplicated().any()

def test_transaction_status_domain():
    df = pd.read_csv(ROOT / "data" / "raw" / "transactions.csv")
    assert set(df["payment_status"]).issubset({"SUCCESS","FAILED","PENDING"})

def test_claim_values():
    df = pd.read_csv(ROOT / "data" / "raw" / "claims.csv")
    assert (df["claim_amount"] >= 0).all()
    assert (df["approved_amount"] >= 0).all()
    assert df["fraud_score"].between(0,100).all()

def test_foreign_keys():
    policy = set(pd.read_csv(ROOT / "data" / "raw" / "policies.csv")["policy_id"])
    tx = pd.read_csv(ROOT / "data" / "raw" / "transactions.csv")
    claims = pd.read_csv(ROOT / "data" / "raw" / "claims.csv")
    assert set(tx["policy_id"]).issubset(policy)
    assert set(claims["policy_id"]).issubset(policy)
