# ============================================================
# NIFTY 100 SCREENER ENGINE
# SPRINT 3 - DAY 15
# FILTER ENGINE CORE
# ============================================================

import sqlite3
from pathlib import Path

import pandas as pd
import yaml


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "nifty100.db"

CONFIG_PATH = (
    PROJECT_ROOT
    / "config"
    / "screener_config.yaml"
)


# ============================================================
# LOAD YAML CONFIGURATION
# ============================================================

def load_config():

    if not CONFIG_PATH.exists():

        raise FileNotFoundError(
            f"Configuration file not found:\n{CONFIG_PATH}"
        )

    with open(
        CONFIG_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        config = yaml.safe_load(file)

    return config


# ============================================================
# LOAD FINANCIAL RATIO DATA
# ============================================================

def load_financial_data():

    if not DB_PATH.exists():

        raise FileNotFoundError(
            f"Database not found:\n{DB_PATH}"
        )

    conn = sqlite3.connect(DB_PATH)

    try:

        df = pd.read_sql_query(
            """
            SELECT *
            FROM financial_ratios
            """,
            conn
        )

    finally:

        conn.close()

    return df


# ============================================================
# LOAD COMPANY DATA
# ============================================================

def load_company_data():

    conn = sqlite3.connect(DB_PATH)

    try:

        tables = pd.read_sql_query(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """,
            conn
        )["name"].tolist()


        if "companies" not in tables:

            return pd.DataFrame()


        df = pd.read_sql_query(
            """
            SELECT *
            FROM companies
            """,
            conn
        )

    finally:

        conn.close()

    return df


# ============================================================
# FIND SECTOR COLUMN
# ============================================================

def find_sector_column(
    company_df
):

    possible_columns = [
        "broad_sector",
        "sector",
        "broadsector",
    ]

    for column in possible_columns:

        if column in company_df.columns:

            return column

    return None


# ============================================================
# PREPARE SCREENING DATAFRAME
# ============================================================

def prepare_dataframe():

    financial_df = load_financial_data()

    company_df = load_company_data()


    if financial_df.empty:

        return financial_df


    # --------------------------------------------------------
    # No company table
    # --------------------------------------------------------

    if company_df.empty:

        financial_df[
            "broad_sector"
        ] = None

        return financial_df


    sector_column = find_sector_column(
        company_df
    )


    # --------------------------------------------------------
    # Select company information
    # --------------------------------------------------------

    company_columns = [
        "company_id"
    ]


    if "company_name" in company_df.columns:

        company_columns.append(
            "company_name"
        )


    if sector_column:

        company_columns.append(
            sector_column
        )


    company_info = (
        company_df[
            company_columns
        ]
        .drop_duplicates(
            subset=["company_id"]
        )
    )


    # --------------------------------------------------------
    # Merge
    # --------------------------------------------------------

    df = financial_df.merge(
        company_info,
        on="company_id",
        how="left"
    )


    # --------------------------------------------------------
    # Standardize sector name
    # --------------------------------------------------------

    if sector_column:

        if sector_column != "broad_sector":

            df = df.rename(
                columns={
                    sector_column:
                        "broad_sector"
                }
            )

    elif "broad_sector" not in df.columns:

        df[
            "broad_sector"
        ] = None


    return df


# ============================================================
# CONVERT NUMERIC COLUMNS
# ============================================================

def convert_numeric_columns(
    df
):

    protected_columns = {
        "company_id",
        "year",
        "company_name",
        "broad_sector",
        "icr_label",
    }


    for column in df.columns:

        if column not in protected_columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )


    return df


# ============================================================
# APPLY NORMAL NUMERIC FILTER
# ============================================================

def apply_numeric_condition(
    df,
    metric,
    condition
):

    if df.empty:

        return df


    result = df.copy()


    # --------------------------------------------------------
    # Minimum threshold
    # --------------------------------------------------------

    if "min" in condition:

        minimum = condition["min"]

        result = result[
            result[metric].notna()
            &
            (
                result[metric]
                >= minimum
            )
        ]


    # --------------------------------------------------------
    # Maximum threshold
    # --------------------------------------------------------

    if "max" in condition:

        maximum = condition["max"]

        result = result[
            result[metric].notna()
            &
            (
                result[metric]
                <= maximum
            )
        ]


    # --------------------------------------------------------
    # Exact value
    # --------------------------------------------------------

    if "equals" in condition:

        expected = condition["equals"]

        result = result[
            result[metric]
            == expected
        ]


    return result


# ============================================================
# INTEREST COVERAGE FILTER
# ============================================================

def apply_icr_filter(
    df,
    condition
):

    result = df.copy()


    if "min" not in condition:

        return result


    minimum = condition["min"]


    # --------------------------------------------------------
    # Debt-free companies automatically pass
    # --------------------------------------------------------

    if "icr_label" in result.columns:

        debt_free = (
            result["icr_label"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("debt free")
        )

    else:

        debt_free = pd.Series(
            False,
            index=result.index
        )


    # --------------------------------------------------------
    # Normal ICR
    # --------------------------------------------------------

    icr = pd.to_numeric(
        result.get(
            "interest_coverage"
        ),
        errors="coerce"
    )


    passes = (
        debt_free
        |
        (
            icr.notna()
            &
            (
                icr >= minimum
            )
        )
    )


    return result[passes]


# ============================================================
# DEBT-TO-EQUITY FILTER
# ============================================================

def apply_de_filter(
    df,
    condition
):

    result = df.copy()


    # --------------------------------------------------------
    # Financials sector
    #
    # D/E filter is skipped for Financials.
    # --------------------------------------------------------

    if "broad_sector" in result.columns:

        financials_mask = (
            result["broad_sector"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("financials")
        )

    else:

        financials_mask = pd.Series(
            False,
            index=result.index
        )


    financials_df = result[
        financials_mask
    ].copy()


    non_financials_df = result[
        ~financials_mask
    ].copy()


    # --------------------------------------------------------
    # Apply D/E filter only to non-financial companies
    # --------------------------------------------------------

    non_financials_df = apply_numeric_condition(
        non_financials_df,
        "debt_to_equity",
        condition
    )


    # --------------------------------------------------------
    # Put Financials back
    # --------------------------------------------------------

    result = pd.concat(
        [
            non_financials_df,
            financials_df
        ],
        ignore_index=True
    )


    return result


# ============================================================
# DEBT-TO-EQUITY DECLINING FILTER
# ============================================================

def apply_debt_declining_filter(
    df,
    condition
):

    if df.empty:

        return df


    if "company_id" not in df.columns:

        return df


    if "year" not in df.columns:

        return df


    if "debt_to_equity" not in df.columns:

        print(
            "WARNING: debt_to_equity "
            "column not available."
        )

        return df.iloc[0:0]


    result = df.copy()


    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    result = result.sort_values(
        [
            "company_id",
            "year"
        ]
    )


    # --------------------------------------------------------
    # Previous year's D/E
    # --------------------------------------------------------

    result[
        "previous_de"
    ] = (
        result
        .groupby("company_id")
        ["debt_to_equity"]
        .shift(1)
    )


    # --------------------------------------------------------
    # Current D/E < previous D/E
    # --------------------------------------------------------

    result[
        "_debt_declining"
    ] = (
        result["debt_to_equity"]
        <
        result["previous_de"]
    )


    expected = condition.get(
        "equals",
        True
    )


    result = result[
        result["_debt_declining"]
        == expected
    ]


    # --------------------------------------------------------
    # Remove temporary columns
    # --------------------------------------------------------

    result = result.drop(
        columns=[
            "previous_de",
            "_debt_declining"
        ],
        errors="ignore"
    )


    return result


# ============================================================
# APPLY ONE FILTER
# ============================================================

def apply_filter(
    df,
    metric,
    condition
):

    if df.empty:

        return df


    # --------------------------------------------------------
    # Special D/E declining filter
    # --------------------------------------------------------

    if metric == "debt_to_equity_declining":

        return apply_debt_declining_filter(
            df,
            condition
        )


    # --------------------------------------------------------
    # Check metric
    # --------------------------------------------------------

    if metric not in df.columns:

        print(
            f"WARNING: Metric "
            f"'{metric}' not found."
        )

        print(
            "Filter skipped."
        )

        return df


    # --------------------------------------------------------
    # D/E special handling
    # --------------------------------------------------------

    if metric == "debt_to_equity":

        return apply_de_filter(
            df,
            condition
        )


    # --------------------------------------------------------
    # ICR special handling
    # --------------------------------------------------------

    if metric == "interest_coverage":

        return apply_icr_filter(
            df,
            condition
        )


    # --------------------------------------------------------
    # Normal metric
    # --------------------------------------------------------

    return apply_numeric_condition(
        df,
        metric,
        condition
    )


# ============================================================
# NORMALIZE ONE METRIC USING P10/P90
# ============================================================

def normalize_metric(
    series
):

    numeric = pd.to_numeric(
        series,
        errors="coerce"
    )


    if numeric.notna().sum() == 0:

        return pd.Series(
            None,
            index=series.index,
            dtype=float
        )


    p10 = numeric.quantile(
        0.10
    )

    p90 = numeric.quantile(
        0.90
    )


    # --------------------------------------------------------
    # Avoid division by zero
    # --------------------------------------------------------

    if p90 == p10:

        return pd.Series(
            50.0,
            index=series.index
        )


    capped = numeric.clip(
        lower=p10,
        upper=p90
    )


    normalized = (
        (
            capped - p10
        )
        /
        (
            p90 - p10
        )
        * 100
    )


    return normalized


# ============================================================
# ADD COMPOSITE QUALITY SCORE
# ============================================================

def add_composite_score(
    df
):

    result = df.copy()


    if result.empty:

        result[
            "composite_quality_score"
        ] = pd.Series(
            dtype=float
        )

        return result


    score_columns = []


    # ========================================================
    # PROFITABILITY
    # ========================================================

    profitability_metrics = [
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "net_profit_margin_pct",
    ]


    for metric in profitability_metrics:

        if metric in result.columns:

            score_column = (
                "_score_"
                + metric
            )


            result[
                score_column
            ] = normalize_metric(
                result[metric]
            )


            score_columns.append(
                score_column
            )


    # ========================================================
    # GROWTH
    # ========================================================

    growth_metrics = [
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
    ]


    for metric in growth_metrics:

        if metric in result.columns:

            score_column = (
                "_score_"
                + metric
            )


            result[
                score_column
            ] = normalize_metric(
                result[metric]
            )


            score_columns.append(
                score_column
            )


    # ========================================================
    # LEVERAGE
    #
    # Lower D/E is better.
    # ========================================================

    if "debt_to_equity" in result.columns:

        de_score = normalize_metric(
            -pd.to_numeric(
                result[
                    "debt_to_equity"
                ],
                errors="coerce"
            )
        )


        result[
            "_score_debt_to_equity"
        ] = de_score


        score_columns.append(
            "_score_debt_to_equity"
        )


    # ========================================================
    # INTEREST COVERAGE
    # ========================================================

    if "interest_coverage" in result.columns:

        icr_score = normalize_metric(
            result[
                "interest_coverage"
            ]
        )


        # Debt-free companies are treated
        # as maximum ICR.

        if "icr_label" in result.columns:

            debt_free = (
                result[
                    "icr_label"
                ]
                .fillna("")
                .astype(str)
                .str.lower()
                .eq("debt free")
            )


            icr_score.loc[
                debt_free
            ] = 100


        result[
            "_score_interest_coverage"
        ] = icr_score


        score_columns.append(
            "_score_interest_coverage"
        )


    # ========================================================
    # FCF
    # ========================================================

    if "free_cash_flow_cr" in result.columns:

        result[
            "_score_fcf"
        ] = normalize_metric(
            result[
                "free_cash_flow_cr"
            ]
        )


        score_columns.append(
            "_score_fcf"
        )


    # ========================================================
    # FINAL SCORE
    # ========================================================

    if score_columns:

        result[
            "composite_quality_score"
        ] = (
            result[
                score_columns
            ]
            .mean(axis=1)
            .clip(
                lower=0,
                upper=100
            )
        )

    else:

        result[
            "composite_quality_score"
        ] = None


    # --------------------------------------------------------
    # Remove temporary score columns
    # --------------------------------------------------------

    result = result.drop(
        columns=score_columns,
        errors="ignore"
    )


    return result


# ============================================================
# APPLY PRESET
# ============================================================

def apply_preset(
    preset_name
):

    config = load_config()


    presets = config.get(
        "presets",
        {}
    )


    if preset_name not in presets:

        raise ValueError(
            f"Unknown preset: "
            f"{preset_name}"
        )


    preset = presets[
        preset_name
    ]


    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    df = prepare_dataframe()


    if df.empty:

        return df


    df = convert_numeric_columns(
        df
    )


    # --------------------------------------------------------
    # Apply every configured filter
    # --------------------------------------------------------

    filters = preset.get(
        "filters",
        {}
    )


    for metric, condition in filters.items():

        df = apply_filter(
            df,
            metric,
            condition
        )


    # --------------------------------------------------------
    # Composite score
    # --------------------------------------------------------

    df = add_composite_score(
        df
    )


    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    if (
        "composite_quality_score"
        in df.columns
    ):

        df = df.sort_values(
            "composite_quality_score",
            ascending=False
        )


    return df.reset_index(
        drop=True
    )


# ============================================================
# CUSTOM SCREEN
# ============================================================

def custom_screen(
    filters
):

    df = prepare_dataframe()


    if df.empty:

        return df


    df = convert_numeric_columns(
        df
    )


    # --------------------------------------------------------
    # Apply custom filters
    # --------------------------------------------------------

    for metric, condition in filters.items():

        df = apply_filter(
            df,
            metric,
            condition
        )


    # --------------------------------------------------------
    # Composite score
    # --------------------------------------------------------

    df = add_composite_score(
        df
    )


    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    if (
        "composite_quality_score"
        in df.columns
    ):

        df = df.sort_values(
            "composite_quality_score",
            ascending=False
        )


    return df.reset_index(
        drop=True
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print(
        "NIFTY 100 SCREENER ENGINE"
    )
    print(
        "SPRINT 3 - DAY 15"
    )
    print("=" * 70)


    # --------------------------------------------------------
    # Load configuration
    # --------------------------------------------------------

    config = load_config()


    print()
    print(
        "Configuration loaded successfully."
    )


    # --------------------------------------------------------
    # Show presets
    # --------------------------------------------------------

    print()
    print(
        "Available presets:"
    )


    for preset_name in config.get(
        "presets",
        {}
    ):

        print(
            f"  - {preset_name}"
        )


    # --------------------------------------------------------
    # Show filter count
    # --------------------------------------------------------

    metrics = config.get(
        "filterable_metrics",
        []
    )


    print()
    print(
        "Filterable metrics:",
        len(metrics)
    )


    # --------------------------------------------------------
    # Load database
    # --------------------------------------------------------

    print()
    print(
        "Loading financial data..."
    )


    df = prepare_dataframe()


    print(
        "Rows available:",
        len(df)
    )


    print(
        "Columns available:",
        len(df.columns)
    )


    # --------------------------------------------------------
    # Test Quality Compounder
    # --------------------------------------------------------

    print()
    print(
        "Running Quality Compounder..."
    )


    result = apply_preset(
        "quality_compounder"
    )


    print(
        "Quality Compounder results:",
        len(result)
    )


    # --------------------------------------------------------
    # Display results
    # --------------------------------------------------------

    if not result.empty:

        display_columns = [
            column
            for column in [
                "company_id",
                "year",
                "company_name",
                "return_on_equity_pct",
                "debt_to_equity",
                "free_cash_flow_cr",
                "revenue_cagr_5yr",
                "composite_quality_score",
            ]
            if column in result.columns
        ]


        print()
        print(
            result[
                display_columns
            ]
            .head(10)
            .to_string(
                index=False
            )
        )


    # --------------------------------------------------------
    # Finish
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "DAY 15 ENGINE TEST COMPLETED"
    )
    print("=" * 70)