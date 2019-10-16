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

    driver.find_element_by_name("frmUsername").send_keys(opts.username)
    driver.find_element_by_name("frmPassword").send_keys(opts.password)
    driver.find_element_by_name("frmForceTerms").click()
    driver.find_element_by_name("submitted").click()
    
    timestamp = driver.find_element_by_id("time").text.split("Your time: ")
    timestamp = timestamp[-1].strip()
    account_balance = driver.find_element_by_id("blocklogout_userBalanceText").text
    date = datetime.date(datetime.now())


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
#    # Get all the rows on column number 7 (Stake)
#    stakes = table.find_elements_by_xpath("//tr/td["+str(STAKE)+"]")

    # TODO Handle a situation with multiple pages.
    # Pages can come in different forms
    # '' ==> means just one page
    # '12»' ==> means just two pages in total
    # '1234567»[12]' ==> means 12 pages in total
    # 
    pagination = driver.find_element_by_class_name("pagination")
    pagination_text = pagination.text
    num_of_pages = 0
    if pagination_text == '':
        # only one page to deal with
        num_of_pages = 1
    elif pagination_text.endswith("»"):
        # '12»' -> 2
        num_of_pages = int(pagination_text.split('»')[0][-1])
    elif pagination_text.endswith("]"):
        # '1234567»[12]' -> 12
        num_of_pages = int(pagination_text.split('[')[-1].split(']')[0])

    money_in_bets = 0.00

    for page in range(1, num_of_pages+1):
        if page > 1:
            pagination = driver.find_element_by_class_name("pagination") # Need of raises StaleElementReferenceException
            page_ = pagination.find_element_by_link_text('{}'.format(page))
            page_.click()
            time.sleep(0.5)
        # Get all the rows on column number 7 (Stake)
        stakes = table.find_elements_by_xpath("//tr/td["+str(STAKE)+"]")
        
        for stake in stakes:
            money_in_bets += float(stake.text)


    #money_in_bets = 0.00
    ##for stake in stakes:
    #    money_in_bets += float(stake.text)

    driver.close()

    with open('balance.csv', mode='w') as balance_file:
        balance_writer = csv.writer(balance_file, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
        balance_writer.writerow([date, account_balance, timestamp, money_in_bets])

if __name__ == "__main__":
    main()
