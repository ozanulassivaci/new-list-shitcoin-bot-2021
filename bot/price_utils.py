"""
USD <-> crypto conversion helper.

Originally an empty stub (usdtoxxx.py, i.e. "USD to XXX"). trader.py
already does a BNB -> USD conversion by scraping valuta.exchange; this
module does the same conversion using Binance's public ticker price
instead, which is more reliable than scraping a third-party website.
"""
from binance_api import get_price


def to_usd(amount, symbol="BNB"):
    """Convert an amount of symbol into its current USDT value."""
    price = get_price(f"{symbol.upper()}USDT")
    return amount * price


def from_usd(usd_amount, symbol="BNB"):
    """Convert a USD amount into an equivalent amount of symbol."""
    price = get_price(f"{symbol.upper()}USDT")
    return usd_amount / price
