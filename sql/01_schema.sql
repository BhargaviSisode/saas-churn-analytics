-- sql/01_schema.sql: Relational Schema Definition

DROP TABLE IF EXISTS support_tickets;
DROP TABLE IF EXISTS feature_usage;
DROP TABLE IF EXISTS subscriptions;
DROP TABLE IF EXISTS customers;

-- 1. Customers Master Table
CREATE TABLE customers (
    customer_id VARCHAR(16) PRIMARY KEY,
    industry VARCHAR(32) NOT NULL,
    segment VARCHAR(32) NOT NULL,
    signup_date DATE NOT NULL
);

-- 2. Subscriptions & Billing Table
CREATE TABLE subscriptions (
    subscription_id VARCHAR(16) PRIMARY KEY,
    customer_id VARCHAR(16) REFERENCES customers(customer_id) ON DELETE CASCADE,
    plan_tier VARCHAR(20) NOT NULL,
    mrr NUMERIC(10, 2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(16) NOT NULL
);

-- 3. Telemetry & Feature Usage Table
CREATE TABLE feature_usage (
    customer_id VARCHAR(16) PRIMARY KEY REFERENCES customers(customer_id) ON DELETE CASCADE,
    logins_last_30_days INT NOT NULL,
    reports_generated INT NOT NULL,
    api_calls INT NOT NULL
);

-- 4. Customer Support Tickets Table
CREATE TABLE support_tickets (
    ticket_id VARCHAR(16) PRIMARY KEY,
    customer_id VARCHAR(16) REFERENCES customers(customer_id) ON DELETE CASCADE,
    priority VARCHAR(16) NOT NULL,
    resolution_time_hours INT NOT NULL,
    satisfaction_score INT CHECK (satisfaction_score BETWEEN 1 AND 5)
);

-- Create strategic indexes for fast analytical query execution
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_customer_id ON subscriptions(customer_id);
CREATE INDEX idx_support_customer_id ON support_tickets(customer_id);