"""
notebooks/load_to_postgres.py
Automates ingestion from raw CSVs to PostgreSQL relational database.
"""

import os
import pandas as pd
from sqlalchemy import create_engine

# Update with your local PostgreSQL credentials
DB_USER = "postgres"
DB_PASS = "admin"       # replace with your local postgres password
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "saas_analytics"

def load_data():
    conn_str = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(conn_str)
    
    raw_dir = os.path.join("data", "raw")
    
    print("[-] Connecting to PostgreSQL and ingesting datasets...")
    
    # Order matters due to Foreign Key constraints
    tables = [
        ("customers.csv", "customers"),
        ("subscriptions.csv", "subscriptions"),
        ("feature_usage.csv", "feature_usage"),
        ("support_tickets.csv", "support_tickets")
    ]
    
    for filename, table_name in tables:
        path = os.path.join(raw_dir, filename)
        df = pd.read_csv(path)
        print(f"    -> Loading {filename} into {table_name} ({len(df):,} rows)...")
        df.to_sql(table_name, engine, if_exists="append", index=False)
        
    print("[✓] All tables successfully ingested into PostgreSQL!")

if __name__ == "__main__":
    load_data()