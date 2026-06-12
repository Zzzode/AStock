-- Baseline schema: captures the initial table structure.
-- This migration is safe to re-run (uses IF NOT EXISTS).

CREATE TABLE IF NOT EXISTS stocks (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    industry TEXT,
    list_date DATE
);

CREATE TABLE IF NOT EXISTS daily_quotes (
    code TEXT NOT NULL,
    date DATE NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    amount REAL NOT NULL,
    PRIMARY KEY (code, date)
);

CREATE INDEX IF NOT EXISTS idx_daily_quotes_date
    ON daily_quotes(date);

CREATE TABLE IF NOT EXISTS watch_items (
    code TEXT PRIMARY KEY,
    name TEXT,
    conditions TEXT NOT NULL DEFAULT '{}',
    alert_channels TEXT NOT NULL DEFAULT '["terminal"]',
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME
);

CREATE TABLE IF NOT EXISTS alert_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    signal_name TEXT NOT NULL,
    message TEXT NOT NULL,
    level INTEGER NOT NULL DEFAULT 3,
    triggered_at DATETIME NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    channels TEXT NOT NULL DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_alert_records_code
    ON alert_records(code);
CREATE INDEX IF NOT EXISTS idx_alert_records_triggered_at
    ON alert_records(triggered_at);
