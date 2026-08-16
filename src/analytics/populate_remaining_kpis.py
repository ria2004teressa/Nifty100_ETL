# ============================================================
# SPRINT 2 - DAY 12
# REMAINING FINANCIAL KPI ENGINE
# ============================================================

import sqlite3
from pathlib import Path
import math


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "nifty100.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


print("=" * 70)
print("DAY 12 - REMAINING FINANCIAL KPIs")
print("=" * 70)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_columns(table_name):

    return [
        row[1]
        for row in cursor.execute(
            f"PRAGMA table_info({table_name})"
        )
    ]


def add_column_if_missing(
    table_name,
    column_name,
    data_type="REAL"
):

    columns = get_columns(table_name)

    if column_name not in columns:

        cursor.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name} {data_type}
            """
        )

        print(
            f"Added column: {table_name}.{column_name}"
        )


def safe_number(value):

    if value is None:
        return None

    try:
        return float(value)

    except (TypeError, ValueError):
        return None


# ============================================================
# CAGR ENGINE
# ============================================================

def calculate_cagr(
    start_value,
    end_value,
    years
):
    """
    CAGR with all required edge cases.

    Returns:
        (cagr_value, flag)

    Flags:
        NORMAL
        DECLINE_TO_LOSS
        TURNAROUND
        BOTH_NEGATIVE
        ZERO_BASE
        INSUFFICIENT
    """

    start_value = safe_number(start_value)
    end_value = safe_number(end_value)

    if (
        start_value is None
        or end_value is None
        or years is None
        or years <= 0
    ):

        return None, "INSUFFICIENT"


    if start_value == 0:

        return None, "ZERO_BASE"


    # Positive -> Positive
    if (
        start_value > 0
        and end_value > 0
    ):

        try:

            result = (
                (end_value / start_value)
                ** (1 / years)
                - 1
            ) * 100

            return result, "NORMAL"

        except (
            ValueError,
            ZeroDivisionError
        ):

            return None, "INSUFFICIENT"


    # Positive -> Negative
    if (
        start_value > 0
        and end_value < 0
    ):

        return None, "DECLINE_TO_LOSS"


    # Negative -> Positive
    if (
        start_value < 0
        and end_value > 0
    ):

        return None, "TURNAROUND"


    # Negative -> Negative
    if (
        start_value < 0
        and end_value < 0
    ):

        return None, "BOTH_NEGATIVE"


    return None, "INSUFFICIENT"


# ============================================================
# LOAD TABLE COLUMNS
# ============================================================

pl_columns = get_columns(
    "profitandloss"
)

bs_columns = get_columns(
    "balancesheet"
)

cf_columns = get_columns(
    "cashflow"
)

ratio_columns = get_columns(
    "financial_ratios"
)


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
    "net_profit",
    "eps",
    "dividend",
]

required_bs = [
    "company_id",
    "year",
    "equity",
    "assets",
]

required_cf = [
    "company_id",
    "year",
    "operating_cash_flow",
    "investing_cash_flow",
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

missing_cf = [
    column
    for column in required_cf
    if column not in cf_columns
]


if missing_pl:

    print("\nERROR: Missing P&L columns:")
    print(missing_pl)

    conn.close()

    raise SystemExit(1)


if missing_bs:

    print("\nERROR: Missing Balance Sheet columns:")
    print(missing_bs)

    conn.close()

    raise SystemExit(1)


if missing_cf:

    print("\nERROR: Missing Cash Flow columns:")
    print(missing_cf)

    conn.close()

    raise SystemExit(1)


# ============================================================
# REQUIRED FINANCIAL RATIO COLUMNS
# ============================================================

required_ratio_columns = {

    "earnings_per_share":
        "REAL",

    "book_value_per_share":
        "REAL",

    "dividend_payout_ratio_pct":
        "REAL",

    "revenue_cagr_5yr":
        "REAL",

    "revenue_cagr_5yr_flag":
        "TEXT",

    "pat_cagr_5yr":
        "REAL",

    "pat_cagr_5yr_flag":
        "TEXT",

    "eps_cagr_5yr":
        "REAL",

    "eps_cagr_5yr_flag":
        "TEXT",

    "composite_quality_score":
        "REAL",
}


for column, data_type in required_ratio_columns.items():

    add_column_if_missing(
        "financial_ratios",
        column,
        data_type
    )


conn.commit()


# ============================================================
# GET ALL P&L DATA
# ============================================================

pl_query = """
SELECT
    company_id,
    year,
    sales,
    net_profit,
    eps,
    dividend

FROM profitandloss

ORDER BY
    company_id,
    year
"""


pl_rows = cursor.execute(
    pl_query
).fetchall()


print()
print(
    "P&L rows:",
    len(pl_rows)
)


# ============================================================
# GET BALANCE SHEET DATA
# ============================================================

bs_query = """
SELECT
    company_id,
    year,
    equity,
    assets

