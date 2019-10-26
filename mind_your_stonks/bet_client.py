import argparse
import time
import csv

from datetime import datetime

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select

from mind_your_stonks.web_driver import WebDriverSetup

# Betting History table columns
# | Ticket | Event Date | Tournament | Event | Selection | Bet Type | Stake | Potential Win | Status |
(TICKET, EVENT_DATE, TOURNAMENT, EVENT, SELECTION, BET_TYPE,
 STAKE, POTENTIAL_WIN, STATUS)  = range(1, 10)

# Bet Statuses
ALL = 'Filter by wager status'
UNSETTLED = 'Unsettled'
WON = 'Won'
LOST = 'Lost'
VOID = 'Void'

(JANUARY, FEBRUARY, MARCH, APRIL, MAY, JUNE, JULY,
 AUGUST, SEPTEMBER, OCTOBER, NOVEMBER, DECEMBER) = range(1, 13)
LAST_7_DAYS = '7d'
LAST_30_DAYS = '30'
ALL = 'all'
BET_URL = 'https://www.bet.co.za'


class BetClient(object):
    """
    """
    def __init__(self, username, password, headless=True):
        self._username = username
        self._password = password
        self._driver = WebDriverSetup(headless)
        self.driver = self._driver.driver

    def sign_in(self):
        self._driver.open_session(BET_URL)
        self.driver.find_element_by_name("frmUsername").send_keys(self._username)
        self.driver.find_element_by_name("frmPassword").send_keys(self._password)
        self.driver.find_element_by_name("frmForceTerms").click()
        self.driver.find_element_by_name("submitted").click()

    def sign_out(self):
        self.driver.find_element_by_xpath("//*[@id='block-logout']").click()
        self._driver.close_session()

    @property
    def timestamp(self):
        timestamp = self.driver.find_element_by_id("time").text.split("Your time: ")
        timestamp = timestamp[-1].strip()
        return timestamp

    @property
    def current_balance(self):
        account_balance = self.driver.find_element_by_id("blocklogout_userBalanceText").text
        return account_balance

    def goto_betting_history(self):
        self.driver.find_element_by_link_text('My Betting History').click()
    
    def goto_account_history(self):
        self.driver.find_element_by_link_text('My Account History').click()

    def filter_betting_history(self, status, month=LAST_7_DAYS, year=str(datetime.now().year)):
        """

        Parameters
        ----------
        status : str
            Wager status
        month : str
        year : str
        """
        # Get the filter form
        form_filter = self.driver.find_element_by_id('filter_form')
        # Create a selector object for dropdown tables
        selector = Select(form_filter.find_element_by_id('status'))
        # Select 'Unsettled' bets
        selector.select_by_visible_text(status)

        if month != LAST_7_DAYS:
            selector = Select(form_filter.find_element_by_class_name('date_range'))
            # Select 'Unsettled' bets
            selector.select_by_visible_text(month)

        if year != str(datetime.now().year):
            selector = Select(form_filter.find_element_by_class_name('year'))
            # Select 'Unsettled' bets
            selector.select_by_visible_text(year)

        # Click on the 'Go' button to filter bets
        form_filter.find_element_by_class_name('inputBtn').click()

    def _get_number_of_pages_for_table(self):
        # Pages can come in different forms
        # '' ==> means just one page
        # '12»' ==> means just two pages in total
        # '1234567»[12]' ==> means 12 pages in total
        # 
        pagination = self.driver.find_element_by_class_name("pagination")
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
        
        return num_of_pages

    def compute_money_invested(self):
        money_invested = 0.00
        num_of_pages = self._get_number_of_pages_for_table()
        # Get the table object
        table = self.driver.find_element_by_class_name('stdTable')
        for page in range(1, num_of_pages+1):
            if page > 1:
                pagination = self.driver.find_element_by_class_name("pagination") # Need of raises StaleElementReferenceException
                page_ = pagination.find_element_by_link_text('{}'.format(page))
                page_.click()
            
            # Get all the rows on column number 7 (Stake)
            stakes = table.find_elements_by_xpath("//tr/td["+str(STAKE)+"]")
        
            for stake in stakes:
                money_invested += float(stake.text)
        
        return money_invested


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

    bet_client = BetClient(opts.username, opts.password)
    bet_client.sign_in()

    timestamp = bet_client.timestamp
    account_balance = bet_client.current_balance
    bet_client.goto_betting_history()
    bet_client.filter_betting_history(UNSETTLED, 2019)
    money_in_bets = bet_client.compute_money_invested()

    date = datetime.date(datetime.now())

    bet_client.sign_out()

    with open('balance.csv', mode='w') as balance_file:
        balance_writer = csv.writer(balance_file, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
        balance_writer.writerow([date, account_balance, timestamp, money_in_bets])

if __name__ == "__main__":
    main()
