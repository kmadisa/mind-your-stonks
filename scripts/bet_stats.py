import time

from selenium import webdriver 
from selenium.webdriver.common.keys import Keys


# How to get the account balance.
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
driver.get("https://www.bet.co.za")
driver.close()