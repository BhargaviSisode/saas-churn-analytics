import streamlit as st
import pandas as pd

st.set_page_config(page_title="SaaS Churn Analytics", layout="wide")
st.title("📊 B2B SaaS Customer Churn Analytics Dashboard")

# ---------- LOAD DATA ----------
df = pd.read_csv('data/processed/saas_churn_mart.csv')

# ---------- SIDEBAR FILTERS ----------
st.sidebar.header("Filters")
segment_filter = st.sidebar.multiselect(
    "Select Segment", 
    options=df['segment'].unique(), 
    default=df['segment'].unique()
)
plan_filter = st.sidebar.multiselect(
    "Select Plan Tier", 
    options=df['plan_tier'].unique(), 
    default=df['plan_tier'].unique()
)

filtered_df = df[(df['segment'].isin(segment_filter)) & (df['plan_tier'].isin(plan_filter))]

# ---------- KPIs ----------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", f"{len(filtered_df):,}")
col2.metric("Churn Rate", f"{filtered_df['is_churned'].mean()*100:.1f}%")
col3.metric("Total MRR", f"${filtered_df[filtered_df['status']=='Active']['mrr'].sum():,.0f}")
col4.metric("Avg CSAT Score", f"{filtered_df['avg_csat'].mean():.2f}")

st.divider()

# ---------- CHURN BY SEGMENT ----------
st.subheader("Churn Rate by Segment")
churn_by_segment = filtered_df.groupby('segment')['is_churned'].mean() * 100
st.bar_chart(churn_by_segment)

# ---------- CHURN BY PLAN TIER ----------
st.subheader("Churn Rate by Plan Tier")
churn_by_plan = filtered_df.groupby('plan_tier')['is_churned'].mean() * 100
st.bar_chart(churn_by_plan)

# ---------- ENGAGEMENT RISK TIER ----------
st.subheader("Customer Distribution by Engagement Risk")
risk_distribution = filtered_df['engagement_risk_tier'].value_counts()
st.bar_chart(risk_distribution)

# ---------- CHURN BY INDUSTRY ----------
st.subheader("Churn Rate by Industry")
churn_by_industry = filtered_df.groupby('industry')['is_churned'].mean().sort_values(ascending=False) * 100
st.bar_chart(churn_by_industry)

# ---------- RAW DATA ----------
st.subheader("Raw Data Explorer")
st.dataframe(filtered_df)