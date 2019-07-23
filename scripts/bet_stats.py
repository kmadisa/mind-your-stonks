import argparse
import time
import csv

from datetime import datetime

from selenium import webdriver 
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select 

(TICKET, EVENT_DATE, TOURNAMENT, EVENT, SELECTION, BET_TYPE,
 STAKE, POTENTIAL_WIN, STATUS)  = range(1, 10)

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

    print("Reading timestamp.")
    timestamp = driver.find_element_by_id("time").text.split("Your time: ")
    timestamp = timestamp[-1].strip()
    account_balance = driver.find_element_by_id("blocklogout_userBalanceText").text
    

    print("Account Balance: R", account_balance)
    print("Timestamp: ", timestamp)
    date = datetime.date(datetime.now())
    print("Date: ", date)


    # Also need to get the amount of funds that is placed in bets
    driver.find_element_by_link_text('My Betting History').click()
    # Get the filter form
    form_filter = driver.find_element_by_id('filter_form')
    # Create a selector object for dropdown tables
    selector = Select(form_filter.find_element_by_id('status'))
    # Select 'Unsettled' bets
    selector.select_by_visible_text('Unsettled')
    # Click on the 'Go' button to filter bets
    form_filter.find_element_by_class_name('inputBtn').click()
    # Get the table object
    table = driver.find_element_by_class_name('stdTable')
    # Get all the rows on column number 7 (Stake)
    col = table.find_elements_by_xpath("//tr/td["+str(STAKE)+"]")

    # TODO Handle a situation with multiple pages.
    money_in_bets = 0.00
    for c in col:
        money_in_bets += float(c)
    
    print("Money in bets: R", money_in_bets)

    driver.close()

    with open('balance.csv', mode='w') as balance_file:
        balance_writer = csv.writer(balance_file, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
        balance_writer.writerow([date, account_balance, timestamp, money_in_bets])

if __name__ == "__main__":
    main()
