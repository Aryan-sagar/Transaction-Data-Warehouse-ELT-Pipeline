# Transaction Data Warehouse & ELT Pipeline

An end-to-end fintech transaction data platform: ingestion, dimensional modeling, automated data-quality testing, and an interactive analytics dashboard.

**Stack:** PostgreSQL · Apache Airflow · dbt · Streamlit · Pandas · Docker

---

## Overview

Raw transaction, account, and merchant data is ingested into PostgreSQL, orchestrated through Airflow, and transformed by dbt into a dimensional warehouse. dbt tests enforce data quality at every layer, and a Streamlit dashboard exposes the resulting analytics — KPIs, trends, payment method performance, merchant category breakdowns, and risk analysis.

## Architecture

```
Raw CSV Data
     │
     ▼
PostgreSQL  ──▶  Airflow Orchestration
     │
     ▼
Raw ──▶ Staging ──▶ Dimensional Warehouse
                          │
        ┌─────────────┬──┴──┬──────────────┐
        ▼             ▼     ▼              ▼
  dim_accounts  dim_merchants  dim_date  fact_transactions
                                              │
                                              ▼
                                      Analytics Marts
                          ┌───────────┬────────┴────────┬───────────┐
                          ▼           ▼                 ▼           ▼
                    Daily Payment  Merchant        Risk Analytics
                    Analytics      Methods         Categories
                          └───────────┴────────┬────────┘
                                                ▼
                                     Dashboard Summary
                                                │
                                                ▼
                                     Streamlit Dashboard
```

## Data Pipeline

**1. Raw layer** — CSV datasets (accounts, merchants, transactions) land in PostgreSQL.

**2. Staging layer** — Standardizes and prepares raw data for transformation.

**3. Dimensional warehouse** — Star-schema design:
- **Dimensions:** `dim_accounts`, `dim_merchants`, `dim_date`
- **Fact:** `fact_transactions`

**4. Analytics layer** — Business-facing marts:
- `fct_daily_transactions`
- `fct_payment_method`
- `fct_merchant_category`
- `fct_risk_category`
- `fct_dashboard_summary`

## Data Quality

Enforced with **48 dbt tests** covering not-null constraints, uniqueness, staging integrity, and analytical model integrity.

Core model validation: `PASS=11  WARN=0  ERROR=0`

## Dashboard

Interactive Streamlit app with date-range filtering across all sections:

| Section | Metrics |
|---|---|
| Executive KPIs | Total transactions, total value, success rate, failure rate |
| Transaction Trends | Daily volume, daily value |
| Payment Methods | Volume by method, success rate by method |
| Merchant Categories | Volume, value, success rate |
| Risk Analysis | Volume by risk tier, success rate by risk tier, failed value by risk tier |

It also auto-surfaces business insights: best-performing payment method, weakest merchant category, and the risk tier with the highest failed transaction value.

## Key Results

| Metric | Result |
|---|---|
| Transactions | 10,000 |
| Successful | 9,372 |
| Failed | 430 |
| Pending | 198 |
| Total transaction value | ₹4,136,431.64 |
| Success rate | 93.72% |

**Payment methods** — UPI leads on success rate (94.05%); net banking trails (93.24%); wallet drives the highest transaction value.

**Merchant categories** — Healthcare has the highest volume; utilities the highest value; grocery the highest success rate; travel the lowest.

**Risk** — Low-risk merchants dominate transaction share; medium-risk merchants post the highest success rate; high-risk merchants are a small slice of overall activity.

## Running the Project

**Prerequisites:** Docker Desktop, Python 3.12+, Git

**1. Start infrastructure**
```bash
docker compose up -d
```
Brings up the PostgreSQL warehouse and Airflow services.

**2. Run dbt**
```bash
cd fintech_warehouse
dbt run
dbt test
```

**3. Run the dashboard locally**
```bash
cd ../dashboard
pip install -r requirements.txt
python -m streamlit run app.py
```
Available at `http://localhost:8501`

**3b. Or run the dashboard via Docker**
```bash
docker compose up -d postgres dashboard
```

## Project Structure

