import time
import random
from aenum import Constant

from datetime import datetime

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select

from mind_your_stonks.web_driver import WebDriverSetup


BET_URL = "https://www.bet.co.za"

# Solution for creating a set of constants found here
# https://codereview.stackexchange.com/questions/193090/python-constant-class-different-enum-implementation

# Betting History table columns
# | Ticket | Event Date | Tournament | Event | Selection | Bet Type | Stake | Potential Win | Status |
class BetHistoryTableColumn(Constant):
    (TICKET, EVENT_DATE, TOURNAMENT, EVENT, SELECTION, BET_TYPE,
     STAKE, POTENTIAL_WIN, STATUS)  = range(1, 10)


class BetStatus(Constant):
    ALL = "Filter by wager status"
    UNSETTLED = "Unsettled"
    WON = "Won"
    LOST = "Lost"
    VOID = "Void"


class BetMonth(Constant):
    (JANUARY, FEBRUARY, MARCH, APRIL, MAY, JUNE, JULY,
     AUGUST, SEPTEMBER, OCTOBER, NOVEMBER, DECEMBER) = range(1, 13)
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30"
    ALL = "All"


class BetClient(object):
    """
    """
    def __init__(self, username, password, headless=True):
        self._username = username
        self._password = password
        self.web_setup = WebDriverSetup(headless)
        self.driver = self.web_setup.driver

    def sign_in(self):
        self.web_setup.open_session(BET_URL)
        self.driver.find_element_by_name("frmUsername").send_keys(self._username)
        self.driver.find_element_by_name("frmPassword").send_keys(self._password)
        self.driver.find_element_by_name("frmForceTerms").click()
        self.driver.find_element_by_name("submitted").click()

    def sign_out(self):
        self.driver.find_element_by_xpath("//*[@id='block-logout']").click()
        self.web_setup.close_session()

    @property
    def timestamp(self):
        timestamp = self.driver.find_element_by_id("time").text.split("Your time: ")
        timestamp = timestamp[-1].strip()
        return timestamp

    @property
    def current_balance(self):
        account_balance = (
            self.driver.find_element_by_id("blocklogout_userBalanceText").text)
        return account_balance

    def goto_betting_history(self):
        self.driver.find_element_by_link_text("My Betting History").click()
    
    def goto_account_history(self):
        self.driver.find_element_by_link_text("My Account History").click()

    def filter_betting_history(self, status, month=BetMonth.LAST_7_DAYS,
                               year=str(datetime.now().year)):
        """

        Parameters
        ----------
        status : str
            Wager status
        month : str
            Calendar months in integer or string value.
        year : str
            Years from 2011 to current.
        """
        # Get the filter form
        form_filter = self.driver.find_element_by_id("filter_form")
        # Create a selector object for dropdown tables
        selector = Select(form_filter.find_element_by_id("status"))
        # Select option in wager status dropdown
        selector.select_by_visible_text(status)

        if month != BetMonth.LAST_7_DAYS:
            selector = Select(form_filter.find_element_by_class_name("date_range"))
            # Select option in month dropdown
            selector.select_by_visible_text(month)

        if year != str(datetime.now().year):
            selector = Select(form_filter.find_element_by_class_name("year"))
            # Select option in year dropdown
            selector.select_by_visible_text(year)

        # Click on the 'Go' button to filter bets
        form_filter.find_element_by_class_name("inputBtn").click()

    def _get_number_of_pages_for_table(self):
        # Pages can come in different forms
        # '' ==> means just one page
        # '12»' ==> means just two pages in total
        # '1234567»[12]' ==> means 12 pages in total
        # 
        pagination = self.driver.find_element_by_class_name("pagination")
        pagination_text = pagination.text
        num_of_pages = 0
        if pagination_text == "":
            # only one page to deal with
            num_of_pages = 1
        elif pagination_text.endswith("»"):
            # '12»' -> 2
            num_of_pages = int(pagination_text.split('»')[0][-1])
        elif pagination_text.endswith("]"):
            # '1234567»[12]' -> 12
            num_of_pages = int(pagination_text.split("[")[-1].split("]")[0])
        
        return num_of_pages

    def compute_money_invested(self):
        money_invested = 0.00
        num_of_pages = self._get_number_of_pages_for_table()
        # Get the table object
        table = self.driver.find_element_by_class_name("stdTable")
        for page in range(1, num_of_pages+1):
            if page > 1:
                # Need to get the pagination element again or else raises
                # StaleElementReferenceException
                pagination = self.driver.find_element_by_class_name("pagination")
                page_ = pagination.find_element_by_link_text('{}'.format(page))
                page_.click()
            
            # Get all the rows on column number 7 (Stake)
            stakes = table.find_elements_by_xpath(
                "//tr/td["+str(BetHistoryTableColumn.STAKE)+"]")
        
            for stake in stakes:
                money_invested += float(stake.text)
        
        return money_invested

    def export_betting_history_data(self, month=str(BetMonth.ALL)):
        self.filter_betting_history(BetStatus.ALL, month=month)
        betting_history = []
        number_of_pages = self._get_number_of_pages_for_table()

        for page_number in range(1, number_of_pages+1):
            if page_number > 1:
                # Need to get the pagination element again or else raises
                # StaleElementReferenceException
                pagination = self.driver.find_element_by_class_name("pagination")
                print("Page number: {}".format(page_number))
                page = pagination.find_element_by_link_text('{}'.format(page_number))
                page.click()
                time.sleep(random.randint(2, 3))

            # Get the table object
            table = self.driver.find_element_by_class_name("stdTable")

            # Get all the rows on columns. Attempted to extract the data by rows,
            # however the getting the .text attribute resulted in string that would be
            # difficult to split up (no unique delimiter).
            tickets = table.find_elements_by_xpath(
                "//tr/td["+str(BetHistoryTableColumn.TICKET)+"]")
            event_dates = table.find_elements_by_xpath(
                "//tr/td["+str(BetHistoryTableColumn.EVENT_DATE)+"]")
            tournaments = table.find_elements_by_xpath(
                "//tr/td["+str(BetHistoryTableColumn.TOURNAMENT)+"]")
            events = table.find_elements_by_xpath(
                "//tr/td["+str(BetHistoryTableColumn.EVENT)+"]")
            selections = table.find_elements_by_xpath(
                "//tr/td["+str(BetHistoryTableColumn.SELECTION)+"]")
            bet_types = table.find_elements_by_xpath(
                "//tr/td["+str(BetHistoryTableColumn.BET_TYPE)+"]")
            stakes = table.find_elements_by_xpath(
                "//tr/td["+str(BetHistoryTableColumn.STAKE)+"]")
            potential_wins = table.find_elements_by_xpath(
                "//tr/td["+str(BetHistoryTableColumn.POTENTIAL_WIN)+"]")
            statuses = table.find_elements_by_xpath(
                "//tr/td["+str(BetHistoryTableColumn.STATUS)+"]")

            for (ticket, event_date, tournament, event,
                 selection, bet_type, stake, potential_win,
                 status) in zip(tickets, event_dates, tournaments, events,
                 selections, bet_types, stakes, potential_wins,
                 statuses):
                 betting_history.append([
                     ticket.text, event_date.text, tournament.text,
                     event.text, selection.text, bet_type.text, stake.text,
                     potential_win.text, status.text
                     ])

        return betting_history
