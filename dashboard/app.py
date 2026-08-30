import pandas as pd
import psycopg2
import streamlit as st
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "fintech"),
    "user": os.getenv("DB_USER", "fintech"),
    "password": os.getenv("DB_PASSWORD", "fintech_dev_password"),
}
@st.cache_resource
def get_connection():
    return psycopg2.connect(**DB_CONFIG)


@st.cache_data(ttl=300)
def load_query(query, params=None):
    connection = get_connection()
    return pd.read_sql_query(query, connection, params=params)


# -------------------------
# Page configuration
# -------------------------

st.set_page_config(
    page_title="Fintech Transaction Intelligence",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -------------------------
# Sidebar
# -------------------------

with st.sidebar:
    st.title("💳 Fintech Intelligence")

    st.markdown("---")

    st.markdown("### Dashboard")
    st.write("Transaction performance and operational analytics.")

    st.markdown("---")

    st.markdown("### Data Coverage")
    st.write("10,000 transactions")
    st.write("200 merchants")
    st.write("1,000 accounts")

    st.markdown("---")

    st.caption("Powered by PostgreSQL + dbt + Airflow + Streamlit")

    st.markdown("---")

    st.markdown("### Date Range")

    start_date = st.date_input(
        "Start date",
        value=pd.Timestamp("2026-05-01").date(),
    )

    end_date = st.date_input(
        "End date",
        value=pd.Timestamp("2026-07-31").date(),
    )


# -------------------------
# Header
# -------------------------

st.title("💳 Fintech Transaction Dashboard")
st.caption(
    "Executive overview of transaction performance, "
    "payment methods, merchant categories, and risk."
)


# -------------------------
# Load executive KPIs
# -------------------------

summary = load_query(
    """
    SELECT
        COUNT(*) AS total_transactions,

        COUNT(*) FILTER (
            WHERE status = 'success'
        ) AS successful_transactions,

        COUNT(*) FILTER (
            WHERE status = 'failed'
        ) AS failed_transactions,

        COUNT(*) FILTER (
            WHERE status = 'pending'
        ) AS pending_transactions,

        COALESCE(SUM(amount), 0) AS total_amount,

        ROUND(
            COALESCE(
                100.0 * COUNT(*) FILTER (
                    WHERE status = 'success'
                ) / NULLIF(COUNT(*), 0),
                0
            ),
            2
        ) AS success_rate,

        ROUND(
            COALESCE(
                100.0 * COUNT(*) FILTER (
                    WHERE status = 'failed'
                ) / NULLIF(COUNT(*), 0),
                0
            ),
            2
        ) AS failure_rate

    FROM mart.fact_transactions
    WHERE transaction_timestamp::date
          BETWEEN %(start_date)s AND %(end_date)s
    """,
    params={"start_date": start_date, "end_date": end_date},
)

kpi = summary.iloc[0]


# -------------------------
# KPI cards
# -------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Transactions",
    f"{int(kpi['total_transactions']):,}",
)

col2.metric(
    "Total Transaction Value",
    f"₹{kpi['total_amount']:,.2f}",
)

col3.metric(
    "Overall Success Rate",
    f"{kpi['success_rate']:.2f}%",
)

col4.metric(
    "Overall Failure Rate",
    f"{kpi['failure_rate']:.2f}%",
)

# -------------------------
# Daily transaction trends
# -------------------------

st.markdown("---")
st.subheader("Daily Transaction Trends")

daily = load_query(
    """
    SELECT
        date_key,
        total_transactions,
        total_amount
    FROM mart.fct_daily_transactions
    WHERE TO_DATE(date_key::text, 'YYYYMMDD')
          BETWEEN %(start_date)s AND %(end_date)s
    ORDER BY date_key
    """,
    params={"start_date": start_date, "end_date": end_date},
)
daily["date"] = pd.to_datetime(
    daily["date_key"].astype(str),
    format="%Y%m%d"
)

col1, col2 = st.columns(2)

with col1:
    st.caption("Transaction Volume")
    st.line_chart(
        daily.set_index("date")["total_transactions"]
    )

with col2:
    st.caption("Transaction Value")
    st.line_chart(
        daily.set_index("date")["total_amount"]
    )

# -------------------------
# Payment method performance
# -------------------------

st.markdown("---")
st.subheader("Payment Method Performance")

payment_methods = load_query(
    """
    SELECT
        payment_method,
        COUNT(*) AS total_transactions,
        ROUND(
            100.0 * COUNT(*) FILTER (
                WHERE status = 'success'
            ) / NULLIF(COUNT(*), 0),
            2
        ) AS success_rate
    FROM mart.fact_transactions
    WHERE transaction_timestamp::date
          BETWEEN %(start_date)s AND %(end_date)s
    GROUP BY payment_method
    ORDER BY total_transactions DESC
    """,
    params={"start_date": start_date, "end_date": end_date},
)