```
fintech-transaction-warehouse/
├── airflow/
│   ├── dags/
│   ├── dbt/
│   └── Dockerfile
├── dashboard/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── data/
│   └── raw/
├── fintech_warehouse/
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   ├── dbt_project.yml
│   └── profiles.yml
├── src/
│   └── pipeline/
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

## Engineering Highlights

- End-to-end batch data pipeline with containerized PostgreSQL warehouse
- Airflow orchestration and dimensional/star-schema modeling
- dbt transformation layer with automated data-quality testing
- Reusable analytical marts and dynamic business insight generation
- Interactive Streamlit dashboard with dynamic date filtering
- Fully Dockerized dashboard-to-database connectivity

## Failure Modes & Recovery

[#failure-modes--recovery](#failure-modes--recovery)

This is a single-node batch pipeline, not a distributed system — no
multi-node consensus, no network partitions between independent
stores. What follows are the concrete partial-failure and consistency
modes that *do* apply to an orchestrated batch ELT pipeline like this
one, what's been fixed, and what's still open.

| # | Failure mode | Status | Fix |
|---|---|---|---|
| 1 | A failed/retried Airflow task re-runs ingestion, but re-inserting an existing `transaction_id` is a no-op — so a real status correction (`pending` → `success`) on an already-ingested row was silently dropped, both at the raw layer and downstream. | **Fixed** | `ingestion.py` now upserts (`ON CONFLICT ... DO UPDATE`) when `status` or `amount` actually changed, instead of `DO NOTHING`. |
| 2 | `fact_transactions`'s incremental filter watermarked on `transaction_timestamp`, which never changes at the source — so even with raw fixed, a status correction on an old transaction would never re-cross the watermark and reach the fact table. | **Fixed** | Incremental filter now watermarks on `ingested_at` (which advances on every upsert), with `source_ingested_at` carried onto the fact table to compare against. |
| 3 | `dbt run --select marts` builds table-by-table with no atomicity. If it fails partway (or `dbt test` fails after), the dashboard — which queries the same schema dbt just built into — can read a half-rebuilt or untested warehouse with no signal anything's wrong. | **Fixed** | Marts always build into a shadow schema, `mart_next` (`macros/generate_schema_name.sql`). A new `promote_marts` DAG task runs `swap_mart_schema()` (`macros/swap_mart_schema.sql`) only after `dbt_test_marts` passes, atomically renaming `mart_next` → `mart` in one transaction. A failed build or failed test leaves `mart` serving the last known-good state; the dashboard never sees an in-progress or failed run. |
| 4 | Two DAG runs (e.g. a manual backfill and the hourly schedule) can overlap and write to the same tables concurrently — nothing currently prevents this. | Open | Add `max_active_runs=1` on the DAG, or an Airflow pool / Postgres advisory lock acquired in `ingest_raw`. |
| 5 | `ingestion.py` reads each CSV fully into a Python list before `executemany` — fine at 10k rows, an OOM risk at real-world volume. | Open | Stream via `psycopg2.extras.copy_expert` (`COPY`) or chunked batches instead of one in-memory list. |
| 6 | DB password is hardcoded in `docker-compose.yml` and in the DAG's task `env=` dict. | Open | Move to `.env` + `${POSTGRES_PASSWORD}` in compose, and an Airflow Connection (`PostgresHook`) instead of a literal dict in the DAG. |
| 7 | `stg_transactions.sql` silently drops rows failing `amount > 0` / null checks — invalid data just disappears with no audit trail. | Open | Route failing rows to a `stg_transactions_quarantine` model instead of filtering them out. |
| 8 | Postgres is a single instance serving both the write path (ingestion, dbt builds) and the read path (dashboard) — no replica, no failover. | Open | Add a read replica (or at least a separate pooled connection) for the dashboard so write load and read load don't contend, and the dashboard has somewhere to fail over to. |

## Future Improvements

- Incremental dbt models
- Automated anomaly detection and transaction-level fraud scoring
- Dashboard authentication
- CI/CD with GitHub Actions
- Cloud deployment
- Real-time transaction ingestion and automated data-quality alerts

---

**Author:** Aryan Sagar
