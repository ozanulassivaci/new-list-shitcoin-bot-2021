"""
Watches CoinMarketCap's "new" listings page and logs coins that were both
just listed ("... hours ago") and are on the BNB (Binance Smart Chain)
network to a dated CSV file.
"""
import csv
import os
from datetime import date

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

from storage import write_csv, backup_csv

COINMARKETCAP_NEW_URL = "https://coinmarketcap.com/new/"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "new_listings")

SLEEP_AFTER_REFRESH = 10

driver_service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=driver_service)


class GetCapNewListedToday:

    def __init__(self):
        self.option = webdriver.ChromeOptions()
        self.browser = webdriver.Chrome(service=driver_service, options=self.option)
        self.browser.maximize_window()
        self.coinmarketcap_new = COINMARKETCAP_NEW_URL
        self.new_coin_list = []
        self.today_all_coins = []
        self.today_and_binance_list = []
        self.split_coin_names = []
        self.split_coin_name_check_in = ""
        self.docs_name = ""
        self.file_name = DATA_DIR
        self.max_rows_to_check = 30

    def coin2csv(self):
        details = ["#_", "Name", "Short Name", "Price,1h,24h,Market Cap, Volume", "Blockchain", "Added"]
        write_csv(f"{self.file_name}/{self.docs_name}", details, self.today_and_binance_list)

    def copy_csv(self):
        backup_csv(
            f"{self.file_name}/{self.docs_name}",
            f"{self.file_name}/{self.docs_name}.backup.csv",
        )

    def go2Cap(self):
        self.browser.get(self.coinmarketcap_new)
        time.sleep(5)

        self.docs_name = "today_and_binance_list_token" + f"{date.today()}" + ".csv"
        if not os.path.isfile(f"{self.file_name}/{self.docs_name}"):
            GetCapNewListedToday.coin2csv(self)

        coin_list = self.browser.find_element(By.XPATH, "//*[@id='__next']/div[1]/div[1]/div[2]/div/div[2]/table/tbody")
        list_today = coin_list.find_elements(By.TAG_NAME, "tr")

        for coins in list_today:
            coin_names = coins.text
            self.split_coin_names.append(coin_names)
            self.split_coin_names = self.split_coin_names[0].split('\n')
            self.split_coin_name_check_in = self.split_coin_names[1]

            if not any(f"{self.split_coin_name_check_in}" in word for word in self.new_coin_list):
                self.new_coin_list.append(coin_names)

            self.split_coin_names.clear()

        x = range(0, self.max_rows_to_check)

        for n in x:
            try:
                try:
                    all_coins = self.new_coin_list[n].split("\n")
                    if all_coins not in self.today_all_coins:
                        self.today_all_coins.append(all_coins)
                except IndexError:
                    self.max_rows_to_check = self.max_rows_to_check - 2
            except Exception:
                pass

        x = range(0, self.max_rows_to_check)

        for n in x:
            if_today_and_binance_coin = self.today_all_coins[n]
            if_today_and_binance_coin_names = if_today_and_binance_coin[1]

            # only keep coins listed a few hours ago and running on the BNB chain
            if any("hours" in word for word in if_today_and_binance_coin) and any("BNB" in word for word in if_today_and_binance_coin):
                if if_today_and_binance_coin not in self.today_and_binance_list:
                    self.today_and_binance_list.append(if_today_and_binance_coin)

                    with open(f"{self.file_name}/{self.docs_name}", newline='') as f:
                        reader = csv.reader(f)
                        csv_to_list = list(reader)

                    already_saved = any(if_today_and_binance_coin_names in sublist for sublist in csv_to_list)
                    if not already_saved:
                        with open(f"{self.file_name}/{self.docs_name}", "a", newline="") as f:
                            csv.writer(f).writerow(if_today_and_binance_coin)

        self.browser.refresh()
        self.copy_csv()
        self.browser.quit()
        time.sleep(SLEEP_AFTER_REFRESH)


if __name__ == "__main__":
    while True:
        gcnlt = GetCapNewListedToday()
        gcnlt.go2Cap()
