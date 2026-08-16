import sqlite3
from pathlib import Path

from ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
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
print("SPRINT 2 - DAY 08")
print("PROFITABILITY RATIO ENGINE")
print("=" * 70)


# ============================================================
# READ AVAILABLE COLUMNS
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


print("\nP&L columns:")
print(pl_columns)

print("\nBalance Sheet columns:")
print(bs_columns)


# ============================================================
# REQUIRED COLUMN CHECK
# ============================================================

required_pl = [
    "company_id",
    "year",
    "sales",
    "operating_profit",
    "net_profit",
]

required_bs = [
    "company_id",
    "year",
    "equity_capital",
    "reserves",
    "borrowings",
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
# CALCULATE RATIOS
# ============================================================

query = """
SELECT
    p.company_id,
    p.year,

    p.sales,
    p.operating_profit,
    p.net_profit,

    b.equity_capital,
    b.reserves,
    b.borrowings,
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


print("\n")
print("=" * 70)
print("PROFITABILITY RATIO RESULTS")
print("=" * 70)


for row in rows:

    (
        company_id,
        year,
        sales,
        operating_profit,
        net_profit,
        equity_capital,
        reserves,
        borrowings,
        total_assets,
    ) = row


    # --------------------------------------------------------
    # NET PROFIT MARGIN
    # --------------------------------------------------------

    npm = net_profit_margin(
        net_profit,
        sales
    )


    # --------------------------------------------------------
    # OPERATING PROFIT MARGIN
    # --------------------------------------------------------

    opm = operating_profit_margin(
        operating_profit,
        sales
    )


    # --------------------------------------------------------
    # ROE
    # --------------------------------------------------------

    roe = return_on_equity(
        net_profit,
        equity_capital,
        reserves
    )


    # --------------------------------------------------------
    # ROCE
    # --------------------------------------------------------

    roce = return_on_capital_employed(
        operating_profit,
        equity_capital,
        reserves,
        borrowings
    )


    # --------------------------------------------------------
    # ROA
    # --------------------------------------------------------

    roa = return_on_assets(
        net_profit,
        total_assets
    )


    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    print()

    print(
        f"Company ID        : {company_id}"
    )

    print(
        f"Year              : {year}"
    )

    print(
        f"Net Profit Margin : "
        f"{npm:.2f}%"
        if npm is not None
        else "Net Profit Margin : None"
    )

    print(
        f"Operating Margin  : "
        f"{opm:.2f}%"
        if opm is not None
        else "Operating Margin  : None"
    )

    print(
        f"ROE               : "
        f"{roe:.2f}%"
        if roe is not None
        else "ROE               : None"
    )

    print(
        f"ROCE              : "
        f"{roce:.2f}%"
        if roce is not None
        else "ROCE              : None"
    )

    print(
        f"ROA               : "
        f"{roa:.2f}%"
        if roa is not None
        else "ROA               : None"
    )


# ============================================================
# CLOSE
# ============================================================

connection.close()


print()
print("=" * 70)
print("DAY 08 PROFITABILITY RATIO CALCULATION COMPLETED")
print("=" * 70)