col1, col2 = st.columns(2)

with col1:
    st.caption("Transaction Volume by Payment Method")

    st.bar_chart(
        payment_methods.set_index("payment_method")[
            "total_transactions"
        ]
    )

with col2:
    st.caption("Success Rate by Payment Method")

    st.bar_chart(
        payment_methods.set_index("payment_method")[
            "success_rate"
        ]
    )

# -------------------------
# Merchant category performance
# -------------------------

categories = load_query(
    """
    SELECT
        dm.category,
        COUNT(*) AS total_transactions,
        SUM(ft.amount) AS total_amount,
        ROUND(
            100.0 * COUNT(*) FILTER (
                WHERE ft.status = 'success'
            ) / NULLIF(COUNT(*), 0),
            2
        ) AS success_rate
    FROM mart.fact_transactions ft
    INNER JOIN mart.dim_merchants dm
        ON ft.merchant_key = dm.merchant_key
    WHERE ft.transaction_timestamp::date
          BETWEEN %(start_date)s AND %(end_date)s
    GROUP BY dm.category
    ORDER BY total_transactions DESC
    """,
    params={"start_date": start_date, "end_date": end_date},
)
col1, col2 = st.columns(2)

with col1:
    st.caption("Transaction Volume by Category")

    st.bar_chart(
        categories.set_index("category")[
            "total_transactions"
        ]
    )

with col2:
    st.caption("Transaction Value by Category")

    st.bar_chart(
        categories.set_index("category")[
            "total_amount"
        ]
    )

st.caption("Success Rate by Merchant Category")

st.bar_chart(
    categories.set_index("category")[
        "success_rate"
    ]
)

# -------------------------
# Risk analysis
# -------------------------

st.markdown("---")
st.subheader("Merchant Risk Analysis")
risk = load_query(
    """
    SELECT
        dm.risk_category,
        COUNT(*) AS total_transactions,
        ROUND(
            100.0 * COUNT(*) FILTER (
                WHERE ft.status = 'success'
            ) / NULLIF(COUNT(*), 0),
            2
        ) AS success_rate,
        COUNT(*) FILTER (
            WHERE ft.status = 'failed'
        ) AS failed_transactions,
        COALESCE(
            SUM(ft.amount) FILTER (
                WHERE ft.status = 'failed'
            ),
            0
        ) AS failed_amount
    FROM mart.fact_transactions ft
    INNER JOIN mart.dim_merchants dm
        ON ft.merchant_key = dm.merchant_key
    WHERE ft.transaction_timestamp::date
          BETWEEN %(start_date)s AND %(end_date)s
    GROUP BY dm.risk_category
    ORDER BY total_transactions DESC
    """,
    params={"start_date": start_date, "end_date": end_date},
)

col1, col2 = st.columns(2)

with col1:
    st.caption("Transaction Volume by Risk Category")

    st.bar_chart(
        risk.set_index("risk_category")[
            "total_transactions"
        ]
    )

with col2:
    st.caption("Success Rate by Risk Category")

    st.bar_chart(
        risk.set_index("risk_category")[
            "success_rate"
        ]
    )

st.caption("Failed Transaction Value by Risk Category")

st.bar_chart(
    risk.set_index("risk_category")[
        "failed_amount"
    ]
)
# -------------------------
# Key business insights
# -------------------------

st.markdown("---")
st.subheader("Key Business Insights")

best_payment = payment_methods.loc[
    payment_methods["success_rate"].idxmax()
]

worst_payment = payment_methods.loc[
    payment_methods["success_rate"].idxmin()
]

best_category = categories.loc[
    categories["success_rate"].idxmax()
]

worst_category = categories.loc[
    categories["success_rate"].idxmin()
]

highest_failed_risk = risk.loc[
    risk["failed_amount"].idxmax()
]

col1, col2, col3 = st.columns(3)

with col1:
    st.info(
        f"**Best payment method**\n\n"
        f"{best_payment['payment_method'].title()} "
        f"with a {best_payment['success_rate']:.2f}% success rate."
    )

with col2:
    st.warning(
        f"**Weakest merchant category**\n\n"
        f"{worst_category['category'].title()} "
        f"with a {worst_category['success_rate']:.2f}% success rate."
    )

with col3:
    st.error(
        f"**Highest failed-value risk**\n\n"
        f"{highest_failed_risk['risk_category'].title()} risk "
        f"with ₹{highest_failed_risk['failed_amount']:,.2f} "
        f"in failed transactions."
    )