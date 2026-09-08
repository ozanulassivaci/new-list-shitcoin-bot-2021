"""
Drives the MetaMask browser extension through Selenium: unlocks the
wallet and adds the BNB (Binance Smart Chain) network.
"""
import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

URL_METAMASK_HOME = "chrome-extension://n/home.html"
URL_ADD_CHAIN = "chrome-extension://n/home.html#settings/networks/add-network"

METAMASK_PASSWORD = os.getenv("METAMASK_PASSWORD", "")
METAMASK_SEED_PHRASE = os.getenv("METAMASK_SEED_PHRASE", "")

SLEEP_SHORT = 2
SLEEP_MEDIUM = 3
SLEEP_LONG = 5


class MetaMaskLogin:

    def __init__(self):
        self.option = webdriver.ChromeOptions()
        self.option.add_extension(os.path.join(os.path.dirname(__file__), "metamask_10_8_1_0.crx"))
        self.browser = webdriver.Chrome(ChromeDriverManager().install(), options=self.option)
        self.browser.maximize_window()
        self.urlMM = URL_METAMASK_HOME
        self.urladdchain = URL_ADD_CHAIN
        self.metamaskPass = METAMASK_PASSWORD
        self.metamaskWords = METAMASK_SEED_PHRASE

    def MetaMask(self):
        self.browser.get(self.urlMM)
        time.sleep(SLEEP_SHORT)

        # MetaMask opens two windows on first launch; close the extra one
        handles = self.browser.window_handles
        self.browser.switch_to.window(handles[0])
        self.browser.close()
        self.browser.switch_to.window(handles[1])
        time.sleep(SLEEP_SHORT)

        self.browser.find_element(By.XPATH, "//*[@id='app-content']/div/div[2]/div/div/div/button").click()
        time.sleep(SLEEP_SHORT)
        self.browser.find_element(By.XPATH, "//*[@id='app-content']/div/div[2]/div/div/div[2]/div/div[2]/div[1]/button").click()
        time.sleep(SLEEP_SHORT)
        self.browser.find_element(By.XPATH, "//*[@id='app-content']/div/div[2]/div/div/div/div[5]/div[1]/footer/button[1]").click()
        time.sleep(SLEEP_SHORT)

    def loginMeta(self):
        self.browser.find_element(By.XPATH, "//*[@id='app-content']/div/div[2]/div/div/form/div[4]/div[1]/div").click()
        time.sleep(SLEEP_SHORT)
        self.browser.find_element(By.XPATH, "//*[@id='app-content']/div/div[2]/div/div/form/div[4]/div[1]/div/input").send_keys(self.metamaskWords)
        self.browser.find_element(By.XPATH, "//*[@id='password']").send_keys(self.metamaskPass)
        self.browser.find_element(By.XPATH, "//*[@id='confirm-password']").send_keys(self.metamaskPass)
        self.browser.find_element(By.XPATH, "//*[@id='app-content']/div/div[2]/div/div/form/div[7]/div").click()
        time.sleep(SLEEP_SHORT)
        self.browser.find_element(By.XPATH, "//*[@id='app-content']/div/div[2]/div/div/form/button").click()
        time.sleep(SLEEP_LONG)
        self.browser.find_element(By.XPATH, "//*[@id='app-content']/div/div[2]/div/div/button").click()
        time.sleep(SLEEP_SHORT)
        self.browser.find_element(By.XPATH, "//*[@id='popover-content']/div/div/section/header/div/button").click()
        time.sleep(SLEEP_SHORT)

    def add_bnb_chain(self):
        network_name = "Binance Smart Chain"
        new_rpc_url = "https://bsc-dataseed.binance.org/"
        chainid = "56"
        symbol = "BNB"
        block_explorer_url = "https://bscscan.com"

        self.browser.get(self.urladdchain)
        time.sleep(SLEEP_SHORT)

        self.browser.find_element(By.XPATH, "//*[@id='app-content']/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[1]/label/input").send_keys(network_name)
        self.browser.find_element(By.XPATH, "//*[@id='app-content']/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[3]/label/input").send_keys(chainid)
        self.browser.find_element(By.XPATH, "//*[@id='app-content']/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/label/input").send_keys(new_rpc_url)
        self.browser.find_element(By.XPATH, "//*[@id='app-content']/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[4]/label/input").send_keys(symbol)
        self.browser.find_element(By.XPATH, "//*[@id='app-content']/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[5]/label/input").send_keys(block_explorer_url)
        time.sleep(SLEEP_SHORT)
        self.browser.find_element(By.XPATH, "//*[@id='app-content']/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[3]/button[2]").click()
        time.sleep(SLEEP_SHORT)
