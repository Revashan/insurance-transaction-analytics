# Windows Setup — Airflow with Docker Desktop + WSL2

Apache Airflow does not support native Windows deployment. This repository therefore runs Airflow in Linux containers through Docker Desktop / WSL2.

## Prerequisites
1. Windows 10/11 with virtualization enabled.
2. WSL2 installed.
3. Docker Desktop configured to use the WSL2 engine.
4. Git.
5. Power BI Desktop (optional, for the dashboard).

## First-time setup
Open PowerShell as Administrator:
```powershell
wsl --install
```
Restart Windows if requested.

Install Docker Desktop and ensure **Use the WSL 2 based engine** is enabled.

## Run the project
From PowerShell or Windows Terminal:
```powershell
cd path\to\insurance_transaction_analytics
docker compose build
docker compose up -d
```

Check containers:
```powershell
docker compose ps
```

Airflow UI:
`http://localhost:8080`

Retrieve the generated Airflow standalone credentials:
```powershell
docker compose exec airflow cat /opt/airflow/simple_auth_manager_passwords.json.generated
```

In Airflow:
1. Open DAG `insurance_transaction_analytics`.
2. Unpause it.
3. Click **Trigger DAG** for the first run.
4. Check Graph/Grid view and task logs.

PostgreSQL reporting database from Windows:
- Host: localhost
- Port: 5433
- Database: insurance_analytics
- User: analytics
- Password: analytics

## Stop
```powershell
docker compose down
```

## Full reset
This deletes local Postgres and Airflow volumes:
```powershell
docker compose down -v
docker compose up -d --build
```

## Notes for a real organisation
The included Compose deployment is a local development/portfolio environment. For production:
- use a managed PostgreSQL metadata database;
- use secret management instead of credentials in Compose;
- use remote object storage for logs;
- deploy Airflow on a Linux/Kubernetes-based runtime;
- add CI/CD, image scanning, RBAC/SSO, backups and monitoring.
