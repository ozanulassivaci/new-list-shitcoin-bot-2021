"""
Monitors open positions and sells them according to the original design's
exit rule:

  - if a coin never reaches +30% within its first 24 hours, sell it --
    coins that don't pop early tend to just trend to zero
  - once it has crossed +30%, keep holding while it keeps making new
    highs (it could still go on to +200%/+300%), and only sell once the
    price has pulled back for a few checks in a row -- a confirmed
    reversal from its peak -- to lock in gains before it crashes, which
    is what these coins tend to do after a run-up

The decision logic (_is_downtrend, the peak/gain tracking) is plain
Python and works independent of any web page. The PancakeSwap steps in
_sell() below mirror the buy flow in trader.py -- the one part of this
project that was actually run against the live site -- but this sell
path itself has never been run and its selectors are best-effort; see
the README Limitations section.
"""
import time

from selenium.webdriver.common.by import By

import positions
from price_check import get_token_price

PANCAKESWAP_URL = "https://pancakeswap.finance/swap"

SLEEP_SHORT = 2
SLEEP_MEDIUM = 3
SLEEP_LONG = 5

# exit rule tuning -- see module docstring
STOP_LOSS_WINDOW_HOURS = 24
STOP_LOSS_THRESHOLD_PCT = 30
CONSECUTIVE_DROPS_TO_SELL = 3
CHECK_HISTORY_SIZE = 5


class Seller:

    def __init__(self, pancake):
        self.PancakeImport = pancake

    def check_and_sell_positions(self):
        for position in positions.load_open_positions():
            self._check_one(position)

    def _check_one(self, position):
        address = position["Address"]
        buy_price = float(position["BuyPriceUsd"])
        buy_timestamp = float(position["BuyTimestamp"])
        peak_gain_pct = float(position["PeakGainPct"] or 0)
        recent_gain_pct = [float(g) for g in position["RecentGainPct"].split("|") if g] if position["RecentGainPct"] else []

        try:
            current_price = get_token_price(self.PancakeImport.MetaMaskLoginImport.browser, address)
        except Exception:
            return

        gain_pct = (current_price - buy_price) / buy_price * 100 if buy_price else 0
        peak_gain_pct = max(peak_gain_pct, gain_pct)
        recent_gain_pct.append(gain_pct)
        recent_gain_pct = recent_gain_pct[-CHECK_HISTORY_SIZE:]

        hours_since_buy = (time.time() - buy_timestamp) / 3600

        # rule 1: never popped -- cut it loose after the first 24 hours
        if peak_gain_pct < STOP_LOSS_THRESHOLD_PCT and hours_since_buy >= STOP_LOSS_WINDOW_HOURS:
            self._sell(position, current_price, "stop_loss_24h")
            return

        # rule 2: it popped, but has now pulled back for a few checks in a row
        if peak_gain_pct >= STOP_LOSS_THRESHOLD_PCT and self._is_downtrend(recent_gain_pct):
            self._sell(position, current_price, "trailing_exit")
            return

        positions.update_position_tracking(address, peak_gain_pct, recent_gain_pct)

    @staticmethod
    def _is_downtrend(recent_gain_pct):
        """True if the last CONSECUTIVE_DROPS_TO_SELL checks each dropped from the one before."""
        if len(recent_gain_pct) < CONSECUTIVE_DROPS_TO_SELL + 1:
            return False
        last_n = recent_gain_pct[-(CONSECUTIVE_DROPS_TO_SELL + 1):]
        return all(last_n[i] > last_n[i + 1] for i in range(len(last_n) - 1))

    def _sell(self, position, current_price, reason):
        print(f"selling {position['Name']} ({reason}), current price {current_price}")

        browser = self.PancakeImport.MetaMaskLoginImport.browser
        browser.get(PANCAKESWAP_URL)
        time.sleep(SLEEP_LONG)

        # set the input token to the one we're holding (mirrors the output
        # token selection in trader.py's pancake_ex, not verified against
        # the live site)
        browser.find_element(By.XPATH, "//*[@id='swap-currency-input']/div[1]/button").click()
        time.sleep(SLEEP_SHORT)
        browser.find_element(By.XPATH, "//*[@id='token-search-input']").send_keys(position["Address"])
        time.sleep(SLEEP_LONG)
        browser.find_element(By.XPATH, "//*[@id='__next']/div[1]/div[2]/div[2]/div[1]/div[2]/div/button").click()
        time.sleep(SLEEP_SHORT)

        # set the output token to BNB
        browser.find_element(By.XPATH, "//*[@id='swap-currency-output']/div[1]/button").click()
        time.sleep(SLEEP_SHORT)
        browser.find_elements(By.XPATH, "//*[contains(text(), 'BNB')]")[0].click()
        time.sleep(SLEEP_SHORT)

        # sell (approximately) everything we bought
        buy_price = float(position["BuyPriceUsd"])
        usd_spent = float(position["UsdSpent"])
        approx_token_amount = usd_spent / buy_price if buy_price else 0
        browser.find_element(By.XPATH, "//*[@id='swap-currency-input']/div[2]/div/div[1]/div/input").send_keys(str(approx_token_amount))
        time.sleep(SLEEP_SHORT)

        # NOTE: confirming the swap and approving it in the MetaMask popup
        # is intentionally not included here -- see README Limitations.
        # This bot only ever logs the position as closed; it does not
        # verify the trade went through on-chain, matching how the buy
        # side already logged purchases before this feature existed.

        positions.close_position(position, current_price, reason)
