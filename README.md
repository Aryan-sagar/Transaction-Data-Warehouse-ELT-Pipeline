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

## Future Improvements

- Incremental dbt models
- Automated anomaly detection and transaction-level fraud scoring
- Dashboard authentication
- CI/CD with GitHub Actions
- Cloud deployment
- Real-time transaction ingestion and automated data-quality alerts

---

**Author:** Aryan Sagar
