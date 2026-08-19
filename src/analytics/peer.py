import sqlite3
from pathlib import Path
import pandas as pd

# --------------------------------------------------
# PATHS
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "nifty100.db"
PEER_FILE = PROJECT_ROOT / "data" / "raw" / "peer_groups.xlsx"

# --------------------------------------------------
# LOAD FILES
# --------------------------------------------------
peer_df = pd.read_excel(PEER_FILE)

conn = sqlite3.connect(DB_PATH)
ratio_df = pd.read_sql("SELECT * FROM financial_ratios", conn)

# --------------------------------------------------
# STANDARDISE COLUMN NAMES
# --------------------------------------------------
peer_df.columns = (
    peer_df.columns.str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# Expected columns:
# company_id , peer_group_name

merged = ratio_df.merge(
    peer_df,
    on="company_id",
    how="left"
)

# --------------------------------------------------
# METRICS
# --------------------------------------------------
metrics = {
    "return_on_equity_pct": False,
    "return_on_capital_employed_pct": False,
    "net_profit_margin_pct": False,
    "debt_to_equity": True,
    "free_cash_flow_cr": False,
    "pat_cagr_5yr": False,
    "revenue_cagr_5yr": False,
    "eps_cagr_5yr": False,
    "interest_coverage": False,
    "asset_turnover": False,
}

rows = []

for group_name, group in merged.groupby("peer_group_name"):

    for metric, inverse in metrics.items():

        if metric not in group.columns:
            continue

        values = pd.to_numeric(group[metric], errors="coerce")

        ranks = values.rank(pct=True)

        if inverse:
            ranks = 1 - ranks

        for i in group.index:

            if pd.isna(group.loc[i, metric]):
                continue

            rows.append(
                {
                    "company_id": group.loc[i, "company_id"],
                    "peer_group_name": group_name,
                    "metric": metric,
                    "value": group.loc[i, metric],
                    "percentile_rank": round(
                        ranks.loc[i] * 100,
                        2
                    ),
                    "year": group.loc[i, "year"],
                }
            )

peer_percentiles = pd.DataFrame(rows)

# --------------------------------------------------
# SAVE SQLITE
# --------------------------------------------------
peer_percentiles.to_sql(
    "peer_percentiles",
    conn,
    if_exists="replace",
    index=False,
)

conn.commit()

print("=" * 50)
print("DAY 18 COMPLETED")
print("=" * 50)
print("Rows:", len(peer_percentiles))
print(
    "Peer Groups:",
    peer_percentiles["peer_group_name"].nunique()
)

conn.close()