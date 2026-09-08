"""
Tracks coins the bot currently holds, in CSV files under data/, so
trader.py (buying) and seller.py (selling) share the same state and it
survives a restart -- this is the "check save data and load previous coin
data" step from the original design (see docs/ALGORITHM.md): since the
state already lives on disk, resuming just means reading these files
again, which load_open_positions() does on every call.

data/bought/positions.csv holds one row per coin bought.
data/sold/sold.csv holds one row per coin sold, keyed by Address.
A position is "open" if its Address is not yet in sold.csv.
"""
import csv
import os
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSITIONS_CSV = os.path.join(PROJECT_ROOT, "data", "bought", "positions.csv")
SOLD_CSV = os.path.join(PROJECT_ROOT, "data", "sold", "sold.csv")

POSITIONS_HEADER = ["Name", "Address", "BuyPriceUsd", "UsdSpent", "BuyTimestamp", "PeakGainPct", "RecentGainPct"]
SOLD_HEADER = ["Name", "Address", "BuyPriceUsd", "SellPriceUsd", "UsdSpent", "RoiPct", "SellReason", "BuyTimestamp", "SellTimestamp"]


def _ensure_file(path, header):
    if not os.path.isfile(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="") as f:
            csv.writer(f).writerow(header)


def add_position(name, address, buy_price_usd, usd_spent):
    _ensure_file(POSITIONS_CSV, POSITIONS_HEADER)
    with open(POSITIONS_CSV, "a", newline="") as f:
        csv.writer(f).writerow([name, address, buy_price_usd, usd_spent, time.time(), 0, ""])


def load_open_positions():
    """Return every position that has been bought but not yet sold."""
    _ensure_file(POSITIONS_CSV, POSITIONS_HEADER)
    _ensure_file(SOLD_CSV, SOLD_HEADER)

    with open(SOLD_CSV, newline="") as f:
        sold_addresses = {row["Address"] for row in csv.DictReader(f)}

    with open(POSITIONS_CSV, newline="") as f:
        return [row for row in csv.DictReader(f) if row["Address"] not in sold_addresses]


def load_sold_positions():
    """Return every closed position, most recently sold last."""
    _ensure_file(SOLD_CSV, SOLD_HEADER)
    with open(SOLD_CSV, newline="") as f:
        return list(csv.DictReader(f))


def update_position_tracking(address, peak_gain_pct, recent_gain_pct_history):
    """Rewrite positions.csv with the latest peak/recent gain values for one address."""
    _ensure_file(POSITIONS_CSV, POSITIONS_HEADER)
    with open(POSITIONS_CSV, newline="") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        if row["Address"] == address:
            row["PeakGainPct"] = peak_gain_pct
            row["RecentGainPct"] = "|".join(str(g) for g in recent_gain_pct_history)

    with open(POSITIONS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=POSITIONS_HEADER)
        writer.writeheader()
        writer.writerows(rows)


def close_position(position, sell_price_usd, reason):
    _ensure_file(SOLD_CSV, SOLD_HEADER)
    buy_price = float(position["BuyPriceUsd"])
    roi_pct = (sell_price_usd - buy_price) / buy_price * 100 if buy_price else 0
    with open(SOLD_CSV, "a", newline="") as f:
        csv.writer(f).writerow([
            position["Name"], position["Address"], buy_price, sell_price_usd,
            position["UsdSpent"], roi_pct, reason, position["BuyTimestamp"], time.time(),
        ])
