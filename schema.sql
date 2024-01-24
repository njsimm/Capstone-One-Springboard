-- Schema Design for Capstone Project

-- Create User table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
);

-- Create Asset table
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    ticker TEXT UNIQUE NOT NULL,
    price DECIMAL(15,2) NOT NULL CHECK (price >= 0),
    market_cap DECIMAL(15,2) NOT NULL CHECK (market_cap >= 0),
);

-- Create ComparisonHistory table
CREATE TABLE comparisons_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    asset_id_1 INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    asset_1_price_at_comparison DECIMAL(15,2) NOT NULL,
    asset_1_market_cap_at_comparison DECIMAL(15,2) NOT NULL,
    asset_id_2 INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    asset_2_price_at_comparison DECIMAL(15,2) NOT NULL,
    asset_2_market_cap_at_comparison DECIMAL(15,2) NOT NULL,
    comparison_timestamp TIMESTAMPTZ NOT NULL,
    percent_difference DECIMAL(15,2) NOT NULL
);
