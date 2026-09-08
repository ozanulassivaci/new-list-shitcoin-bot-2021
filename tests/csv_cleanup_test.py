"""Ad-hoc smoke test: load bought_coins.csv and drop columns not needed for review."""
import os

import pandas as pd

BOUGHT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "bought")
BOUGHT_COINS_CSV = "bought_coins.csv"

df = pd.read_csv(f"{BOUGHT_DIR}/{BOUGHT_COINS_CSV}", on_bad_lines="skip")
print(df.columns)
print("original data:\n")
print(df)

# columns: #_,Name,Short Name,Address,Buy Value,Sell Value,"Price,1h,24h,Market Cap, Volume",Blockchain,Added
try:
    df = df.drop('#_', inplace=True, axis=1)
    df = df.drop('Price', inplace=True, axis=1)
    df = df.drop('Blockchain', inplace=True, axis=1)
    df = df.drop('Added', inplace=True, axis=1)
except Exception:
    pass

print("\ndata after dropping columns:\n")
print(df)
