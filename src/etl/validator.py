from pathlib import Path
import pandas as pd
import re


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_FOLDER = PROJECT_ROOT / "data" / "processed"
OUTPUT_FOLDER = PROJECT_ROOT / "output"

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

failures = []


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def add_failure(rule, severity, table, message):

    failures.append({
        "rule": rule,
        "severity": severity,
        "table": table,
        "message": message
    })


def numeric_series(df, column):

    if column not in df.columns:
        return None

    return pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# DQ-01: PRIMARY KEY UNIQUENESS
# ============================================================

def check_primary_key(df, columns, table_name):

    if not all(
        column in df.columns
        for column in columns
    ):
        return

    duplicate_count = df.duplicated(
        subset=columns
    ).sum()

    if duplicate_count > 0:

        add_failure(
            "DQ-01",
            "CRITICAL",
            table_name,
            f"{duplicate_count} duplicate primary-key records "
            f"found using {columns}"
        )


# ============================================================
# DQ-02: COMPANY + YEAR UNIQUENESS
# ============================================================

def check_company_year(df, table_name):

    if "company_id" not in df.columns:
        return

    if "year" not in df.columns:
        return

    duplicate_count = df.duplicated(
        subset=["company_id", "year"]
    ).sum()

    if duplicate_count > 0:

        add_failure(
            "DQ-02",
            "CRITICAL",
            table_name,
            f"{duplicate_count} duplicate company-year records found"
        )


# ============================================================
# DQ-03: FOREIGN KEY INTEGRITY
# ============================================================

def check_company_id(df, table_name):

    if "company_id" not in df.columns:
        return

    missing = df["company_id"].isna().sum()

    if missing > 0:

        add_failure(
            "DQ-03",
            "CRITICAL",
            table_name,
            f"{missing} records have missing company_id"
        )


# ============================================================
# DQ-04: BALANCE SHEET BALANCE
# Assets = Liabilities + Equity
# ============================================================

def check_balance_sheet(df, table_name):

    required = [
        "assets",
        "liabilities",
        "equity"
    ]

    if not all(
        column in df.columns
        for column in required
    ):
        return

    assets = numeric_series(df, "assets")
    liabilities = numeric_series(df, "liabilities")
    equity = numeric_series(df, "equity")

    calculated = liabilities + equity

    valid = (
        assets.notna() &
        calculated.notna() &
        (assets != 0)
    )

    difference = (
        abs(assets - calculated) /
        assets.abs()
    )

    invalid = (
        (difference > 0.01) &
        valid
    ).sum()

    if invalid > 0:

        add_failure(
            "DQ-04",
            "WARNING",
            table_name,
            f"{invalid} records have balance-sheet "
            f"difference greater than 1%"
        )


# ============================================================
# DQ-05: OPERATING PROFIT MARGIN
# OPM = Operating Profit / Sales × 100
# ============================================================

def check_opm(df, table_name):

    if not all(
        column in df.columns
        for column in [
            "sales",
            "operating_profit"
        ]
    ):
        return

    sales = numeric_series(df, "sales")
    operating_profit = numeric_series(
        df,
        "operating_profit"
    )

    valid = (
        sales.notna() &
        operating_profit.notna() &
        (sales != 0)
    )

    opm = (
        operating_profit /
        sales
    ) * 100

    invalid = (
        (
            (opm < -100) |
            (opm > 100)
        ) &
        valid
    ).sum()

    if invalid > 0:

        add_failure(
            "DQ-05",
            "WARNING",
            table_name,
            f"{invalid} records have unusual "
            f"operating profit margin"
        )


# ============================================================
# DQ-06: POSITIVE SALES
# ============================================================

def check_sales(df, table_name):

    if "sales" not in df.columns:
        return

    sales = numeric_series(
        df,
        "sales"
    )

    invalid = (
        sales <= 0
    ).sum()

    if invalid > 0:

        add_failure(
            "DQ-06",
            "WARNING",
            table_name,
            f"{invalid} records have sales <= 0"
        )


# ============================================================
# DQ-07: NET CASH
# Net Cash = Cash - Debt
# ============================================================

def check_net_cash(df, table_name):

    if not all(
        column in df.columns
        for column in [
            "cash",
            "debt"
        ]
    ):
        return

    cash = numeric_series(df, "cash")
    debt = numeric_series(df, "debt")

    net_cash = cash - debt

    invalid = net_cash.isna().sum()

    if invalid > 0:

        add_failure(
            "DQ-07",
            "WARNING",
            table_name,
            f"{invalid} invalid net-cash calculations"
        )


# ============================================================
# DQ-08: TAX RATE
# Tax Rate = Tax / Profit Before Tax × 100
# ============================================================

