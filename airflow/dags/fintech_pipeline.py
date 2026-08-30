from datetime import datetime ,timedelta

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="fintech_transaction_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 * * * *",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["fintech", "warehouse"],
) as dag:

    ingest_raw = BashOperator(
        task_id="ingest_raw",
        env={
            "DB_HOST": "postgres",
            "DB_PORT": "5432",
            "DB_NAME": "fintech",
            "DB_USER": "fintech",
            "DB_PASSWORD": "fintech_dev_password",
        },
        bash_command="""
            cd /opt/airflow/project

            echo "=== RAW INGESTION ==="
            echo "Database host: $DB_HOST"

            python src/pipeline/ingestion.py
        """,
    )

    dbt_staging = BashOperator(
        task_id="dbt_staging",
        bash_command="""
            cd /opt/airflow/project/fintech_warehouse

            echo "=== DBT STAGING ==="

            dbt run --select staging
        """,
    )

    dbt_test_staging = BashOperator(
        task_id="dbt_test_staging",
        bash_command="""
            cd /opt/airflow/project/fintech_warehouse

            echo "=== DBT TESTS: STAGING ==="

            dbt test --select staging
        """,
    )

    dbt_marts = BashOperator(
        task_id="dbt_marts",
        bash_command="""
            cd /opt/airflow/project/fintech_warehouse

            echo "=== DBT MARTS ==="

            dbt run --select marts
        """,
    )

    dbt_test_marts = BashOperator(
        task_id="dbt_test_marts",
        bash_command="""
            cd /opt/airflow/project/fintech_warehouse

            echo "=== DBT TESTS: MARTS ==="

            dbt test --select marts
        """,
    )

    # Staging is tested before marts are built off it (fail fast on bad
    # source data), and marts are tested only after they exist — testing
    # them beforehand would just error on missing relations.
    ingest_raw >> dbt_staging >> dbt_test_staging >> dbt_marts >> dbt_test_marts