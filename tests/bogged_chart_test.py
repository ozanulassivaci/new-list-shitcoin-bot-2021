"""Ad-hoc smoke test: open a token's bogged.finance chart and read its price."""
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# example token contract address, used only to exercise the chart page
BOGGED_CHART_URL = "https://charts.bogged.finance/?c=bsc&t=0xD74b782E05AA25c50e7330Af541d46E18f36661C"

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "new_listings")

driver_service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=driver_service)


class GetCapNewListedToday:

    def __init__(self):
        self.option = webdriver.ChromeOptions()
        self.browser = webdriver.Chrome(service=driver_service, options=self.option)
        self.browser.maximize_window()
        self.file_name = DATA_DIR
        self.bogged = BOGGED_CHART_URL

    def go2Cap(self):
        self.browser.get(self.bogged)
        time.sleep(5)
        try:
            self.browser.find_element(By.XPATH, "//*[@id='WEB3_CONNECT_MODAL_ID']/div/div/div[1]").click()
        except Exception:
            pass
        time.sleep(3)
        price = self.browser.find_element(By.XPATH, "//*[@id='headlessui-listbox-button-8']/div/div[2]/h4[1]/span").get_attribute("title")
        print(price)


if __name__ == "__main__":
    gcnlt = GetCapNewListedToday()
    gcnlt.go2Cap()
