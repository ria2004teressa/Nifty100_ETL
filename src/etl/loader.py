from pathlib import Path
import sqlite3
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_FOLDER = PROJECT_ROOT / "data" / "processed"

DB_PATH = PROJECT_ROOT / "nifty100.db"

OUTPUT_FOLDER = PROJECT_ROOT / "output"

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

AUDIT_FILE = OUTPUT_FOLDER / "load_audit.csv"


# ============================================================
# CSV -> DATABASE TABLE MAPPING
# ============================================================

TABLE_MAPPING = {

    "companies_clean.csv": "companies",

    "profitandloss_clean.csv": "profitandloss",

    "balancesheet_clean.csv": "balancesheet",

    "cashflow_clean.csv": "cashflow",

    "analysis_clean.csv": "analysis",

    "documents_clean.csv": "documents",

    "prosandcons_clean.csv": "prosandcons",

    "sectors_clean.csv": "sectors",

    "stock_prices_clean.csv": "stock_prices",

    "financial_ratios_clean.csv": "financial_ratios",

    "peer_groups_clean.csv": "peer_groups"
}


# ============================================================
# LOAD ONE CSV
# ============================================================

def load_file(
    connection,
    csv_file,
    table_name
):

    print()
    print(
        f"Loading {csv_file.name} -> {table_name}"
    )

    try:

        # Read CSV
        df = pd.read_csv(
            csv_file
        )

        source_rows = len(df)

        print(
            f"Source rows: {source_rows}"
        )

        if df.empty:

            print(
                "WARNING: File is empty."
            )

            return {
                "table": table_name,
                "source_rows": 0,
                "loaded_rows": 0,
                "rejected_rows": 0,
                "status": "EMPTY"
            }

        # ----------------------------------------------------
        # INSERT DATA
        # ----------------------------------------------------

        df.to_sql(
            table_name,
            connection,
            if_exists="append",
            index=False
        )

        loaded_rows = len(df)

        print(
            f"Loaded rows: {loaded_rows}"
        )

        return {
            "table": table_name,
            "source_rows": source_rows,
            "loaded_rows": loaded_rows,
            "rejected_rows": 0,
            "status": "SUCCESS"
        }

    except Exception as error:

        print(
            f"ERROR: {error}"
        )

        return {
            "table": table_name,
            "source_rows": len(df) if "df" in locals() else 0,
            "loaded_rows": 0,
            "rejected_rows": len(df) if "df" in locals() else 0,
            "status": f"ERROR: {error}"
        }


# ============================================================
# MAIN LOADER
# ============================================================

def main():

    print()
    print("=" * 60)
    print("NIFTY100 FULL DATA LOAD")
    print("=" * 60)

    # --------------------------------------------------------
    # CHECK DATABASE
    # --------------------------------------------------------

    if not DB_PATH.exists():

        print()
        print(
            "ERROR: nifty100.db does not exist."
        )

        print(
            "Run create_database.py first."
        )

        return

    # --------------------------------------------------------
    # CONNECT DATABASE
    # --------------------------------------------------------

    connection = sqlite3.connect(
        DB_PATH
    )

    # Enable foreign keys
    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    audit = []

    # --------------------------------------------------------
    # LOAD FILES
    # --------------------------------------------------------

    for filename, table_name in TABLE_MAPPING.items():

        csv_file = (
            PROCESSED_FOLDER /
            filename
        )

        if not csv_file.exists():

            print()
            print(
                f"WARNING: {filename} not found."
            )

            audit.append({
                "table": table_name,
                "source_rows": 0,
                "loaded_rows": 0,
                "rejected_rows": 0,
                "status": "FILE NOT FOUND"
            })

            continue

        result = load_file(
            connection,
            csv_file,
            table_name
        )

        audit.append(
            result
        )

        # Stop on critical loading error
        if result["status"].startswith("ERROR"):

            print()
            print(
                "Critical loading error."
            )

            print(
                "Stopping the data load."
            )

            break

    # --------------------------------------------------------
    # FOREIGN KEY CHECK
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("FOREIGN KEY CHECK")
    print("=" * 60)

    cursor = connection.cursor()

    cursor.execute(
        "PRAGMA foreign_key_check;"
    )

    foreign_key_errors = cursor.fetchall()

    if len(foreign_key_errors) == 0:

        print(
            "Foreign key check: 0 errors"
        )

    else:

        print(
            f"Foreign key errors: "
            f"{len(foreign_key_errors)}"
        )

        for error in foreign_key_errors:

            print(error)

    # --------------------------------------------------------
    # COMMIT
    # --------------------------------------------------------

    connection.commit()

    # --------------------------------------------------------
    # SAVE AUDIT
    # --------------------------------------------------------

    audit_df = pd.DataFrame(
        audit
    )

    audit_df.to_csv(
        AUDIT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # DISPLAY DATABASE COUNTS
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("DATABASE ROW COUNTS")
    print("=" * 60)

    for filename, table_name in TABLE_MAPPING.items():

        try:

            cursor.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            )

            count = cursor.fetchone()[0]

            print(
                f"{table_name}: {count}"
            )

        except sqlite3.Error:

            pass

    # --------------------------------------------------------
    # CLOSE
    # --------------------------------------------------------

    connection.close()

    print()
    print("=" * 60)
    print("DATA LOAD COMPLETED")
    print("=" * 60)

    print(
        f"Audit file:\n{AUDIT_FILE}"
    )

    print()
    

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()