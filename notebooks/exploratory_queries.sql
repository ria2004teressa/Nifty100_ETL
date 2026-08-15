-- ============================================================
-- NIFTY100 ETL - SPRINT 1
-- DAY 7 - EXPLORATORY QUERIES
-- ============================================================

PRAGMA foreign_keys = ON;


-- ============================================================
-- QUERY 1
-- Total number of companies
-- ============================================================

SELECT COUNT(*) AS total_companies
FROM companies;


-- ============================================================
-- QUERY 2
-- List all companies
-- ============================================================

SELECT
    company_id,
    company_name,
    ticker,
    sector
FROM companies
ORDER BY company_name;


-- ============================================================
-- QUERY 3
-- Companies by sector
-- ============================================================

SELECT
    sector,
    COUNT(*) AS company_count
FROM companies
GROUP BY sector
ORDER BY company_count DESC;


-- ============================================================
-- QUERY 4
-- Year coverage for each company
-- ============================================================

SELECT
    c.company_name,
    COUNT(DISTINCT p.year) AS years_available,
    MIN(p.year) AS first_year,
    MAX(p.year) AS last_year
FROM companies c
LEFT JOIN profitandloss p
    ON c.company_id = p.company_id
GROUP BY
    c.company_id,
    c.company_name
ORDER BY
    years_available DESC;


-- ============================================================
-- QUERY 5
-- Companies with less than 5 years of data
-- ============================================================

SELECT
    c.company_id,
    c.company_name,
    COUNT(DISTINCT p.year) AS years_available
FROM companies c
LEFT JOIN profitandloss p
    ON c.company_id = p.company_id
GROUP BY
    c.company_id,
    c.company_name
HAVING COUNT(DISTINCT p.year) < 5;


-- ============================================================
-- QUERY 6
-- Highest sales
-- ============================================================

SELECT
    c.company_name,
    p.year,
    p.sales
FROM profitandloss p
JOIN companies c
    ON p.company_id = c.company_id
WHERE p.sales IS NOT NULL
ORDER BY p.sales DESC
LIMIT 10;


-- ============================================================
-- QUERY 7
-- Highest net profit
-- ============================================================

SELECT
    c.company_name,
    p.year,
    p.net_profit
FROM profitandloss p
JOIN companies c
    ON p.company_id = c.company_id
WHERE p.net_profit IS NOT NULL
ORDER BY p.net_profit DESC
LIMIT 10;


-- ============================================================
-- QUERY 8
-- Operating margin by company
-- ============================================================

SELECT
    c.company_name,
    p.year,
    p.operating_margin
FROM profitandloss p
JOIN companies c
    ON p.company_id = c.company_id
WHERE p.operating_margin IS NOT NULL
ORDER BY p.operating_margin DESC;


-- ============================================================
-- QUERY 9
-- Balance sheet check
-- Assets should approximately equal
-- liabilities + equity
-- ============================================================

SELECT
    c.company_name,
    b.year,
    b.assets,
    b.liabilities,
    b.equity,
    (b.liabilities + b.equity) AS liabilities_plus_equity,
    (b.assets - (b.liabilities + b.equity)) AS difference
FROM balancesheet b
JOIN companies c
    ON b.company_id = c.company_id
ORDER BY
    ABS(
        b.assets -
        (b.liabilities + b.equity)
    ) DESC;


-- ============================================================
-- QUERY 10
-- Stock price summary
-- ============================================================

SELECT
    c.company_name,
    MIN(s.low) AS minimum_price,
    MAX(s.high) AS maximum_price,
    AVG(s.close) AS average_close,
    COUNT(*) AS trading_days
FROM stock_prices s
JOIN companies c
    ON s.company_id = c.company_id
GROUP BY
    c.company_id,
    c.company_name
ORDER BY
    average_close DESC;