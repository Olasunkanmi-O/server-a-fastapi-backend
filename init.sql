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
    user_id INTEGER REFERENCES users(id),
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
    user_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    input_text TEXT NOT NULL,
    llm_response JSONB NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    source_model VARCHAR(100) NOT NULL,
    session_id VARCHAR(255) NOT NULL
);


-- Feedback entries table
CREATE TABLE IF NOT EXISTS feedback_entries (
    id SERIAL PRIMARY KEY,
    conversation_id INT REFERENCES conversation_logs(id) ON DELETE CASCADE,
    user_id VARCHAR(255),
    rating INT CHECK (rating BETWEEN 1 AND 5),
    correction TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversation_feedback (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    conversation_id INT NOT NULL REFERENCES conversation_logs(id),
    feedback_text TEXT NOT NULL,
    rating INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
