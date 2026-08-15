import sqlite3
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DB_PATH = PROJECT_ROOT / "nifty100.db"

SCHEMA_PATH = PROJECT_ROOT / "db" / "schema.sql"


# ============================================================
# CHECK SCHEMA FILE
# ============================================================

if not SCHEMA_PATH.exists():

    print("ERROR: schema.sql was not found.")

    print(
        f"Expected location: {SCHEMA_PATH}"
    )

    raise SystemExit(1)


# ============================================================
# CREATE DATABASE
# ============================================================

print()
print("=" * 60)
print("CREATING NIFTY100 DATABASE")
print("=" * 60)

print(
    f"Schema: {SCHEMA_PATH}"
)

print(
    f"Database: {DB_PATH}"
)


# Connect to SQLite
connection = sqlite3.connect(DB_PATH)


# Enable foreign keys
connection.execute(
    "PRAGMA foreign_keys = ON"
)


# ============================================================
# READ SCHEMA
# ============================================================

with open(
    SCHEMA_PATH,
    "r",
    encoding="utf-8"
) as file:

    schema = file.read()


# ============================================================
# EXECUTE SCHEMA
# ============================================================

try:

    connection.executescript(schema)

    connection.commit()

    print()
    print("Schema executed successfully.")

except sqlite3.Error as error:

    print()
    print("ERROR while creating database:")
    print(error)

    connection.rollback()
    connection.close()

    raise SystemExit(1)


# ============================================================
# CHECK FOREIGN KEYS
# ============================================================

cursor = connection.cursor()

cursor.execute(
    "PRAGMA foreign_keys;"
)

foreign_keys = cursor.fetchone()[0]

print(
    f"Foreign keys enabled: {foreign_keys}"
)


# ============================================================
# LIST TABLES
# ============================================================

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name;
""")

tables = cursor.fetchall()


print()
print("Tables created:")
print("-" * 40)

for table in tables:

    print(
        f"- {table[0]}"
    )


# ============================================================
# TABLE COUNT
# ============================================================

print()
print(
    f"Total tables: {len(tables)}"
)


# ============================================================
# CLOSE DATABASE
# ============================================================

connection.close()


print()
print("=" * 60)
print("DATABASE CREATION COMPLETED")
print("=" * 60)

print(
    f"Database saved at:\n{DB_PATH}"
)

print()