FROM balancesheet
"""


bs_rows = cursor.execute(
    bs_query
).fetchall()


# ============================================================
# BALANCE SHEET LOOKUP
# ============================================================

balance_lookup = {}

for row in bs_rows:

    (
        company_id,
        year,
        equity,
        assets,
    ) = row

    balance_lookup[
        (company_id, year)
    ] = {
        "equity": safe_number(equity),
        "assets": safe_number(assets),
    }


# ============================================================
# GROUP P&L DATA BY COMPANY
# ============================================================

company_records = {}


for row in pl_rows:

    (
        company_id,
        year,
        sales,
        net_profit,
        eps,
        dividend,
    ) = row


    record = {

        "company_id":
            company_id,

        "year":
            year,

        "sales":
            safe_number(sales),

        "net_profit":
            safe_number(net_profit),

        "eps":
            safe_number(eps),

        "dividend":
            safe_number(dividend),

    }


    if company_id not in company_records:

        company_records[company_id] = []


    company_records[
        company_id
    ].append(record)


# ============================================================
# INSERT MISSING COMPANY-YEAR ROWS
# ============================================================

print()
print(
    "Ensuring financial_ratios contains "
    "all company-year records..."
)


ratio_columns_now = get_columns(
    "financial_ratios"
)


inserted = 0


for company_id, records in company_records.items():

    for record in records:

        year = record["year"]


        existing = cursor.execute(
            """
            SELECT 1

            FROM financial_ratios

            WHERE
                company_id = ?
                AND year = ?

            LIMIT 1
            """,
            (
                company_id,
                year,
            )
        ).fetchone()


        if existing is None:

            cursor.execute(
                """
                INSERT INTO financial_ratios
                (
                    company_id,
                    year
                )

                VALUES (?, ?)
                """,
                (
                    company_id,
                    year,
                )
            )

            inserted += 1


conn.commit()


print(
    "New financial_ratios rows inserted:",
    inserted
)


# ============================================================
# HELPER FOR 5-YEAR VALUE
# ============================================================

def get_previous_value(
    records,
    current_year,
    field,
    years=5
):

    target_year = current_year - years


    for record in records:

        if record["year"] == target_year:

            return record.get(field)


    return None


# ============================================================
# PROCESS KPI VALUES
# ============================================================

updated = 0


for company_id, records in company_records.items():

    for record in records:

        year = record["year"]


        # ----------------------------------------------------
        # CURRENT VALUES
        # ----------------------------------------------------

        sales = record["sales"]

        pat = record["net_profit"]

        eps = record["eps"]

        dividend = record["dividend"]


        # ----------------------------------------------------
        # BALANCE SHEET
        # ----------------------------------------------------

        balance = balance_lookup.get(
            (
                company_id,
                year
            ),
            {}
        )


        equity = balance.get(
            "equity"
        )


        # ----------------------------------------------------
        # BOOK VALUE PER SHARE
        # ----------------------------------------------------
        #
        # We DO NOT have shares outstanding.
        #
        # Therefore we cannot safely calculate:
        #
        # equity / shares
        #
        # Instead of inventing a denominator,
        # store NULL.
        # ----------------------------------------------------

        book_value_per_share = None


        # ----------------------------------------------------
        # DIVIDEND PAYOUT RATIO
        # ----------------------------------------------------

        dividend_payout = None


        if (
            dividend is not None
            and pat is not None
            and pat != 0
        ):

            dividend_payout = (
                dividend / pat
            ) * 100


        # ----------------------------------------------------
        # REVENUE CAGR
        # ----------------------------------------------------

        previous_sales = get_previous_value(
            records,
            year,
            "sales",
            5
        )


        revenue_cagr, revenue_flag = calculate_cagr(
            previous_sales,
            sales,
            5
        )


        # ----------------------------------------------------
        # PAT CAGR
        # ----------------------------------------------------

        previous_pat = get_previous_value(
            records,
            year,
            "net_profit",
            5
        )


        pat_cagr, pat_flag = calculate_cagr(
            previous_pat,
            pat,
            5
        )


        # ----------------------------------------------------
        # EPS CAGR
        # ----------------------------------------------------

        previous_eps = get_previous_value(
            records,
            year,
            "eps",
            5
        )


        eps_cagr, eps_flag = calculate_cagr(
            previous_eps,
            eps,
            5
        )


        # ----------------------------------------------------
        # COMPOSITE QUALITY SCORE
        # ----------------------------------------------------
        #
        # Uses the already-calculated core ratios.
        #
        # This is a simple normalized score, not a
        # market-standard rating.
        # ----------------------------------------------------

        ratio_result = cursor.execute(
            """
            SELECT
                return_on_equity_pct,
                debt_to_equity,
                net_profit_margin_pct

            FROM financial_ratios

            WHERE
                company_id = ?
                AND year = ?

            LIMIT 1
            """,
            (
                company_id,
                year,
            )
        ).fetchone()


        composite_score = None


        if ratio_result is not None:

            roe = safe_number(
                ratio_result[0]
            )

            de = safe_number(
                ratio_result[1]
            )

            npm = safe_number(
                ratio_result[2]
            )


            score_components = []


            # ROE component
            if roe is not None:

                roe_score = min(
                    max(roe, 0),
                    100
                )

                score_components.append(
                    roe_score
                )


            # Debt component
            if de is not None:

                debt_score = max(
                    0,
                    100 - (de * 10)
                )

                score_components.append(
                    debt_score
                )


            # Margin component
            if npm is not None:

                margin_score = min(
                    max(npm, 0),
                    100
                )

                score_components.append(
                    margin_score
                )


            if score_components:

                composite_score = (
                    sum(score_components)
                    / len(score_components)
                )


        # ----------------------------------------------------
        # UPDATE DATABASE
        # ----------------------------------------------------

        cursor.execute(
            """
            UPDATE financial_ratios

            SET

                earnings_per_share = ?,

                book_value_per_share = ?,

                dividend_payout_ratio_pct = ?,

                revenue_cagr_5yr = ?,

                revenue_cagr_5yr_flag = ?,

                pat_cagr_5yr = ?,

                pat_cagr_5yr_flag = ?,

                eps_cagr_5yr = ?,

                eps_cagr_5yr_flag = ?,

                composite_quality_score = ?

            WHERE

                company_id = ?

                AND year = ?
            """,

            (

                eps,

                book_value_per_share,

                dividend_payout,

                revenue_cagr,

                revenue_flag,

                pat_cagr,

                pat_flag,

                eps_cagr,

                eps_flag,

                composite_score,

                company_id,

                year,

            )
        )


        if cursor.rowcount > 0:

            updated += cursor.rowcount


# ============================================================
# COMMIT
# ============================================================

conn.commit()


# ============================================================
# FINAL ROW COUNT
# ============================================================

ratio_count = cursor.execute(
    """
    SELECT COUNT(*)
    FROM financial_ratios
    """
).fetchone()[0]


company_count = cursor.execute(
    """
    SELECT COUNT(DISTINCT company_id)
    FROM financial_ratios
    """
).fetchone()[0]


year_count = cursor.execute(
    """
    SELECT COUNT(DISTINCT year)
    FROM financial_ratios
    """
).fetchone()[0]


# ============================================================
# KPI NULL REPORT
# ============================================================

kpis = [

    "net_profit_margin_pct",

    "operating_profit_margin_pct",

    "return_on_equity_pct",

    "return_on_capital_employed_pct",

    "return_on_assets_pct",

    "debt_to_equity",

    "asset_turnover",

    "free_cash_flow_cr",

    "earnings_per_share",

    "book_value_per_share",

    "dividend_payout_ratio_pct",

    "revenue_cagr_5yr",

    "pat_cagr_5yr",

    "eps_cagr_5yr",

    "composite_quality_score",

]


print()
print("=" * 70)
print("KPI NULL REPORT")
print("=" * 70)


for kpi in kpis:

    null_count = cursor.execute(
        f"""
        SELECT COUNT(*)

        FROM financial_ratios

        WHERE
            {kpi} IS NULL
        """
    ).fetchone()[0]


    total_count = cursor.execute(
        """
        SELECT COUNT(*)
        FROM financial_ratios
        """
    ).fetchone()[0]


    populated = (
        total_count
        - null_count
    )


    print(
        f"{kpi:<40}"
        f" populated={populated:<6}"
        f" null={null_count}"
    )


# ============================================================
# CAGR FLAG REPORT
# ============================================================

print()
print("=" * 70)
print("CAGR FLAG SUMMARY")
print("=" * 70)


for column in [
    "revenue_cagr_5yr_flag",
    "pat_cagr_5yr_flag",
    "eps_cagr_5yr_flag",
]:

    print()
    print(column)


    flag_rows = cursor.execute(
        f"""
        SELECT
            {column},
            COUNT(*)

        FROM financial_ratios

        GROUP BY
            {column}

        ORDER BY
            COUNT(*) DESC
        """
    ).fetchall()


    for flag, count in flag_rows:

        print(
            f"  {flag}: {count}"
        )


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 70)
print("DAY 12 COMPLETED")
print("=" * 70)

print()
print(
    "Companies:",
    company_count
)

print(
    "Years:",
    year_count
)

print(
    "financial_ratios rows:",
    ratio_count
)

print(
    "Rows inserted:",
    inserted
)

print(
    "Rows updated:",
    updated
)


if ratio_count >= 1100:

    print()
    print(
        "SUCCESS: financial_ratios has "
        "at least 1,100 rows."
    )

else:

    print()
    print(
        "WARNING: financial_ratios has "
        f"{ratio_count} rows."
    )

    print(
        "Target is at least 1,100 rows."
    )


print()
print("=" * 70)


# ============================================================
# CLOSE
# ============================================================

conn.close()