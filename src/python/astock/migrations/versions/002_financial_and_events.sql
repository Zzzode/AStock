-- Add financial_statements table for cached structured financials.

CREATE TABLE IF NOT EXISTS financial_cache (
    code TEXT NOT NULL,
    period TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL,
    fetched_at DATETIME NOT NULL,
    PRIMARY KEY (code, period, metric_name)
);

CREATE INDEX IF NOT EXISTS idx_financial_cache_code
    ON financial_cache(code);

-- Add corporate_events table for news/announcement pipeline.

CREATE TABLE IF NOT EXISTS corporate_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    event_type TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    published_at DATETIME,
    severity TEXT NOT NULL DEFAULT 'medium',
    source TEXT,
    url TEXT,
    tags TEXT NOT NULL DEFAULT '[]',
    raw_data TEXT NOT NULL DEFAULT '{}',
    ingested_at DATETIME NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_corporate_events_code
    ON corporate_events(code);
CREATE INDEX IF NOT EXISTS idx_corporate_events_type
    ON corporate_events(event_type);
CREATE INDEX IF NOT EXISTS idx_corporate_events_published
    ON corporate_events(published_at);
