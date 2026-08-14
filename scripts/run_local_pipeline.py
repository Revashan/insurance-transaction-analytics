from src.pipeline import (
    validate_raw_files, initialize_database, load_staging,
    build_warehouse, data_quality, export_powerbi, audit_success
)

if __name__ == "__main__":
    print("1/7 Validate:", validate_raw_files())
    print("2/7 Initializing database...")
    initialize_database()
    print("3/7 Stage:", load_staging())
    print("4/7 Building warehouse...")
    build_warehouse()
    print("5/7 Quality:", data_quality())
    print("6/7 Exports:", export_powerbi())
    print("7/7 Audit...")
    audit_success("manual_local_run")
    print("Pipeline completed successfully.")
