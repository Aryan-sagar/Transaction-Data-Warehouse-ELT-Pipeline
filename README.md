\# Fintech Transaction Warehouse



An end-to-end fintech transaction data platform built with \*\*PostgreSQL, Apache Airflow, dbt, Docker, Python, and Streamlit\*\*.



The project ingests raw transaction data, transforms it into a dimensional warehouse, validates data quality with automated dbt tests, and exposes the resulting analytics through an interactive fintech dashboard.



\---



\## Architecture



```text

Raw CSV Data

&#x20;    │

&#x20;    ▼

PostgreSQL

&#x20;    │

&#x20;    ▼

Airflow Orchestration

&#x20;    │

&#x20;    ▼

Raw → Staging

&#x20;    │

&#x20;    ▼

Dimensional Warehouse

&#x20;    │

&#x20;    ├── dim\_accounts

&#x20;    ├── dim\_merchants

&#x20;    ├── dim\_date

&#x20;    └── fact\_transactions

&#x20;             │

&#x20;             ▼

&#x20;       Analytics Marts

&#x20;             │

&#x20;       ┌─────┼──────────────┐

&#x20;       ▼     ▼              ▼

&#x20;     Daily Payment      Merchant

&#x20;    Analytics Methods    Categories

&#x20;       │     │              │

&#x20;       └─────┼──────────────┘

&#x20;             ▼

&#x20;       Risk Analytics

&#x20;             │

&#x20;             ▼

&#x20;     Dashboard Summary

&#x20;             │

&#x20;             ▼

&#x20;       Streamlit Dashboard

Tech Stack

Python — ingestion and application logic

PostgreSQL 16 — data warehouse

Apache Airflow — workflow orchestration

dbt — transformation and data quality

Streamlit — interactive dashboard

Pandas — analytical data handling

Docker / Docker Compose — reproducible infrastructure

Git / GitHub — version control

Data Pipeline



The pipeline processes transaction, account, and merchant data through several layers.



1\. Raw Layer



Raw CSV datasets are ingested into PostgreSQL.



Sources include:



Accounts

Merchants

Transactions

2\. Staging Layer



Staging models standardize and prepare raw data for analytical transformations.



3\. Dimensional Warehouse



The warehouse follows a dimensional/star-schema design.



Dimensions

dim\_accounts

dim\_merchants

dim\_date

Fact

fact\_transactions

4\. Analytics Layer



The warehouse produces business-focused marts:



fct\_daily\_transactions

fct\_payment\_method

fct\_merchant\_category

fct\_risk\_category

fct\_dashboard\_summary

Data Quality



Data quality is enforced using dbt tests.



The project currently contains 48 data tests covering:



Not-null constraints

Uniqueness

Staging data integrity

Analytical model integrity



The core analytical models were validated successfully with:

PASS=11

WARN=0

ERROR=0

Dashboard



The Streamlit dashboard provides an interactive view of transaction performance.



Executive KPIs

Total transactions

Total transaction value

Overall success rate

Overall failure rate

Transaction Trends

Daily transaction volume

Daily transaction value

Payment Methods

Transaction volume by payment method

Success rate by payment method

Merchant Categories

Transaction volume

Transaction value

Success rate

Risk Analysis

Transaction volume by risk category

Success rate by risk category

Failed transaction value by risk category

Business Insights



The dashboard dynamically identifies:



Best-performing payment method

Weakest merchant category

Risk category with the highest failed transaction value

Interactive Filtering



All major dashboard sections respond to a selectable date range.



Key Results



The current dataset contains:



Metric	Result

Transactions	10,000

Successful	9,372

Failed	430

Pending	198

Total transaction value	₹4,136,431.64

Success rate	93.72%

Payment Method Insights

UPI has the highest success rate at 94.05%

Net banking has the lowest success rate at 93.24%

Wallet has the highest transaction value

Merchant Category Insights

Healthcare has the highest transaction volume

Utilities has the highest transaction value

Grocery has the highest success rate

Travel has the lowest success rate

Risk Insights

Low-risk merchants account for the majority of transactions

Medium-risk merchants currently have the highest success rate

High-risk merchants represent a smaller share of overall transaction activity

Running the Project

Prerequisites

Docker Desktop

Python 3.12+

Git

Start the infrastructure



From the project root:

docker compose up -d

This starts the PostgreSQL warehouse and Airflow services.



Run dbt



Navigate to the dbt project:

cd fintech\_warehouse



Build the models:

dbt run



Run the data-quality tests:

dbt test



Run the dashboard locally

Navigate to the dashboard:



cd ../dashboard



Install dependencies:

pip install -r requirements.txt



Start Streamlit:

python -m streamlit run app.py



The dashboard will be available at:

http://localhost:8501



Run the dashboard with Docker

From the project root:
docker compose up -d postgres dashboard

Then open:
http://localhost:8501


Project Structure

fintech-transaction-warehouse/
│
├── airflow/
│   ├── dags/
│   ├── dbt/
│   └── Dockerfile
│
├── dashboard/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── data/
│   └── raw/
│
├── fintech_warehouse/
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   ├── dbt_project.yml
│   └── profiles.yml
│
├── src/
│   └── pipeline/
│
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md


Engineering Highlights

End-to-end batch data pipeline
Containerized PostgreSQL warehouse
Airflow orchestration
Dimensional/star-schema modeling
dbt transformation layer
Automated data-quality testing
Reusable analytical marts
Interactive Streamlit dashboard
Dynamic date filtering
Business insight generation
Dockerized dashboard-to-database connectivity
Git-based version control


Future Improvements

Potential extensions include:
Incremental dbt models
Automated anomaly detection
Transaction-level fraud scoring
Dashboard authentication
CI/CD with GitHub Actions
Cloud deployment
Real-time transaction ingestion
Automated data-quality alerts

Author

Aryan Sagar
