-- ============================================================
-- NIFTY100 ETL PROJECT
-- SPRINT 1 - DAY 04
-- SQLITE DATABASE SCHEMA
-- ============================================================

-- Enable foreign-key enforcement
PRAGMA foreign_keys = ON;


-- ============================================================
-- 1. COMPANIES
-- ============================================================

CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY,
    company_name TEXT NOT NULL,
    ticker TEXT NOT NULL UNIQUE,
    sector TEXT,
    industry TEXT,
    exchange TEXT,
    website TEXT
);


-- ============================================================
-- 2. PROFIT AND LOSS
-- Primary Key: (company_id, year)
-- ============================================================

CREATE TABLE IF NOT EXISTS profitandloss (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,

    sales REAL,
    operating_profit REAL,
    operating_margin REAL,

    profit_before_tax REAL,
    tax REAL,
    net_profit REAL,

    eps REAL,
    dividend REAL,

    PRIMARY KEY (company_id, year),

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


-- ============================================================
-- 3. BALANCE SHEET
-- Primary Key: (company_id, year)
-- ============================================================

CREATE TABLE IF NOT EXISTS balancesheet (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,

    assets REAL,
    liabilities REAL,
    equity REAL,

    cash REAL,
    debt REAL,

    current_assets REAL,
    current_liabilities REAL,

    net_worth REAL,

    PRIMARY KEY (company_id, year),

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


-- ============================================================
-- 4. CASH FLOW
-- Primary Key: (company_id, year)
-- ============================================================

CREATE TABLE IF NOT EXISTS cashflow (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,

    operating_cash_flow REAL,
    investing_cash_flow REAL,
    financing_cash_flow REAL,

    free_cash_flow REAL,

    capital_expenditure REAL,

    PRIMARY KEY (company_id, year),

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


-- ============================================================
-- 5. ANALYSIS
-- Primary Key: (company_id, year)
-- ============================================================

CREATE TABLE IF NOT EXISTS analysis (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,

    revenue_growth REAL,
    profit_growth REAL,

    operating_margin REAL,

    return_on_equity REAL,
    return_on_capital REAL,
    return_on_assets REAL,

    earnings_growth REAL,

    PRIMARY KEY (company_id, year),

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


-- ============================================================
-- 6. DOCUMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS documents (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,

    company_id INTEGER NOT NULL,

    document_type TEXT,
    document_title TEXT,
    document_url TEXT,
    document_date TEXT,

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


-- ============================================================
-- 7. PROS AND CONS
-- ============================================================

CREATE TABLE IF NOT EXISTS prosandcons (
    company_id INTEGER PRIMARY KEY,

    pros TEXT,
    cons TEXT,

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


-- ============================================================
-- 8. SECTORS
-- ============================================================

CREATE TABLE IF NOT EXISTS sectors (
    sector_id INTEGER PRIMARY KEY AUTOINCREMENT,

    sector_name TEXT NOT NULL UNIQUE,
    description TEXT
);


-- ============================================================
-- 9. STOCK PRICES
-- Primary Key: (company_id, date)
-- ============================================================

CREATE TABLE IF NOT EXISTS stock_prices (
    company_id INTEGER NOT NULL,
    date TEXT NOT NULL,

    open REAL,
    high REAL,
    low REAL,
    close REAL,

    adjusted_close REAL,

    volume INTEGER,

    PRIMARY KEY (company_id, date),

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


-- ============================================================
-- 10. FINANCIAL RATIOS
-- Primary Key: (company_id, year)
-- ============================================================

CREATE TABLE IF NOT EXISTS financial_ratios (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,

    pe_ratio REAL,
    pb_ratio REAL,

    debt_to_equity REAL,
    current_ratio REAL,
    quick_ratio REAL,

    roe REAL,
    roa REAL,

    dividend_yield REAL,

    eps REAL,

    PRIMARY KEY (company_id, year),

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


-- ============================================================
-- 11. PEER GROUPS
-- Included because the project specification explicitly
-- mentions peer_groups.
-- ============================================================

CREATE TABLE IF NOT EXISTS peer_groups (
    peer_group_id INTEGER PRIMARY KEY AUTOINCREMENT,

    company_id INTEGER NOT NULL,

    peer_company_id INTEGER NOT NULL,

    similarity_score REAL,

    peer_type TEXT,

    created_at TEXT,

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (peer_company_id)
        REFERENCES companies(company_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    UNIQUE (
        company_id,
        peer_company_id
    )
);


-- ============================================================
-- INDEXES
-- These improve query performance.
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_companies_ticker
ON companies(ticker);


CREATE INDEX IF NOT EXISTS idx_companies_sector
ON companies(sector);


CREATE INDEX IF NOT EXISTS idx_pnl_company
ON profitandloss(company_id);


CREATE INDEX IF NOT EXISTS idx_pnl_year
ON profitandloss(year);


CREATE INDEX IF NOT EXISTS idx_bs_company
ON balancesheet(company_id);


CREATE INDEX IF NOT EXISTS idx_bs_year
ON balancesheet(year);


CREATE INDEX IF NOT EXISTS idx_cf_company
ON cashflow(company_id);


CREATE INDEX IF NOT EXISTS idx_cf_year
ON cashflow(year);


CREATE INDEX IF NOT EXISTS idx_analysis_company
ON analysis(company_id);


CREATE INDEX IF NOT EXISTS idx_analysis_year
ON analysis(year);


CREATE INDEX IF NOT EXISTS idx_documents_company
ON documents(company_id);


CREATE INDEX IF NOT EXISTS idx_stock_prices_company
ON stock_prices(company_id);


CREATE INDEX IF NOT EXISTS idx_stock_prices_date
ON stock_prices(date);


CREATE INDEX IF NOT EXISTS idx_ratios_company
ON financial_ratios(company_id);


CREATE INDEX IF NOT EXISTS idx_ratios_year
ON financial_ratios(year);


CREATE INDEX IF NOT EXISTS idx_peer_groups_company
ON peer_groups(company_id);


CREATE INDEX IF NOT EXISTS idx_peer_groups_peer
ON peer_groups(peer_company_id);


-- ============================================================
-- SCHEMA VALIDATION
-- ============================================================

-- Foreign keys remain enabled for this connection.
PRAGMA foreign_keys = ON;