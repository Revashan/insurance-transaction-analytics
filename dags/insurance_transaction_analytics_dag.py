from __future__ import annotations
import pendulum
from airflow.sdk import dag, task

@dag(
    dag_id="insurance_transaction_analytics",
    schedule="0 2 * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="Asia/Kuala_Lumpur"),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2},
    tags=["insurance", "analytics", "powerbi", "postgresql"],
    doc_md="""
    ## Insurance Transaction Analytics
    Daily orchestration of raw insurance customers, policies, premium/payment transactions
    and claims into a PostgreSQL analytics warehouse with quality gates and Power BI exports.
    """,
)
def insurance_transaction_analytics():

    @task
    def validate():
        from src.pipeline import validate_raw_files
        return validate_raw_files()

    @task
    def init_db():
        from src.pipeline import initialize_database
        initialize_database()

    @task
    def stage():
        from src.pipeline import load_staging
        return load_staging()

    @task
    def warehouse():
        from src.pipeline import build_warehouse
        build_warehouse()

    @task
    def quality():
        from src.pipeline import data_quality
        return data_quality()

    @task
    def export():
        from src.pipeline import export_powerbi
        return export_powerbi()

    @task
    def audit():
        from src.pipeline import audit_success
        audit_success()

    validation = validate()
    initialized = init_db()
    validation >> initialized
    staged = stage()
    initialized >> staged
    built = warehouse()
    staged >> built
    checked = quality()
    built >> checked
    exported = export()
    checked >> exported
    audited = audit()
    exported >> audited

insurance_transaction_analytics()
