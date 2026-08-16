import sqlite3
from pathlib import Path

from ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity,
    asset_turnover,
)

from cashflow_kpis import (
    free_cash_flow,
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "nifty100.db"


# ============================================================
# DATABASE
# ============================================================

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

print("=" * 70)
print("SPRINT 2 - DAY 12")
print("POPULATE FINANCIAL_RATIOS")
print("=" * 70)


# ============================================================
# CHECK TABLE
# ============================================================

tables = [
    row[0]
    for row in cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
]

if "financial_ratios" not in tables:
    print("\nERROR: financial_ratios table does not exist.")
    connection.close()
    raise SystemExit(1)


# ============================================================
# SOURCE COLUMNS
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

cf_columns = [
    row[1]
    for row in cursor.execute(
        "PRAGMA table_info(cashflow)"
    )
]


print("\nP&L columns:")
print(pl_columns)

print("\nBalance Sheet columns:")
print(bs_columns)

print("\nCash Flow columns:")
print(cf_columns)


# ============================================================
# REQUIRED SOURCE COLUMNS
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
    "assets",
    "equity",
    "debt",
]

required_cf = [
    "company_id",
    "year",
    "operating_cash_flow",
    "investing_cash_flow",
]


missing_pl = [
    c for c in required_pl
    if c not in pl_columns
]

missing_bs = [
    c for c in required_bs
    if c not in bs_columns
]

missing_cf = [
    c for c in required_cf
    if c not in cf_columns
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


if missing_cf:
    print("\nERROR: Missing Cash Flow columns:")
    print(missing_cf)
    connection.close()
    raise SystemExit(1)


# ============================================================
# ADD KPI COLUMNS IF REQUIRED
# ============================================================

ratio_columns = [
    row[1]
    for row in cursor.execute(
        "PRAGMA table_info(financial_ratios)"
    )
]


required_ratio_columns = {
    "net_profit_margin_pct": "REAL",
    "operating_profit_margin_pct": "REAL",
    "return_on_equity_pct": "REAL",
    "return_on_capital_employed_pct": "REAL",
    "return_on_assets_pct": "REAL",
    "debt_to_equity": "REAL",
    "asset_turnover": "REAL",
    "free_cash_flow_cr": "REAL",
    "total_debt_cr": "REAL",
    "cash_from_operations_cr": "REAL",
}


for column, data_type in required_ratio_columns.items():

    if column not in ratio_columns:

        print(
            f"Adding financial_ratios column: {column}"
        )

        cursor.execute(
            f"""
            ALTER TABLE financial_ratios
            ADD COLUMN {column} {data_type}
            """
        )


connection.commit()


# ============================================================
# GET SOURCE DATA
# ============================================================

query = """
SELECT
    p.company_id,
    p.year,

    p.sales,
    p.operating_profit,
    p.net_profit,

    b.assets,
    b.equity,
    b.debt,

    c.operating_cash_flow,
    c.investing_cash_flow

FROM profitandloss p

LEFT JOIN balancesheet b
    ON p.company_id = b.company_id
    AND p.year = b.year

LEFT JOIN cashflow c
    ON p.company_id = c.company_id
    AND p.year = c.year

ORDER BY
    p.company_id,
    p.year
"""


rows = cursor.execute(query).fetchall()

print()
print("Source rows:", len(rows))


# ============================================================
# PROCESS
# ============================================================

updated = 0


for row in rows:

    (
        company_id,
        year,

        sales,
        operating_profit,
        net_profit,

        assets,
        equity,
        debt,

        operating_cash_flow,
        investing_cash_flow,

    ) = row


    # --------------------------------------------------------
    # SAFE DEFAULTS
    # --------------------------------------------------------

    equity = equity if equity is not None else 0
    debt = debt if debt is not None else 0


    # --------------------------------------------------------
    # PROFITABILITY
    # --------------------------------------------------------

    npm = net_profit_margin(
        net_profit,
        sales
    )

    opm = operating_profit_margin(
        operating_profit,
        sales
    )

    roe = return_on_equity(
        net_profit,
        equity,
        0
    )

    roce = return_on_capital_employed(
        operating_profit,
        equity,
        0,
        debt
    )

    roa = return_on_assets(
        net_profit,
        assets
    )


    # --------------------------------------------------------
    # LEVERAGE
    # --------------------------------------------------------

    de = debt_to_equity(
        debt,
        equity,
        0
    )


    # --------------------------------------------------------
    # ASSET TURNOVER
    # --------------------------------------------------------

    turnover = asset_turnover(
        sales,
        assets
    )


    # --------------------------------------------------------
    # FREE CASH FLOW
    # --------------------------------------------------------

    fcf = free_cash_flow(
        operating_cash_flow,
        investing_cash_flow
    )


    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    cursor.execute(
        """
        UPDATE financial_ratios

        SET
            net_profit_margin_pct = ?,
            operating_profit_margin_pct = ?,
            return_on_equity_pct = ?,
            return_on_capital_employed_pct = ?,
            return_on_assets_pct = ?,
            debt_to_equity = ?,
            asset_turnover = ?,
            free_cash_flow_cr = ?,
            total_debt_cr = ?,
            cash_from_operations_cr = ?

        WHERE
            company_id = ?
            AND year = ?
        """,

        (
            npm,
            opm,
            roe,
            roce,
            roa,
            de,
            turnover,
            fcf,
            debt,
            operating_cash_flow,

            company_id,
            year,
        )
    )

    if cursor.rowcount > 0:
        updated += cursor.rowcount


# ============================================================
# COMMIT
# ============================================================

connection.commit()


# ============================================================
# VERIFY
# ============================================================

count = cursor.execute(
    "SELECT COUNT(*) FROM financial_ratios"
).fetchone()[0]


print()
print("=" * 70)
print("DAY 12 INITIAL POPULATION")
print("=" * 70)

print("Source rows       :", len(rows))
print("Rows updated      :", updated)
print("financial_ratios  :", count)


# ============================================================
# CLOSE
# ============================================================

connection.close()

print()
print("Day 12 initial ratio population completed.")