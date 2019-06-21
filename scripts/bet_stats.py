import argparse
import time

from selenium import webdriver 
from selenium.webdriver.firefox.options import Options


parser = argparse.ArgumentParser(description="")
parser.add_argument(
    "--username",
    required=True,)
parser.add_argument(
    "--password",
    required=True,)


def main():

    opts = parser.parse_args()
    # How to get the account balance.
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get("https://www.bet.co.za")

    print("Inputting the username!")
    driver.find_element_by_name("frmUsername").send_keys(opts.username)
    print("Inputting the password!")
    driver.find_element_by_name("frmPassword").send_keys(opts.password)
    print("Accepting terms and conditions!")
    driver.find_element_by_name("frmForceTerms").click()
    print("Submitting data!")
    driver.find_element_by_name("submitted").click()

    balance = driver.find_element_by_id("blocklogout_userBalanceText")
    print("Balance: ", balance.text)
    driver.close()

if __name__ == "__main__":
    main()