from aenum import Constant
from datetime import datetime

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as condition
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from mind_your_stonks.web_driver import WebDriverSetup


BET_URL = "https://www.bet.co.za"
TIMEOUT = 2.00

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
        WebDriverWait(self.driver, TIMEOUT).unitl(
            condition.url_to_be("https://www.bet.co.za/index.php/user/account/"))
        self.web_setup.logger.info(f"Succesfully logged into {BET_URL}.")

    def sign_out(self):
        self.driver.find_element_by_xpath("//*[@id='block-logout']").click()
        self.web_setup.logger.info("Succesfully logged out of {BET_URL}.")
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
        WebDriverWait(self.driver, TIMEOUT).unitl(
            condition.url_to_be(
                "https://www.bet.co.za/index.php/betting/history/action/betHistory/"))
        self.web_setup.logger.info("Switched to the Betting History page.")
    
    def goto_account_history(self):
        self.driver.find_element_by_link_text("My Account History").click()
        WebDriverWait(self.driver, TIMEOUT).unitl(
            condition.url_to_be(
                "https://www.bet.co.za/index.php/betting/history/action/translog/"))
        self.web_setup.logger.info("Switched to the Account History page.")

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
        self.web_setup.logger.info(f"Filtering by wager status: {status}.")

        if month != BetMonth.LAST_7_DAYS:
            selector = Select(form_filter.find_element_by_class_name("date_range"))
            # Select option in month dropdown
            selector.select_by_visible_text(month)
            self.web_setup.logger.info(f"Filtering by month: {month}.")

        if year != str(datetime.now().year):
            selector = Select(form_filter.find_element_by_class_name("year"))
            # Select option in year dropdown
            selector.select_by_visible_text(year)
            self.web_setup.logger.info(f"Filtering by year: {year}.")

        # Click on the 'Go' button to filter bets
        form_filter.find_element_by_class_name("inputBtn").click()
        WebDriverWait(self.driver, TIMEOUT).unitl(
            condition.presence_of_element_located(By.CLASS_NAME, "stdTable"))

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
        number_of_pages = self._get_number_of_pages_for_table()
        first_page = 1
        last_page = number_of_pages + 1

        for page_number in range(first_page, last_page):
            self.web_setup.logger.info(f"Computing stakes on page: {page_number}.")
            if page_number > first_page:
                # Need to get the pagination element again or else raises
                # StaleElementReferenceException
                pagination = self.driver.find_element_by_class_name("pagination")
                page = pagination.find_element_by_link_text(f"{page_number}")
                page.click()
                WebDriverWait(self.driver, TIMEOUT).unitl(
                    condition.presence_of_element_located(By.CLASS_NAME, "stdTable"))
            
            # Get the table object
            table = self.driver.find_element_by_class_name("stdTable")
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
        first_page = 1
        last_page = number_of_pages + 1

        for page_number in range(first_page, last_page):
            self.web_setup.logger.info(f"Computing stakes on page: {page_number}.")
            if page_number > first_page:
                # Need to get the pagination element again or else raises
                # StaleElementReferenceException
                pagination = self.driver.find_element_by_class_name("pagination")
                page = pagination.find_element_by_link_text(f"{page_number}")
                page.click()
                WebDriverWait(self.driver, TIMEOUT).unitl(
                    condition.presence_of_element_located(By.CLASS_NAME, "stdTable"))

            # Get the table object
            table = self.driver.find_element_by_class_name("stdTable")

            # Get all the rows on columns. Attempted to extract the data by rows,
            # however the getting the .text attribute resulted in string that would be
            # difficult to split up (no unique delimiter).
            tickets = table.find_elements_by_xpath(
                "//tr/td["+str(BetHistoryTableColumn.TICKET)+"]")

            for ticket in tickets:
                ticket_link = self.driver.find_element_by_link_text(ticket.text)
                window_handles = self.driver.window_handles
                betting_history_window = window_handles[0]
                ticket_link.click()
                WebDriverWait(self.driver, TIMEOUT).unitl(
                    condition.new_window_is_opened(window_handles))
                # TODO (kmadisa 06-09-2019) Extract information fromt the ticket.
                self.driver.switch_to.window(betting_history_window)

        return betting_history
