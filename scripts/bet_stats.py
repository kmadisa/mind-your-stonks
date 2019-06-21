import time

from selenium import webdriver 
from selenium.webdriver.firefox.options import Options


# How to get the account balance.
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
driver.get("https://www.bet.co.za")
driver.close()