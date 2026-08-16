import sqlite3
from pathlib import Path

from ratios import (
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    interest_coverage_label,
    interest_coverage_warning,
    net_debt,
    asset_turnover,
)


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "nifty100.db"


# ============================================================
# CONNECT
# ============================================================

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

print("=" * 70)
print("SPRINT 2 - DAY 09")
print("LEVERAGE & EFFICIENCY RATIO ENGINE")
print("=" * 70)


# ============================================================
# CHECK DATABASE COLUMNS
# ============================================================

pl_columns = [
    row[1]
    for row in cursor.execute(
        "PRAGMA table_info(profitandloss)"
    )
]

bs_columns = [
    row[1]
    for row in cursor.execute(
        "PRAGMA table_info(balancesheet)"
    )
]

company_columns = [
    row[1]
    for row in cursor.execute(
        "PRAGMA table_info(companies)"
    )
]


print("\nP&L columns:")
print(pl_columns)

print("\nBalance Sheet columns:")
print(bs_columns)

print("\nCompany columns:")
print(company_columns)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_pl = [
    "company_id",
    "year",
    "sales",
    "operating_profit",
    "other_income",
    "interest",
]

required_bs = [
    "company_id",
    "year",
    "equity_capital",
    "reserves",
    "borrowings",
    "investments",
    "total_assets",
]


missing_pl = [
    column
    for column in required_pl
    if column not in pl_columns
]

missing_bs = [
    column
    for column in required_bs
    if column not in bs_columns
]


if missing_pl:
    print("\nERROR: Missing P&L columns:")
    print(missing_pl)
    connection.close()
    raise SystemExit(1)


if missing_bs:
    print("\nERROR: Missing Balance Sheet columns:")
    print(missing_bs)
    connection.close()
    raise SystemExit(1)


# ============================================================
# READ DATA
# ============================================================

query = """
SELECT
    p.company_id,
    p.year,

    p.sales,
    p.operating_profit,
    p.other_income,
    p.interest,

    b.equity_capital,
    b.reserves,
    b.borrowings,
    b.investments,
    b.total_assets

FROM profitandloss p

LEFT JOIN balancesheet b
    ON p.company_id = b.company_id
    AND p.year = b.year

ORDER BY
    p.company_id,
    p.year

LIMIT 20
"""


rows = cursor.execute(query).fetchall()


# ============================================================
# CALCULATE
# ============================================================

print()
print("=" * 70)
print("DAY 09 RESULTS")
print("=" * 70)


for row in rows:

    (
        company_id,
        year,
        sales,
        operating_profit,
        other_income,
        interest,
        equity_capital,
        reserves,
        borrowings,
        investments,
        total_assets,
    ) = row


    # --------------------------------------------------------
    # D/E
    # --------------------------------------------------------

    de = debt_to_equity(
        borrowings,
        equity_capital,
        reserves
    )


    # --------------------------------------------------------
    # HIGH LEVERAGE
    # --------------------------------------------------------

    # Sample sector because the actual sector field may differ.
    # We will connect the real sector column later.
    high_leverage = high_leverage_flag(
        de,
        "Technology"
    )


    # --------------------------------------------------------
    # ICR
    # --------------------------------------------------------

    icr = interest_coverage_ratio(
        operating_profit,
        other_income,
        interest
    )


    icr_label = interest_coverage_label(
        icr
    )


    icr_warning = interest_coverage_warning(
        icr
    )


    # --------------------------------------------------------
    # NET DEBT
    # --------------------------------------------------------

    net_debt_value = net_debt(
        borrowings,
        investments
    )


    # --------------------------------------------------------
    # ASSET TURNOVER
    # --------------------------------------------------------

    turnover = asset_turnover(
        sales,
        total_assets
    )


    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    print()

    print(f"Company ID       : {company_id}")
    print(f"Year             : {year}")

    print(
        f"D/E              : "
        f"{de:.2f}"
        if de is not None
        else "D/E              : None"
    )

    print(
        f"High Leverage    : {high_leverage}"
    )

    print(
        f"ICR              : "
        f"{icr:.2f}"
        if icr is not None
        else "ICR              : None"
    )

    print(
        f"ICR Label        : "
        f"{icr_label}"
    )

    print(
        f"ICR Warning      : "
        f"{icr_warning}"
    )

    print(
        f"Net Debt         : "
        f"{net_debt_value}"
    )

    print(
        f"Asset Turnover   : "
        f"{turnover:.2f}"
        if turnover is not None
        else "Asset Turnover   : None"
    )


# ============================================================
# CLOSE
# ============================================================

connection.close()


print()
print("=" * 70)
print("DAY 09 DATABASE CALCULATION COMPLETED")
print("=" * 70)