-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    business_name VARCHAR(255) NOT NULL,
    business_structure VARCHAR(50) NOT NULL,
    vat_enabled BOOLEAN NOT NULL,
    has_employees BOOLEAN NOT NULL,
    num_employees INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Plaid accounts table
CREATE TABLE IF NOT EXISTS user_plaid_accounts (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    item_id VARCHAR(255) UNIQUE NOT NULL,
    access_token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    plaid_transaction_id VARCHAR(255) UNIQUE,
    date DATE NOT NULL,
    description VARCHAR(255) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    category VARCHAR(255),
    tax_label VARCHAR(255),
    needs_review BOOLEAN DEFAULT FALSE,
    confidence NUMERIC(3,2) DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conversation logs table
CREATE TABLE IF NOT EXISTS conversation_logs (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    input_text TEXT NOT NULL,
    llm_response JSONB NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    source_model VARCHAR(100) NOT NULL,
    session_id VARCHAR(255) NOT NULL
);

-- Review logs table
CREATE TABLE IF NOT EXISTS review_logs (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    session_id VARCHAR(255),
    feedback TEXT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feedback logs table
CREATE TABLE IF NOT EXISTS feedback_logs (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    feedback TEXT NOT NULL,
    task_type VARCHAR(100) DEFAULT 'general',
    source_model VARCHAR(100) DEFAULT 'user',
    session_id VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);