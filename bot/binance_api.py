"""
Small wrapper around Binance's public REST API.

Originally an empty stub (binance.py). Every CSV the scraper produces is
named "today_and_binance_list_token...", which suggests the original plan
was to cross-check newly listed coins against Binance's own listings, but
that part was never written. This fills that gap with a minimal, read-only
client. It only reads public market data, so no API key or secret is
needed for anything here.

Not wired into the scraper/trader loop, to avoid changing existing
behaviour; use it as a building block if that cross-check is added later.
"""
import requests

BASE_URL = "https://api.binance.com"


def get_all_symbols():
    """Return every trading pair symbol currently listed on Binance."""
    response = requests.get(f"{BASE_URL}/api/v3/exchangeInfo", timeout=10)
    response.raise_for_status()
    return [item["symbol"] for item in response.json()["symbols"]]


def is_listed_on_binance(base_asset, quote_asset="USDT"):
    """Check whether base_asset/quote_asset (e.g. "BNB"/"USDT") trades on Binance."""
    symbol = f"{base_asset.upper()}{quote_asset.upper()}"
    return symbol in get_all_symbols()


def get_price(symbol):
    """Return the latest traded price for a Binance symbol, e.g. "BNBUSDT"."""
    response = requests.get(f"{BASE_URL}/api/v3/ticker/price", params={"symbol": symbol.upper()}, timeout=10)
    response.raise_for_status()
    return float(response.json()["price"])