def check_tax_rate(df, table_name):

    if not all(
        column in df.columns
        for column in [
            "tax",
            "profit_before_tax"
        ]
    ):
        return

    tax = numeric_series(
        df,
        "tax"
    )

    pbt = numeric_series(
        df,
        "profit_before_tax"
    )

    valid = (
        tax.notna() &
        pbt.notna() &
        (pbt != 0)
    )

    tax_rate = (
        tax / pbt
    ) * 100

    invalid = (
        (
            (tax_rate < 0) |
            (tax_rate > 100)
        ) &
        valid
    ).sum()

    if invalid > 0:

        add_failure(
            "DQ-08",
            "WARNING",
            table_name,
            f"{invalid} records have tax rate "
            f"outside 0%-100%"
        )


# ============================================================
# DQ-09: DIVIDEND CAP
# Dividend should not exceed net profit
# ============================================================

def check_dividend(df, table_name):

    if not all(
        column in df.columns
        for column in [
            "dividend",
            "net_profit"
        ]
    ):
        return

    dividend = numeric_series(
        df,
        "dividend"
    )

    net_profit = numeric_series(
        df,
        "net_profit"
    )

    valid = (
        dividend.notna() &
        net_profit.notna() &
        (net_profit > 0)
    )

    invalid = (
        (dividend > net_profit) &
        valid
    ).sum()

    if invalid > 0:

        add_failure(
            "DQ-09",
            "WARNING",
            table_name,
            f"{invalid} records have dividend "
            f"greater than net profit"
        )


# ============================================================
# DQ-10: URL VALIDATION
# ============================================================

def check_urls(df, table_name):

    if "url" not in df.columns:
        return

    urls = df["url"].dropna().astype(str)

    pattern = re.compile(
        r"^https?://"
    )

    invalid = (
        ~urls.apply(
            lambda x: bool(
                pattern.match(x)
            )
        )
    ).sum()

    if invalid > 0:

        add_failure(
            "DQ-10",
            "WARNING",
            table_name,
            f"{invalid} invalid URL values found"
        )


# ============================================================
# DQ-11: EPS SIGN CHECK
# EPS should have a valid numeric value
# ============================================================

def check_eps(df, table_name):

    if "eps" not in df.columns:
        return

    eps = numeric_series(
        df,
        "eps"
    )

    invalid = eps.isna().sum()

    if invalid > 0:

        add_failure(
            "DQ-11",
            "WARNING",
            table_name,
            f"{invalid} invalid EPS values found"
        )


# ============================================================
# DQ-12: BSE BALANCE CHECK
# ============================================================

def check_bse_balance(df, table_name):

    if not all(
        column in df.columns
        for column in [
            "bse_assets",
            "bse_liabilities",
            "bse_equity"
        ]
    ):
        return

    assets = numeric_series(
        df,
        "bse_assets"
    )

    liabilities = numeric_series(
        df,
        "bse_liabilities"
    )

    equity = numeric_series(
        df,
        "bse_equity"
    )

    calculated = liabilities + equity

    valid = (
        assets.notna() &
        calculated.notna() &
        (assets != 0)
    )

    difference = (
        abs(assets - calculated) /
        assets.abs()
    )

    invalid = (
        (difference > 0.01) &
        valid
    ).sum()

    if invalid > 0:

        add_failure(
            "DQ-12",
            "WARNING",
            table_name,
            f"{invalid} BSE balance records "
            f"differ by more than 1%"
        )


# ============================================================
# DQ-13: YEAR COVERAGE
# Companies should have at least 5 years of data
# ============================================================

def check_year_coverage(df, table_name):

    if not all(
        column in df.columns
        for column in [
            "company_id",
            "year"
        ]
    ):
        return

    years_per_company = (
        df.groupby("company_id")["year"]
        .nunique()
    )

    insufficient = (
        years_per_company < 5
    ).sum()

    if insufficient > 0:

        add_failure(
            "DQ-13",
            "WARNING",
            table_name,
            f"{insufficient} companies have "
            f"less than 5 years of data"
        )


# ============================================================
# DQ-14: YEAR VALIDATION
# ============================================================

def check_year(df, table_name):

    if "year" not in df.columns:
        return

    years = pd.to_numeric(
        df["year"],
        errors="coerce"
    )

    current_year = pd.Timestamp.now().year

    invalid = (
        years.isna() |
        (years < 1900) |
        (years > current_year)
    ).sum()

    if invalid > 0:

        add_failure(
            "DQ-14",
            "WARNING",
            table_name,
            f"{invalid} invalid year values found"
        )


# ============================================================
# DQ-15: TICKER VALIDATION
# ============================================================

