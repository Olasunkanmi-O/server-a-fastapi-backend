-- USERS
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  business_name VARCHAR(255) NOT NULL,
  business_structure VARCHAR(50) NOT NULL, -- e.g. sole_trader, limited_company
  vat_enabled BOOLEAN NOT NULL,
  has_employees BOOLEAN NOT NULL,
  num_employees INTEGER,
  fiscal_year_start DATE DEFAULT '2025-04-06',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- USER PLAID ACCOUNTS
CREATE TABLE user_plaid_accounts (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id) ON DELETE CASCADE,
  item_id VARCHAR(255) UNIQUE NOT NULL,
  access_token VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TRANSACTIONS
CREATE TABLE transactions (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id) ON DELETE CASCADE,
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

-- CATEGORY MAPPINGS
CREATE TABLE category_mappings (
  id SERIAL PRIMARY KEY,
  plaid_category VARCHAR(255) NOT NULL,
  tax_category VARCHAR(255) NOT NULL,
  deductible BOOLEAN DEFAULT TRUE,
  vat_applicable BOOLEAN DEFAULT TRUE,
  notes TEXT
);

-- TRANSACTION OVERRIDES
CREATE TABLE transaction_overrides (
  id SERIAL PRIMARY KEY,
  transaction_id INT REFERENCES transactions(id) ON DELETE CASCADE,
  user_id INT REFERENCES users(id) ON DELETE CASCADE,
  new_tax_category VARCHAR(255),
  override_type VARCHAR(50), -- e.g. manual, llm_suggested
  reason TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TAX SUMMARIES
CREATE TABLE tax_summaries (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id) ON DELETE CASCADE,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  total_income NUMERIC(12,2),
  total_expenses NUMERIC(12,2),
  vat_due NUMERIC(12,2),
  vat_reclaimable NUMERIC(12,2),
  net_profit NUMERIC(12,2),
  generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CONVERSATION LOGS
CREATE TABLE conversation_logs (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id) ON DELETE CASCADE,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  input_text TEXT NOT NULL,
  llm_response JSONB NOT NULL,
  task_type VARCHAR(100),
  source_model VARCHAR(100),
  session_id VARCHAR(255)
);

-- SCENARIO LOGS
CREATE TABLE scenario_logs (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id) ON DELETE CASCADE,
  prompt TEXT NOT NULL,
  response JSONB NOT NULL,
  context JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FEEDBACK LOGS
CREATE TABLE feedback_logs (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id) ON DELETE CASCADE,
  feedback TEXT NOT NULL,
  task_type VARCHAR(100) DEFAULT 'general',
  source_model VARCHAR(100) DEFAULT 'user',
  session_id VARCHAR(255),
  conversation_id INT REFERENCES conversation_logs(id) ON DELETE SET NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SESSION MANAGEMENT (OPTIONAL)
CREATE TABLE user_sessions (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id) ON DELETE CASCADE,
  device_info TEXT,
  ip_address TEXT,
  refresh_token VARCHAR(255) UNIQUE,
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);