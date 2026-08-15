import sqlite3
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DB_PATH = PROJECT_ROOT / "nifty100.db"

SQL_PATH = (
    PROJECT_ROOT
    / "notebooks"
    / "exploratory_queries.sql"
)


# ============================================================
# CHECK FILES
# ============================================================

if not DB_PATH.exists():
    print("ERROR: nifty100.db not found.")
    raise SystemExit(1)

if not SQL_PATH.exists():
    print("ERROR: exploratory_queries.sql not found.")
    raise SystemExit(1)


# ============================================================
# CONNECT DATABASE
# ============================================================

connection = sqlite3.connect(DB_PATH)

connection.execute(
    "PRAGMA foreign_keys = ON"
)


# ============================================================
# READ SQL FILE
# ============================================================

with open(
    SQL_PATH,
    "r",
    encoding="utf-8"
) as file:

    sql = file.read()


# ============================================================
# REMOVE PRAGMA STATEMENTS
# ============================================================

sql_parts = sql.split(";")

queries = []

for part in sql_parts:

    query = part.strip()

    if not query:
        continue

    # Ignore PRAGMA statements
    if query.upper().startswith("PRAGMA"):
        continue

    queries.append(query)


# ============================================================
# RUN QUERIES
# ============================================================

print()
print("=" * 60)
print("DAY 7 - EXPLORATORY SQL QUERIES")
print("=" * 60)


for number, query in enumerate(
    queries,
    start=1
):

    print()
    print("-" * 60)
    print(f"QUERY {number}")
    print("-" * 60)

    try:

        cursor = connection.execute(
            query
        )

        # Get results
        rows = cursor.fetchall()

        # Some SQL statements don't return columns.
        # Protect against cursor.description being None.
        if cursor.description is None:

            print(
                "Query executed successfully."
            )

            continue

        columns = [
            description[0]
            for description in cursor.description
        ]

        print(
            " | ".join(columns)
        )

        print("-" * 60)

        if not rows:

            print(
                "No records found."
            )

        else:

            for row in rows:

                print(
                    " | ".join(
                        str(value)
                        for value in row
                    )
                )

    except sqlite3.Error as error:

        print(
            f"ERROR: {error}"
        )


# ============================================================
# CLOSE DATABASE
# ============================================================

connection.close()


print()
print("=" * 60)
print("EXPLORATORY QUERIES COMPLETED")
print("=" * 60)