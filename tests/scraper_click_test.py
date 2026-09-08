"""
Ad-hoc smoke test: opens the CoinMarketCap "new" page and tries to click a
coin by its visible name. Used while developing the scraper's row-clicking
logic, not part of an automated test suite.
"""
import os
import time
from datetime import date

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

COINMARKETCAP_NEW_URL = "https://coinmarketcap.com/new/"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "new_listings")

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

    def go2Cap(self):
        self.browser.get(self.coinmarketcap_new)
        time.sleep(5)

        coin_list = self.browser.find_element(By.XPATH, "//*[@id='__next']/div[1]/div[1]/div[2]/div/div[2]/table/tbody")
        coin_list.find_elements(By.TAG_NAME, "tr")

        # example: click a coin found by its visible name
        matches = self.browser.find_elements(By.XPATH, "//*[contains(text(), 'League of Zodiacs')]")
        print(matches)
        matches[0].click()


if __name__ == "__main__":
    gcnlt = GetCapNewListedToday()
    gcnlt.go2Cap()
