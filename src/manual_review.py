import sqlite3
from pathlib import Path
import pandas as pd


# ============================================================
# DAY 6 - DATA QUALITY MANUAL REVIEW
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DB_PATH = PROJECT_ROOT / "nifty100.db"
OUTPUT_FOLDER = PROJECT_ROOT / "output"

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONNECT TO DATABASE
# ============================================================

if not DB_PATH.exists():
    print("ERROR: nifty100.db was not found.")
    print(f"Expected: {DB_PATH}")
    raise SystemExit(1)

connection = sqlite3.connect(DB_PATH)

# Enable foreign keys
connection.execute(
    "PRAGMA foreign_keys = ON"
)


print()
print("=" * 60)
print("DAY 6 - DATA QUALITY MANUAL REVIEW")
print("=" * 60)


# ============================================================
# 1. COMPANY REVIEW
# ============================================================

print()
print("=" * 60)
print("1. COMPANIES")
print("=" * 60)

companies = pd.read_sql_query(
    """
    SELECT
        company_id,
        company_name,
        ticker,
        sector
    FROM companies
    ORDER BY company_id
    """,
    connection
)

print(
    companies.to_string(index=False)
)


# ============================================================
# 2. YEAR COVERAGE
# ============================================================

print()
print("=" * 60)
print("2. YEAR COVERAGE")
print("=" * 60)

coverage = pd.read_sql_query(
    """
    SELECT
        c.company_id,
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
    ORDER BY c.company_id
    """,
    connection
)

print(
    coverage.to_string(index=False)
)

coverage.to_csv(
    OUTPUT_FOLDER / "year_coverage_review.csv",
    index=False
)


# ============================================================
# 3. COMPANIES WITH LESS THAN 5 YEARS
# ============================================================

print()
print("=" * 60)
print("3. COMPANIES WITH LESS THAN 5 YEARS")
print("=" * 60)

less_than_5 = coverage[
    coverage["years_available"] < 5
]

if less_than_5.empty:
    print("None found.")
else:
    print(
        less_than_5.to_string(index=False)
    )


# ============================================================
# 4. PROFIT AND LOSS REVIEW
# ============================================================

print()
print("=" * 60)
print("4. PROFIT AND LOSS REVIEW")
print("=" * 60)

pnl = pd.read_sql_query(
    """
    SELECT
        company_id,
        year,
        sales,
        operating_profit,
        net_profit,
        eps
    FROM profitandloss
    ORDER BY company_id, year
    """,
    connection
)

print(
    pnl.to_string(index=False)
)


# ============================================================
# 5. SALES CHECK
# ============================================================

print()
print("=" * 60)
print("5. SALES CHECK")
print("=" * 60)

invalid_sales = pnl[
    pnl["sales"].notna() &
    (pnl["sales"] <= 0)
]

if invalid_sales.empty:
    print("No invalid sales values found.")
else:
    print("Invalid sales values found:")
    print(
        invalid_sales.to_string(index=False)
    )


# ============================================================
# 6. BALANCE SHEET REVIEW
# ============================================================

print()
print("=" * 60)
print("6. BALANCE SHEET REVIEW")
print("=" * 60)

balance = pd.read_sql_query(
    """
    SELECT
        company_id,
        year,
        assets,
        liabilities,
        equity
    FROM balancesheet
    ORDER BY company_id, year
    """,
    connection
)

if balance.empty:

    print("No balance-sheet records found.")

else:

    balance["calculated_total"] = (
        balance["liabilities"].fillna(0)
        + balance["equity"].fillna(0)
    )

    balance["difference"] = (
        balance["assets"] -
        balance["calculated_total"]
    )

    print(
        balance.to_string(index=False)
    )


# ============================================================
# 7. DUPLICATE CHECK
# ============================================================

print()
print("=" * 60)
print("7. DUPLICATE CHECK")
print("=" * 60)

duplicate_check = pd.read_sql_query(
    """
    SELECT
        company_id,
        year,
        COUNT(*) AS record_count
    FROM profitandloss
    GROUP BY company_id, year
    HAVING COUNT(*) > 1
    """,
    connection
)

if duplicate_check.empty:

    print(
        "No duplicate company-year records found."
    )

else:

    print("Duplicates found:")
    print(
        duplicate_check.to_string(index=False)
    )


# ============================================================
# 8. FOREIGN KEY CHECK
# ============================================================

print()
print("=" * 60)
print("8. FOREIGN KEY CHECK")
print("=" * 60)

foreign_key_errors = connection.execute(
    "PRAGMA foreign_key_check"
).fetchall()

if not foreign_key_errors:

    print(
        "Foreign key check passed: 0 errors."
    )

else:

    print(
        f"Foreign key errors: {len(foreign_key_errors)}"
    )

    for error in foreign_key_errors:
        print(error)


# ============================================================
# 9. TABLE COUNTS
# ============================================================

print()
print("=" * 60)
print("9. FINAL TABLE COUNTS")
print("=" * 60)

tables = [
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "prosandcons",
    "sectors",
    "stock_prices",
    "financial_ratios",
    "peer_groups"
]

results = []

for table in tables:

    try:

        count = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        print(
            f"{table}: {count}"
        )

        results.append({
            "table": table,
            "row_count": count
        })

    except sqlite3.Error as error:

        print(
            f"{table}: ERROR - {error}"
        )


# Save table counts

pd.DataFrame(results).to_csv(
    OUTPUT_FOLDER / "table_counts_review.csv",
    index=False
)


# ============================================================
# 10. CLOSE DATABASE
# ============================================================

connection.close()


print()
print("=" * 60)
print("DAY 6 MANUAL REVIEW COMPLETED")
print("=" * 60)

print()
print("Reports created:")
print("- output/year_coverage_review.csv")
print("- output/table_counts_review.csv")
print()