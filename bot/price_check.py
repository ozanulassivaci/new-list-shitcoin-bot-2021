"""
Reads a token's current USD price off its bogged.finance chart page.

Factored out of trader.py so both the buyer (to log what it paid) and
seller.py (to decide when to sell) use the same price-reading code.
"""
import time

from selenium.webdriver.common.by import By

BOGGED_CHART_URL = "https://charts.bogged.finance/?c=bsc&t={address}"

SLEEP_SHORT = 2
SLEEP_MEDIUM = 3


def parse_price(text):
    return float(text.replace("$", "").replace(",", "").strip())


def get_token_price(browser, contract_address):
    """Navigate to the token's bogged.finance chart and return its current USD price."""
    browser.get(BOGGED_CHART_URL.format(address=contract_address))
    time.sleep(SLEEP_MEDIUM)

    try:
        browser.find_element(By.XPATH, "//*[@id='WEB3_CONNECT_MODAL_ID']/div/div/div[2]/div[1]/div").click()
    except Exception:
        pass

    time.sleep(SLEEP_SHORT)

    try:
        price_text = browser.find_element(
            By.XPATH, "//*[@id='headlessui-listbox-button-8']/div/div[2]/h4[1]/span"
        ).get_attribute("title")
    except Exception:
        price_text = browser.find_element(
            By.XPATH, "//*[@id='headlessui-listbox-button-8']/div/div[2]/h4[1]"
        ).text

    return parse_price(price_text)
