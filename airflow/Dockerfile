FROM apache/airflow:3.1.0

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

RUN pip install --no-cache-dir \
    psycopg2-binary \
    dbt-postgres==1.11.0