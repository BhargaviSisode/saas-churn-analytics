"""
notebooks/02_etl_pipeline.py
Transforms relational tables into an Analytical Mart for Power BI visualization.
"""

import os
import pandas as pd
import numpy as np

def run_etl():
    print("[-] Starting Analytical Mart Transformation...")
    
    raw_dir = os.path.join("data", "raw")
    processed_dir = os.path.join("data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    customers = pd.read_csv(os.path.join(raw_dir, "customers.csv"))
    subscriptions = pd.read_csv(os.path.join(raw_dir, "subscriptions.csv"))
    usage = pd.read_csv(os.path.join(raw_dir, "feature_usage.csv"))
    tickets = pd.read_csv(os.path.join(raw_dir, "support_tickets.csv"))
    
    # 1. Aggregate Support Tickets per customer
    ticket_summary = tickets.groupby("customer_id").agg(
        ticket_count=("ticket_id", "count"),
        avg_resolution_time=("resolution_time_hours", "mean"),
        avg_csat=("satisfaction_score", "mean")
    ).reset_index()
    
    # 2. Merge master data
    mart = customers.merge(subscriptions, on="customer_id", how="inner")
    mart = mart.merge(usage, on="customer_id", how="inner")
    mart = mart.merge(ticket_summary, on="customer_id", how="left")
    
    # 3. Handle accounts with no support tickets
    mart["ticket_count"] = mart["ticket_count"].fillna(0)
    mart["avg_resolution_time"] = mart["avg_resolution_time"].fillna(0)
    mart["avg_csat"] = mart["avg_csat"].fillna(5.0)
    
    # 4. Feature Engineering
    mart["is_churned"] = np.where(mart["status"] == "Churned", 1, 0)
    
    # Engagement classification
    conditions = [
        (mart["logins_last_30_days"] <= 5),
        (mart["logins_last_30_days"] > 5) & (mart["logins_last_30_days"] <= 15),
        (mart["logins_last_30_days"] > 15)
    ]
    labels = ["High Risk (≤5 logins)", "Medium Risk (6-15 logins)", "Healthy (16+ logins)"]
    mart["engagement_risk_tier"] = np.select(conditions, labels, default="Unknown")
    
    # Customer Lifetime in Days
    mart["signup_date"] = pd.to_datetime(mart["signup_date"])
    mart["end_date"] = pd.to_datetime(mart["end_date"])
    mart["tenure_days"] = np.where(
        mart["is_churned"] == 1,
        (mart["end_date"] - mart["signup_date"]).dt.days,
        (pd.to_datetime("2024-01-01") - mart["signup_date"]).dt.days
    )
    
    # Export clean analytical mart
    output_file = os.path.join(processed_dir, "saas_churn_mart.csv")
    mart.to_csv(output_file, index=False)
    
    print(f"[✓] Mart successfully created at: {output_file}")
    print(f"    Total Accounts:    {len(mart):,}")
    print(f"    Overall Churn Rate: {mart['is_churned'].mean() * 100:.2f}%")
    print(f"    Total ARR:         ${mart['mrr'].sum() * 12:,.2f}")

if __name__ == "__main__":
    run_etl()