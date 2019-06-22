import argparse
import time
import csv

from datetime import datetime

from selenium import webdriver 
from selenium.webdriver.firefox.options import Options


parser = argparse.ArgumentParser(description="Scrape the BET.co.za website"
                                 " to obtain the account balance.")
parser.add_argument(
    "--username",
    required=True,
    help="Bet.co.za registered email address",)
parser.add_argument(
    "--password",
    required=True,
    help="Bet.co.za account password.",)

def main():

    opts = parser.parse_args()
    # How to get the account balance.
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get("https://www.bet.co.za")

    print("Entering the username!")
    driver.find_element_by_name("frmUsername").send_keys(opts.username)
    print("Entering the password!")
    driver.find_element_by_name("frmPassword").send_keys(opts.password)
    print("Accepting terms and conditions!")
    driver.find_element_by_name("frmForceTerms").click()
    print("Submitting data to https://www.bet.co.za!")
    driver.find_element_by_name("submitted").click()

    account_balance = driver.find_element_by_id("blocklogout_userBalanceText").text
    driver.close()

    print("Account Balance: R", account_balance)

    date = datetime.date(datetime.now())

    with open('balance.csv', mode='w') as balance_file:
        balance_writer = csv.writer(balance_file, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
        balance_writer.writerow([date, account_balance])

if __name__ == "__main__":
    main()
