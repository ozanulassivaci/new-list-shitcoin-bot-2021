"""
Generates a weekly profit/loss chart from closed positions -- the
"haftalik kazanc grafigi" (weekly earnings graph) step from the original
design, see docs/ALGORITHM.md.
"""
import csv
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import positions

REPORTS_DIR = os.path.join(positions.PROJECT_ROOT, "data", "reports")
WEEKLY_CHART_PATH = os.path.join(REPORTS_DIR, "weekly_pnl.png")

ONE_WEEK_SECONDS = 7 * 24 * 60 * 60


def generate_weekly_chart():
    os.makedirs(REPORTS_DIR, exist_ok=True)

    if not os.path.isfile(positions.SOLD_CSV):
        return None

    cutoff = time.time() - ONE_WEEK_SECONDS
    with open(positions.SOLD_CSV, newline="") as f:
        rows = [row for row in csv.DictReader(f) if float(row["SellTimestamp"]) >= cutoff]

    if not rows:
        return None

    rows.sort(key=lambda row: float(row["SellTimestamp"]))
    names = [row["Name"] for row in rows]

    running_total = 0
    cumulative_pnl = []
    for row in rows:
        usd_spent = float(row["UsdSpent"])
        roi_pct = float(row["RoiPct"])
        running_total += usd_spent * roi_pct / 100
        cumulative_pnl.append(running_total)

    plt.figure(figsize=(10, 5))
    plt.plot(names, cumulative_pnl, marker="o")
    plt.axhline(0, color="gray", linewidth=1)
    plt.ylabel("Cumulative profit/loss (USD)")
    plt.title("Weekly PNL")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(WEEKLY_CHART_PATH)
    plt.close()

    return WEEKLY_CHART_PATH


if __name__ == "__main__":
    generate_weekly_chart()
