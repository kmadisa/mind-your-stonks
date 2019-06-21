import time

from selenium import webdriver 
from selenium.webdriver.common.keys import Keys


# How to get the account balance.
driver = webdriver.Firefox()
driver.get("https://www.bet.co.za")
driver.close()