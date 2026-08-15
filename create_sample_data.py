from pathlib import Path
import pandas as pd

# Location of raw Excel files
RAW = Path("data/raw")
RAW.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 1. Companies
# --------------------------------------------------

companies = pd.DataFrame({
    "company_id": [1, 2, 3, 4, 5],
    "company_name": [
        "Reliance Industries",
        "Tata Consultancy Services",
        "Infosys",
        "HDFC Bank",
        "ICICI Bank"
    ],
    "ticker": [
        "reliance",
        " tcs ",
        "infy",
        "hdfcbank",
        "icicibank"
    ],
    "sector": [
        "Energy",
        "IT",
        "IT",
        "Banking",
        "Banking"
    ]
})

companies.to_excel(RAW / "companies.xlsx", index=False)


# --------------------------------------------------
# 2. Profit and Loss
# --------------------------------------------------

profitandloss = pd.DataFrame({
    "company_id": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
    "year": [
        "2023", " 2024 ",
        "2023", "2024",
        "2023", "2024",
        "2023", "2024",
        "2023", "2024"
    ],
    "sales": [
        100000, 110000,
        90000, 95000,
        70000, 76000,
        85000, 92000,
        65000, 72000
    ],
    "operating_profit": [
        25000, 27000,
        22000, 23000,
        18000, 20000,
        30000, 33000,
        24000, 27000
    ],
    "net_profit": [
        18000, 20000,
        17000, 17500,
        14000, 15000,
        22000, 25000,
        18000, 21000
    ]
})

profitandloss.to_excel(
    RAW / "profitandloss.xlsx",
    index=False
)


# --------------------------------------------------
# 3. Balance Sheet
# --------------------------------------------------

balancesheet = pd.DataFrame({
    "company_id": [1, 2, 3, 4, 5],
    "year": [2024, 2024, 2024, 2024, 2024],
    "assets": [200000, 180000, 140000, 250000, 210000],
    "liabilities": [120000, 90000, 70000, 220000, 180000],
    "equity": [80000, 90000, 70000, 30000, 30000]
})

balancesheet.to_excel(
    RAW / "balancesheet.xlsx",
    index=False
)


# --------------------------------------------------
# 4. Cash Flow
# --------------------------------------------------

cashflow = pd.DataFrame({
    "company_id": [1, 2, 3, 4, 5],
    "year": [2024, 2024, 2024, 2024, 2024],
    "operating_cf": [25000, 22000, 18000, 30000, 25000],
    "investing_cf": [-5000, -3000, -2000, -7000, -4000],
    "financing_cf": [-7000, -4000, -3000, -15000, -12000]
})

cashflow.to_excel(
    RAW / "cashflow.xlsx",
    index=False
)


# --------------------------------------------------
# 5. Analysis
# --------------------------------------------------

analysis = pd.DataFrame({
    "company_id": [1, 2, 3, 4, 5],
    "year": [2024] * 5,
    "eps": [120, 110, 85, 65, 70],
    "roe": [15.2, 48.5, 29.1, 17.4, 18.2],
    "roce": [13.5, 42.1, 25.6, 12.8, 14.5]
})

analysis.to_excel(
    RAW / "analysis.xlsx",
    index=False
)


# --------------------------------------------------
# 6. Documents
# --------------------------------------------------

documents = pd.DataFrame({
    "company_id": [1, 2, 3, 4, 5],
    "document_type": [
        "Annual Report",
        "Annual Report",
        "Annual Report",
        "Annual Report",
        "Annual Report"
    ],
    "document_url": [
        "https://example.com/reliance",
        "https://example.com/tcs",
        "https://example.com/infosys",
        "https://example.com/hdfc",
        "https://example.com/icici"
    ]
})

documents.to_excel(
    RAW / "documents.xlsx",
    index=False
)


# --------------------------------------------------
# 7. Pros and Cons
# --------------------------------------------------

prosandcons = pd.DataFrame({
    "company_id": [1, 2, 3, 4, 5],
    "pros": [
        "Strong diversification",
        "Strong IT services",
        "Strong global presence",
        "Large customer base",
        "Strong retail banking"
    ],
    "cons": [
        "Capital intensive",
        "Currency exposure",
        "High competition",
        "Credit risk",
        "Economic sensitivity"
    ]
})

prosandcons.to_excel(
    RAW / "prosandcons.xlsx",
    index=False
)


# --------------------------------------------------
# 8. Sectors
# --------------------------------------------------

sectors = pd.DataFrame({
    "company_id": [1, 2, 3, 4, 5],
    "sector": [
        "Energy",
        "IT",
        "IT",
        "Banking",
        "Banking"
    ]
})

sectors.to_excel(
    RAW / "sectors.xlsx",
    index=False
)


# --------------------------------------------------
# 9. Stock Prices
# --------------------------------------------------

stock_prices = pd.DataFrame({
    "company_id": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
    "date": [
        "2024-01-02",
        "2024-01-03",
        "2024-01-02",
        "2024-01-03",
        "2024-01-02",
        "2024-01-03",
        "2024-01-02",
        "2024-01-03",
        "2024-01-02",
        "2024-01-03"
    ],
    "close_price": [
        2500, 2525,
        3800, 3820,
        1600, 1620,
        1500, 1520,
        1050, 1070
    ]
})

stock_prices.to_excel(
    RAW / "stock_prices.xlsx",
    index=False
)


# --------------------------------------------------
# 10. Financial Ratios
# --------------------------------------------------

financial_ratios = pd.DataFrame({
    "company_id": [1, 2, 3, 4, 5],
    "year": [2024] * 5,
    "pe_ratio": [25.5, 30.2, 28.1, 20.4, 18.7],
    "debt_equity": [0.45, 0.12, 0.08, 6.5, 5.8],
    "roe": [15.2, 48.5, 29.1, 17.4, 18.2]
})

financial_ratios.to_excel(
    RAW / "financial_ratios.xlsx",
    index=False
)


# --------------------------------------------------
# 11. Peer Groups
# --------------------------------------------------

peer_groups = pd.DataFrame({
    "company_id": [1, 2, 3, 4, 5],
    "peer_company": [
        "ONGC",
        "Infosys",
        "TCS",
        "ICICI Bank",
        "HDFC Bank"
    ]
})

peer_groups.to_excel(
    RAW / "peer_groups.xlsx",
    index=False
)


# --------------------------------------------------
# 12. Dividends
# --------------------------------------------------

dividends = pd.DataFrame({
    "company_id": [1, 2, 3, 4, 5],
    "year": [2024] * 5,
    "dividend_per_share": [10, 50, 28, 20, 18]
})

dividends.to_excel(
    RAW / "dividends.xlsx",
    index=False
)


print("======================================")
print("12 sample Excel files created!")
print("======================================")

for file in sorted(RAW.glob("*.xlsx")):
    print(file)