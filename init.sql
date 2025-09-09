-- users 
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE,
  business_name VARCHAR(255) NOT NULL,
  business_structure VARCHAR(50) NOT NULL, -- e.g. sole_trader, limited_company
  vat_enabled BOOLEAN NOT NULL,
  has_employees BOOLEAN NOT NULL,
  num_employees INTEGER,
  fiscal_year_start DATE DEFAULT '2025-04-06',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- user_plaid_accounts
CREATE TABLE user_plaid_accounts (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  item_id VARCHAR(255) UNIQUE NOT NULL,
  access_token VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- transactions
CREATE TABLE transactions (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  plaid_transaction_id VARCHAR(255) UNIQUE,
  date DATE NOT NULL,
  description TEXT NOT NULL,
  amount NUMERIC(12,2) NOT NULL,
  source VARCHAR(50) DEFAULT 'manual', -- manual, plaid, import
  plaid_category VARCHAR(255),
  tax_category VARCHAR(255),
  vat_rate NUMERIC(4,2),
  vat_amount NUMERIC(12,2),
  deductible BOOLEAN DEFAULT TRUE,
  needs_review BOOLEAN DEFAULT FALSE,
  confidence NUMERIC(3,2) DEFAULT 1.0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- category mapping
CREATE TABLE category_mappings (
  id SERIAL PRIMARY KEY,
  plaid_category VARCHAR(255) NOT NULL,
  tax_category VARCHAR(255) NOT NULL,
  deductible BOOLEAN DEFAULT TRUE,
  vat_applicable BOOLEAN DEFAULT TRUE,
  notes TEXT
);

-- transaction override
CREATE TABLE transaction_overrides (
  id SERIAL PRIMARY KEY,
  transaction_id INT REFERENCES transactions(id),
  user_id INT REFERENCES users(id),
  new_tax_category VARCHAR(255),
  reason TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- tax summaries
CREATE TABLE tax_summaries (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  total_income NUMERIC(12,2),
  total_expenses NUMERIC(12,2),
  vat_due NUMERIC(12,2),
  vat_reclaimable NUMERIC(12,2),
  net_profit NUMERIC(12,2),
  generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- conversation logs
CREATE TABLE conversation_logs (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  input_text TEXT NOT NULL,
  llm_response JSONB NOT NULL,
  task_type VARCHAR(100),
  source_model VARCHAR(100),
  session_id VARCHAR(255)
);

-- scenario logs 
CREATE TABLE scenario_logs (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  prompt TEXT NOT NULL,
  response JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- feedback logs 
CREATE TABLE feedback_logs (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  feedback TEXT NOT NULL,
  task_type VARCHAR(100) DEFAULT 'general',
  source_model VARCHAR(100) DEFAULT 'user',
  session_id VARCHAR(255),
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);