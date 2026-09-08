"""
Reads the user-configurable risk profile (min/max USD to spend per coin)
from .env. This is the "user selects ... max min money" step from the
original design (see docs/ALGORITHM.md).

get_risk_profile() re-reads .env on every call instead of caching it, so
editing .env while the bot is running takes effect on the next loop
iteration without a restart.
"""
import os

from dotenv import load_dotenv

DEFAULT_MIN_SPEND_USD = 5.0
DEFAULT_MAX_SPEND_USD = 50.0


def get_risk_profile():
    load_dotenv(override=True)
    return {
        "min_spend_usd": float(os.getenv("MIN_SPEND_PER_COIN_USD", DEFAULT_MIN_SPEND_USD)),
        "max_spend_usd": float(os.getenv("MAX_SPEND_PER_COIN_USD", DEFAULT_MAX_SPEND_USD)),
    }