def check_ticker(df, table_name):

    if "ticker" not in df.columns:
        return

    tickers = (
        df["ticker"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    invalid = (
        (tickers == "") |
        (tickers.str.len() > 20)
    ).sum()

    if invalid > 0:

        add_failure(
            "DQ-15",
            "WARNING",
            table_name,
            f"{invalid} invalid ticker values found"
        )


# ============================================================
# DQ-16: DATA COVERAGE / MISSING VALUES
# ============================================================

def check_data_coverage(df, table_name):

    if df.empty:
        add_failure(
            "DQ-16",
            "CRITICAL",
            table_name,
            "Table contains zero records"
        )
        return

    # Count rows where every field is empty
    empty_rows = df.isna().all(axis=1).sum()

    if empty_rows > 0:

        add_failure(
            "DQ-16",
            "WARNING",
            table_name,
            f"{empty_rows} completely empty rows found"
        )


# ============================================================
# VALIDATE ONE FILE
# ============================================================

def validate_file(file_name):

    file_path = (
        PROCESSED_FOLDER /
        file_name
    )

    if not file_path.exists():
        return

    df = pd.read_csv(
        file_path
    )

    table_name = file_path.stem

    print(
        f"Checking {table_name}..."
    )

    # --------------------------------------------------------
    # DQ-01
    # --------------------------------------------------------

    yearly_tables = [
        "profitandloss_clean",
        "balancesheet_clean",
        "cashflow_clean",
        "analysis_clean",
        "financial_ratios_clean"
    ]

    if table_name == "stock_prices_clean":

        check_primary_key(
            df,
            ["company_id", "date"],
            table_name
        )

    elif table_name in yearly_tables:

        check_primary_key(
            df,
            ["company_id", "year"],
            table_name
        )

    elif "company_id" in df.columns:

        check_primary_key(
            df,
            ["company_id"],
            table_name
        )

    # --------------------------------------------------------
    # DQ-02
    # --------------------------------------------------------

    check_company_year(
        df,
        table_name
    )

    # --------------------------------------------------------
    # DQ-03
    # --------------------------------------------------------

    check_company_id(
        df,
        table_name
    )

    # --------------------------------------------------------
    # DQ-04
    # --------------------------------------------------------

    if table_name == "balancesheet_clean":

        check_balance_sheet(
            df,
            table_name
        )

    # --------------------------------------------------------
    # DQ-05
    # --------------------------------------------------------

    if table_name == "profitandloss_clean":

        check_opm(
            df,
            table_name
        )

    # --------------------------------------------------------
    # DQ-06
    # --------------------------------------------------------

    check_sales(
        df,
        table_name
    )

    # --------------------------------------------------------
    # DQ-07
    # --------------------------------------------------------

    check_net_cash(
        df,
        table_name
    )

    # --------------------------------------------------------
    # DQ-08
    # --------------------------------------------------------

    check_tax_rate(
        df,
        table_name
    )

    # --------------------------------------------------------
    # DQ-09
    # --------------------------------------------------------

    check_dividend(
        df,
        table_name
    )

    # --------------------------------------------------------
    # DQ-10
    # --------------------------------------------------------

    check_urls(
        df,
        table_name
    )

    # --------------------------------------------------------
    # DQ-11
    # --------------------------------------------------------

    check_eps(
        df,
        table_name
    )

    # --------------------------------------------------------
    # DQ-12
    # --------------------------------------------------------

    check_bse_balance(
        df,
        table_name
    )

    # --------------------------------------------------------
    # DQ-13
    # --------------------------------------------------------

    check_year_coverage(
        df,
        table_name
    )

    # --------------------------------------------------------
    # DQ-14
    # --------------------------------------------------------

    check_year(
        df,
        table_name
    )

    # --------------------------------------------------------
    # DQ-15
    # --------------------------------------------------------

    check_ticker(
        df,
        table_name
    )

    # --------------------------------------------------------
    # DQ-16
    # --------------------------------------------------------

    check_data_coverage(
        df,
        table_name
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("STARTING DATA QUALITY VALIDATION")
    print("DQ-01 TO DQ-16")
    print("=" * 60)
    print()

    csv_files = list(
        PROCESSED_FOLDER.glob("*.csv")
    )

    if not csv_files:

        print(
            "ERROR: No processed CSV files found."
        )

    else:

        for file in csv_files:

            try:

                validate_file(
                    file.name
                )

            except Exception as error:

                add_failure(
                    "SYSTEM",
                    "CRITICAL",
                    file.name,
                    str(error)
                )

    # ========================================================
    # CREATE REPORT
    # ========================================================

    output_file = (
        OUTPUT_FOLDER /
        "validation_failures.csv"
    )

    failure_df = pd.DataFrame(
        failures,
        columns=[
            "rule",
            "severity",
            "table",
            "message"
        ]
    )

    failure_df.to_csv(
        output_file,
        index=False
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 60)
    print("VALIDATION COMPLETED")
    print("=" * 60)

    print(
        f"Total failures: {len(failure_df)}"
    )

    if len(failure_df) > 0:

        critical = (
            failure_df["severity"] ==
            "CRITICAL"
        ).sum()

        warnings = (
            failure_df["severity"] ==
            "WARNING"
        ).sum()

        print(
            f"CRITICAL failures: {critical}"
        )

        print(
            f"WARNING failures: {warnings}"
        )

    else:

        print(
            "All DQ rules passed!"
        )

    print(
        f"\nReport saved to:\n{output_file}"
    )

    print()