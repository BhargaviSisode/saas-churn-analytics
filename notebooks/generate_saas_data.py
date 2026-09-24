import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

print("[-] Generating B2B SaaS dataset...")
os.makedirs('data/raw', exist_ok=True)

np.random.seed(42)
n_customers = 5000

# 1. Generate Customers Table
print("    -> Generating Customers...")
customer_ids = [f"CUST_{str(i).zfill(5)}" for i in range(1, n_customers + 1)]
industries = np.random.choice(['FinTech', 'Healthcare', 'E-commerce', 'EdTech', 'Logistics'], n_customers)
segments = np.random.choice(['SMB', 'Mid-Market', 'Enterprise'], n_customers, p=[0.6, 0.3, 0.1])

customers = pd.DataFrame({
    'customer_id': customer_ids,
    'industry': industries,
    'segment': segments,
    'signup_date': [datetime(2022, 1, 1) + timedelta(days=np.random.randint(0, 700)) for _ in range(n_customers)]
})

# 2. Generate Subscriptions Table (MRR & Churn Logic)
print("    -> Generating Subscriptions & MRR...")
plans = {'Starter': 49, 'Pro': 199, 'Enterprise': 999}
assigned_plans = np.random.choice(list(plans.keys()), n_customers, p=[0.5, 0.4, 0.1])
mrrs = [plans[p] for p in assigned_plans]

# Business Logic: Enterprises churn less (10%), SMBs churn more (35%)
churn_prob = np.where(segments == 'Enterprise', 0.10, np.where(segments == 'Mid-Market', 0.20, 0.35))
churned = np.random.binomial(1, churn_prob)

end_dates = []
for i in range(n_customers):
    if churned[i] == 1:
        # Churn happens between 1 and 12 months after signup
        end_dates.append(customers['signup_date'][i] + timedelta(days=np.random.randint(30, 365)))
    else:
        end_dates.append(pd.NaT)

subscriptions = pd.DataFrame({
    'subscription_id': [f"SUB_{str(i).zfill(5)}" for i in range(1, n_customers + 1)],
    'customer_id': customer_ids,
    'plan_tier': assigned_plans,
    'mrr': mrrs,
    'start_date': customers['signup_date'],
    'end_date': end_dates,
    'status': np.where(churned == 1, 'Churned', 'Active')
})

# 3. Generate Feature Usage Table (Activity Drop-off)
print("    -> Generating Feature Usage Logs...")
usage = pd.DataFrame({
    'customer_id': customer_ids,
    # Business Logic: Churned users have very low recent logins
    'logins_last_30_days': np.where(churned == 1, np.random.randint(0, 5, n_customers), np.random.randint(5, 50, n_customers)),
    'reports_generated': np.where(churned == 1, np.random.randint(0, 2, n_customers), np.random.randint(1, 15, n_customers)),
    'api_calls': np.where(assigned_plans == 'Enterprise', np.random.randint(1000, 50000, n_customers), np.random.randint(0, 1000, n_customers))
})

# 4. Generate Support Tickets Table
print("    -> Generating Support Tickets...")
n_tickets = 12000
ticket_customers = np.random.choice(customer_ids, n_tickets)
ticket_priorities = np.random.choice(['Low', 'Medium', 'High', 'Critical'], n_tickets, p=[0.4, 0.4, 0.15, 0.05])
    
tickets = pd.DataFrame({
    'ticket_id': [f"TKT_{str(i).zfill(6)}" for i in range(1, n_tickets + 1)],
    'customer_id': ticket_customers,
    'priority': ticket_priorities,
    'resolution_time_hours': np.where(ticket_priorities == 'Critical', np.random.randint(1, 24, n_tickets), np.random.randint(12, 72, n_tickets)),
    'satisfaction_score': np.random.choice([1, 2, 3, 4, 5], n_tickets, p=[0.1, 0.1, 0.2, 0.3, 0.3])
})

# Save to CSV in data/raw
customers.to_csv('data/raw/customers.csv', index=False)
subscriptions.to_csv('data/raw/subscriptions.csv', index=False)
usage.to_csv('data/raw/feature_usage.csv', index=False)
tickets.to_csv('data/raw/support_tickets.csv', index=False)

print("[✓] Success! Relational CSVs generated in 'data/raw' folder.")