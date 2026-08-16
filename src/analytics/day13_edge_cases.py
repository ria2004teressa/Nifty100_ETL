import sqlite3
from pathlib import Path
from datetime import datetime


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

LOG_FILE = OUTPUT_DIR / "ratio_edge_cases.log"


# ============================================================
# DATABASE
# ============================================================

conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()


# ============================================================
# START LOG
# ============================================================

with open(LOG_FILE, "w", encoding="utf-8") as log:

    log.write("=" * 70 + "\n")
    log.write("DAY 13 - RATIO EDGE CASE LOG\n")
    log.write("=" * 70 + "\n")
    log.write(
        f"Generated: {datetime.now()}\n\n"
    )


# ============================================================
# CHECK TABLES
# ============================================================

tables = [
    row[0]
    for row in cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
]


required_tables = [
    "financial_ratios",
    "companies",
]


for table in required_tables:

    if table not in tables:

        print(
            f"ERROR: Missing table: {table}"
        )

        conn.close()

        raise SystemExit(1)


# ============================================================
# CHECK COMPANIES COLUMNS
# ============================================================

company_columns = [
    row[1]
    for row in cursor.execute(
        "PRAGMA table_info(companies)"
    )
]


print("Companies columns:")
print(company_columns)


# ============================================================
# FIND SECTOR COLUMN
# ============================================================

sector_column = None


for candidate in [
    "broad_sector",
    "sector",
    "broadsector",
]:

    if candidate in company_columns:

        sector_column = candidate

        break


if sector_column is None:

    print(
        "\nWARNING: No sector column found."
    )

    print(
        "Financials carve-out cannot be applied yet."
    )


# ============================================================
# FINANCIALS COUNT
# ============================================================

financials_count = 0


if sector_column:

    financials_count = cursor.execute(
        f"""
        SELECT COUNT(*)

        FROM companies

        WHERE LOWER({sector_column})
        = 'financials'
        """
    ).fetchone()[0]


print(
    "\nFinancials companies:",
    financials_count
)


# ============================================================
# CREATE / CHECK HIGH LEVERAGE FLAG
# ============================================================

ratio_columns = [
    row[1]
    for row in cursor.execute(
        "PRAGMA table_info(financial_ratios)"
    )
]


if "high_leverage_flag" not in ratio_columns:

    cursor.execute(
        """
        ALTER TABLE financial_ratios

        ADD COLUMN high_leverage_flag INTEGER
        """
    )


if "financials_sector_flag" not in ratio_columns:

    cursor.execute(
        """
        ALTER TABLE financial_ratios

        ADD COLUMN financials_sector_flag INTEGER
        """
    )


conn.commit()


# ============================================================
# APPLY FINANCIALS CARVE-OUT
# ============================================================

if sector_column:

    cursor.execute(
        f"""
        UPDATE financial_ratios

        SET financials_sector_flag = 1

        WHERE company_id IN

        (
            SELECT company_id

            FROM companies

            WHERE LOWER({sector_column})
            = 'financials'
        )
        """
    )


    # Suppress high leverage warning for Financials

    cursor.execute(
        f"""
        UPDATE financial_ratios

        SET high_leverage_flag = 0

        WHERE company_id IN

        (
            SELECT company_id

            FROM companies

            WHERE LOWER({sector_column})
            = 'financials'
        )
        """
    )


    # Non-Financial companies:
    # D/E > 5 = high leverage

    cursor.execute(
        f"""
        UPDATE financial_ratios

        SET high_leverage_flag =

            CASE

                WHEN debt_to_equity > 5
                THEN 1

                ELSE 0

            END

        WHERE company_id NOT IN

        (
            SELECT company_id

            FROM companies

            WHERE LOWER({sector_column})
            = 'financials'
        )
        """
    )


conn.commit()


# ============================================================
# ROCE CROSS-CHECK
# ============================================================

if "roce_percentage" in company_columns:

    roce_rows = cursor.execute(
        f"""
        SELECT
            fr.company_id,
            fr.year,
            fr.return_on_capital_employed_pct,
            c.roce_percentage

        FROM financial_ratios fr

        JOIN companies c

            ON fr.company_id = c.company_id

        WHERE
            fr.return_on_capital_employed_pct
            IS NOT NULL

            AND c.roce_percentage
            IS NOT NULL
        """
    ).fetchall()


    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as log:

        for row in roce_rows:

            (
                company_id,
                year,
                calculated,
                source,
            ) = row


            if (
                calculated is None
                or source is None
            ):
                continue


            difference = abs(
                calculated - source
            )


            if difference > 5:

                log.write(
                    f"ROCE ANOMALY | "
                    f"company_id={company_id} | "
                    f"year={year} | "
                    f"calculated={calculated:.4f} | "
                    f"source={source:.4f} | "
                    f"difference={difference:.4f} | "
                    f"category=REVIEW_REQUIRED\n"
                )


# ============================================================
# ROE CROSS-CHECK
# ============================================================

if "roe_percentage" in company_columns:

    roe_rows = cursor.execute(
        f"""
        SELECT
            fr.company_id,
            fr.year,
            fr.return_on_equity_pct,
            c.roe_percentage

        FROM financial_ratios fr

        JOIN companies c

            ON fr.company_id = c.company_id

        WHERE
            fr.return_on_equity_pct
            IS NOT NULL

            AND c.roe_percentage
            IS NOT NULL
        """
    ).fetchall()


    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as log:

        for row in roe_rows:

            (
                company_id,
                year,
                calculated,
                source,
            ) = row


            difference = abs(
                calculated - source
            )


            if difference > 5:

                log.write(
                    f"ROE ANOMALY | "
                    f"company_id={company_id} | "
                    f"year={year} | "
                    f"calculated={calculated:.4f} | "
                    f"source={source:.4f} | "
                    f"difference={difference:.4f} | "
                    f"category=REVIEW_REQUIRED\n"
                )


# ============================================================
# FINISH LOG
# ============================================================

with open(
    LOG_FILE,
    "a",
    encoding="utf-8"
) as log:

    log.write("\n")
    log.write("=" * 70 + "\n")
    log.write("DAY 13 PROCESS COMPLETED\n")
    log.write("=" * 70 + "\n")


conn.commit()

conn.close()


# ============================================================
# OUTPUT
# ============================================================

print()
print("=" * 70)
print("DAY 13 COMPLETED")
print("=" * 70)

print(
    f"Financials companies: {financials_count}"
)

print(
    f"Edge-case log: {LOG_FILE}"
)

print()
print(
    "Bank/Financials leverage carve-out applied."
)

print(
    "ROCE/ROE source cross-check completed where "
    "source columns are available."
)