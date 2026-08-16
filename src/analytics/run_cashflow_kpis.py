import sqlite3
import csv
from pathlib import Path

from cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    cfo_quality_label,
    capex_intensity,
    capex_intensity_label,
    fcf_conversion_rate,
    capital_allocation_pattern,
    sign_of,
)


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "capital_allocation.csv"


# ============================================================
# DATABASE CONNECTION
# ============================================================

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()


print("=" * 70)
print("SPRINT 2 - DAY 11")
print("CASH FLOW KPIs & CAPITAL ALLOCATION")
print("=" * 70)


# ============================================================
# CHECK COLUMNS
# ============================================================

cf_columns = [
    row[1]
    for row in cursor.execute(
        "PRAGMA table_info(cashflow)"
    )
]

pl_columns = [
    row[1]
    for row in cursor.execute(
        "PRAGMA table_info(profitandloss)"
    )
]


print("\nCash Flow columns:")
print(cf_columns)

print("\nP&L columns:")
print(pl_columns)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_cf = [
    "company_id",
    "year",
    "operating_cash_flow",
    "investing_cash_flow",
    "financing_cash_flow",
]

required_pl = [
    "company_id",
    "year",
    "sales",
    "operating_profit",
    "net_profit",
]


missing_cf = [
    column
    for column in required_cf
    if column not in cf_columns
]

missing_pl = [
    column
    for column in required_pl
    if column not in pl_columns
]


if missing_cf:

    print("\nERROR: Missing Cash Flow columns:")
    print(missing_cf)

    connection.close()

    raise SystemExit(1)


if missing_pl:

    print("\nERROR: Missing P&L columns:")
    print(missing_pl)

    connection.close()

    raise SystemExit(1)


# ============================================================
# GET DATA
# ============================================================

query = """
SELECT
    c.company_id,
    c.year,

    c.operating_cash_flow,
    c.investing_cash_flow,
    c.financing_cash_flow,

    p.sales,
    p.operating_profit,
    p.net_profit

FROM cashflow c

LEFT JOIN profitandloss p
    ON c.company_id = p.company_id
    AND c.year = p.year

ORDER BY
    c.company_id,
    c.year
"""


rows = cursor.execute(query).fetchall()


print()
print("Rows found:", len(rows))


# ============================================================
# CREATE CSV
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "company_id",
        "year",
        "cfo_sign",
        "cfi_sign",
        "cff_sign",
        "pattern_label",
    ])


    # ========================================================
    # PROCESS DATA
    # ========================================================

    for row in rows:

        (
            company_id,
            year,
            cfo,
            cfi,
            cff,
            sales,
            operating_profit,
            pat,
        ) = row


        # ----------------------------------------------------
        # FREE CASH FLOW
        # ----------------------------------------------------

        fcf = free_cash_flow(
            cfo,
            cfi
        )


        # ----------------------------------------------------
        # CFO QUALITY
        # ----------------------------------------------------

        quality_score = cfo_quality_score(
            cfo,
            pat
        )

        quality_label = cfo_quality_label(
            quality_score
        )


        # ----------------------------------------------------
        # CAPEX INTENSITY
        # ----------------------------------------------------

        capex = capex_intensity(
            cfi,
            sales
        )

        capex_label = capex_intensity_label(
            capex
        )


        # ----------------------------------------------------
        # FCF CONVERSION
        # ----------------------------------------------------

        conversion = fcf_conversion_rate(
            fcf,
            operating_profit
        )


        # ----------------------------------------------------
        # CAPITAL ALLOCATION PATTERN
        # ----------------------------------------------------

        pattern_label = capital_allocation_pattern(
            cfo,
            cfi,
            cff,
            quality_score
        )


        # ----------------------------------------------------
        # WRITE CSV
        # ----------------------------------------------------

        writer.writerow([
            company_id,
            year,
            sign_of(cfo),
            sign_of(cfi),
            sign_of(cff),
            pattern_label,
        ])


# ============================================================
# CLOSE DATABASE
# ============================================================

connection.close()


print()
print("=" * 70)
print("DAY 11 COMPLETED")
print("=" * 70)

print()
print("Capital allocation file:")
print(OUTPUT_FILE)

print()
print("Rows written:")
print(len(rows))