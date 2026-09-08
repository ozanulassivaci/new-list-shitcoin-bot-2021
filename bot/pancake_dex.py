"""
Connects the unlocked MetaMask wallet to PancakeSwap and applies the
bot's slippage setting.
"""
import time

from selenium.webdriver.common.by import By

from metamask_wallet import MetaMaskLogin

PANCAKESWAP_URL = "https://pancakeswap.finance/swap"
SLIPPAGE_TOLERANCE = "13"

SLEEP_SHORT = 3
SLEEP_MEDIUM = 4
SLEEP_LONG = 6


class Pancake:

    def __init__(self):
        self.MetaMaskLoginImport = MetaMaskLogin()
        self.pancake_exchange = PANCAKESWAP_URL
        self.Slippage_Tolerance = SLIPPAGE_TOLERANCE

    def metamask_py(self):
        self.MetaMaskLoginImport.MetaMask()
        self.MetaMaskLoginImport.loginMeta()
        self.MetaMaskLoginImport.add_bnb_chain()

    def pancake_connect(self):
        self.MetaMaskLoginImport.browser.get(self.pancake_exchange)
        time.sleep(SLEEP_MEDIUM)

        # connect wallet
        self.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='__next']/div[1]/div[1]/nav/div[2]/button").click()
        time.sleep(SLEEP_SHORT)
        self.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='wallet-connect-metamask']").click()
        time.sleep(SLEEP_SHORT)

        # approve the connection in the MetaMask popup
        switch_to_metamask = self.MetaMaskLoginImport.browser.window_handles
        self.MetaMaskLoginImport.browser.switch_to.window(switch_to_metamask[1])
        self.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='app-content']/div/div[2]/div/div[2]/div[4]/div[2]/button[2]").click()
        time.sleep(SLEEP_MEDIUM)
        self.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='app-content']/div/div[2]/div/div[2]/div[2]/div[2]/footer/button[2]").click()
        self.MetaMaskLoginImport.browser.switch_to.window(switch_to_metamask[0])
        time.sleep(SLEEP_MEDIUM)

    def PancakeSwapSettings(self):
        time.sleep(SLEEP_MEDIUM)
        self.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='__next']/div[1]/div[3]/div/div[1]/div[1]/div[2]/div/div/div/div/div[1]/div/button").click()
        time.sleep(SLEEP_SHORT)
        self.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='open-settings-dialog-button']").click()
        time.sleep(SLEEP_SHORT)
        self.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='__next']/div[1]/div[2]/div[2]/div/div[1]/div[3]/div[2]/button[3]").click()
        time.sleep(SLEEP_SHORT)
        self.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='__next']/div[1]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[2]/div/div[1]/input").send_keys(self.Slippage_Tolerance)
        time.sleep(SLEEP_SHORT)
        self.MetaMaskLoginImport.browser.find_element(By.XPATH, "//*[@id='__next']/div[1]/div[2]/div[1]/button").click()
        time.sleep(SLEEP_SHORT)


if __name__ == "__main__":
    cap = Pancake()
    cap.metamask_py()
    cap.pancake_connect()
