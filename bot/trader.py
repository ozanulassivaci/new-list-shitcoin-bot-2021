"""
Main trading loop: reads coins found by scraper.py, buys the ones that
have not been bought yet on PancakeSwap, and logs the result.
"""
import csv
import os
import time

import pyperclip as pc

import positions
import risk_config
from pancake_dex import Pancake
from price_check import get_token_price
from price_utils import from_usd, to_usd
from storage import append_csv_row, backup_csv
from selenium.webdriver.common.by import By

PANCAKESWAP_URL = "https://pancakeswap.finance/swap"
COINMARKETCAP_NEW_URL = "https://coinmarketcap.com/new/"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEW_LISTINGS_DIR = os.path.join(PROJECT_ROOT, "data", "new_listings")
BOUGHT_DIR = os.path.join(PROJECT_ROOT, "data", "bought")

BOUGHT_COINS_CSV = "bought_coins.csv"
BOUGHT_TOKEN_CSV = "bought_token.csv"

SLEEP_SHORT = 2
SLEEP_MEDIUM = 3
SLEEP_LONG = 5
SLEEP_LONGER = 10


class Swap:

    def __init__(self):
        self.PancakeImport = Pancake()
        self.pancake_exchange = PANCAKESWAP_URL
        self.new_list_docs_name = ""
        self.new_list_file_name = NEW_LISTINGS_DIR
        self.bought_csv_file_path = BOUGHT_DIR
        self.bought_csv_docs_name = BOUGHT_COINS_CSV
        self.bought_csv_token_name = BOUGHT_TOKEN_CSV
        self.today_coin_names_csv_list = []
        self.bought_coin_names_csv = []
        self.coinmarketcap_new = COINMARKETCAP_NEW_URL
        self.usd = 0
        self.coin_value = 0
        self.current_token_name = ""
        self.append_token_values_bought_token_csv = []

    # Walk today's new-listing CSV and Binance's bought-coin CSV in order.
    # Any coin that is not already in the bought list gets bought, then
    # gets appended to the bought list.

    def pancake_py(self):
        self.PancakeImport.pancake_connect()
        self.PancakeImport.PancakeSwapSettings()

    def copy_csv(self):
        backup_csv(
            f"{self.bought_csv_file_path}/{self.bought_csv_docs_name}",
            f"{self.bought_csv_file_path}/{self.bought_csv_docs_name}.backup.csv",
        )

    def read_today_and_binance_list_token_today(self):
        # coins already bought
        for col in csv.DictReader(open(f"{self.bought_csv_file_path}/{self.bought_csv_docs_name}", 'r')):
            if not any(f"{col['Name']}" in word for word in self.bought_coin_names_csv):
                self.bought_coin_names_csv.append(col["Name"])

        # coins to buy
        # TODO: this date is hardcoded for now, should track the current day's file
        self.docs_name = "today_and_binance_list_token" + "2022-02-02" + ".csv"

        for col in csv.DictReader(open(f"{self.new_list_file_name}/{self.docs_name}", 'r')):
            if not any(f"{col['Name']}" in word for word in self.today_coin_names_csv_list):
                if not any(f"{col['Name']}" in word for word in self.bought_coin_names_csv):
                    self.today_coin_names_csv_list.append(col["Name"])

    def buy_tokens(self):
        for search_and_buy_this_token in self.today_coin_names_csv_list:
            self.current_token_name = search_and_buy_this_token
            self.append_token_values_bought_token_csv.append(search_and_buy_this_token)

            self.PancakeImport.MetaMaskLoginImport.browser.get(self.coinmarketcap_new)
            time.sleep(SLEEP_MEDIUM)
            self.PancakeImport.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='cmc-cookie-policy-banner']/div[2]").click()
            time.sleep(SLEEP_MEDIUM)
            try:
                try:
                    self.PancakeImport.MetaMaskLoginImport.browser.find_elements(By.XPATH, f"//*[contains(text(), '{search_and_buy_this_token}')]")[0].click()
                except Exception:
                    self.PancakeImport.MetaMaskLoginImport.browser.find_elements(By.XPATH, f"//*[contains(text(), '{search_and_buy_this_token}')]")[0].click()
            except Exception:
                pass

            time.sleep(SLEEP_LONGER)
            self.PancakeImport.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='__next']/div/div[1]/div[2]/div/div[1]/div[2]/div/div[5]/div/div[3]/div[2]/div/div[1]").click()

            Swap.pancake_ex(self)

            self.today_coin_names_csv_list.remove(f"{search_and_buy_this_token}")

            with open(f"{self.new_list_file_name}/{self.docs_name}") as file_obj:
                reader_obj = csv.reader(file_obj)
                for row in reader_obj:
                    if any(f"{search_and_buy_this_token}" in word for word in row):
                        append_csv_row(f"{self.bought_csv_file_path}/{self.bought_csv_docs_name}", row)
                        self.copy_csv()

    def size_and_enter_position(self):
        """
        Split the available BNB evenly across the coins queued for this run,
        clamp it to the configured risk profile (MIN/MAX_SPEND_PER_COIN_USD,
        see bot/risk_config.py), and type the resulting amount into the swap
        input box. The clamping and the USD<->BNB conversion are new; the
        even-split-then-read-the-input-box part is the original design, but
        the result was never actually entered into the input box before --
        the original bot always bought whatever amount happened to already
        be sitting in that field.
        """
        self.PancakeImport.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='swap-currency-input']/div[2]/div/div[2]/button").click()
        time.sleep(SLEEP_SHORT)

        time.sleep(15)

        bnb_input = self.PancakeImport.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='swap-currency-input']/div[2]/div/div[1]/div/input")
        available_bnb = float(bnb_input.get_attribute("value"))
        will_buy_coins_len = len(self.today_coin_names_csv_list)
        even_share_bnb = available_bnb / float(will_buy_coins_len)

        profile = risk_config.get_risk_profile()
        even_share_usd = to_usd(even_share_bnb, "BNB")
        usd_to_spend = max(profile["min_spend_usd"], min(profile["max_spend_usd"], even_share_usd))
        self.usd = usd_to_spend
        self.append_token_values_bought_token_csv.append(self.usd)

        if usd_to_spend < 1.0:
            self.today_coin_names_csv_list.clear()
            return

        bnb_to_spend = from_usd(usd_to_spend, "BNB")
        bnb_input.clear()
        bnb_input.send_keys(str(bnb_to_spend))
        time.sleep(SLEEP_SHORT)

    def pancake_ex(self):
        self.PancakeImport.MetaMaskLoginImport.browser.get(self.pancake_exchange)
        time.sleep(SLEEP_LONG)

        # find and select the token by contract address
        self.PancakeImport.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='swap-currency-output']/div[1]/button").click()
        time.sleep(SLEEP_SHORT)
        new_list_token_binance_smart_contract = pc.paste()
        self.PancakeImport.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='token-search-input']").send_keys(new_list_token_binance_smart_contract)

        time.sleep(SLEEP_LONGER)
        # import token
        self.PancakeImport.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='__next']/div[1]/div[2]/div[2]/div[1]/div[2]/div/button").click()
        time.sleep(SLEEP_SHORT)
        # acknowledge the risk disclaimer
        self.PancakeImport.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='__next']/div[1]/div[2]/div[2]/div/div[3]/div/input").click()
        time.sleep(SLEEP_SHORT)
        self.PancakeImport.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='__next']/div[1]/div[2]/div[2]/div/div[3]/button").click()
        time.sleep(SLEEP_LONG)

        # figure out how much to spend and enter it, now that the token is selected
        self.size_and_enter_position()

        # watch the coin's chart after buying and record what we paid
        try:
            self.coin_value = get_token_price(self.PancakeImport.MetaMaskLoginImport.browser, new_list_token_binance_smart_contract)
        except Exception:
            self.coin_value = 0

        self.append_token_values_bought_token_csv.append(self.coin_value)
        append_csv_row(f"{self.bought_csv_file_path}/{self.bought_csv_token_name}", self.append_token_values_bought_token_csv)

        if self.coin_value:
            positions.add_position(self.current_token_name, new_list_token_binance_smart_contract, self.coin_value, self.usd)


if __name__ == "__main__":
    import pnl_graph
    from seller import Seller

    cap = Swap()
    # manual step-by-step alternative to metamask_py(), kept for reference:
    # cap.PancakeImport.MetaMaskLoginImport.MetaMask()
    # cap.PancakeImport.MetaMaskLoginImport.loginMeta()
    # cap.PancakeImport.MetaMaskLoginImport.add_bnb_chain()
    cap.PancakeImport.metamask_py()
    cap.pancake_py()

    # positions.csv / sold.csv already hold whatever was bought and not yet
    # sold from a previous run, so this resumes monitoring them automatically
    seller = Seller(cap.PancakeImport)

    while True:
        cap.read_today_and_binance_list_token_today()
        cap.buy_tokens()
        seller.check_and_sell_positions()
        pnl_graph.generate_weekly_chart()
