from aenum import Constant
from datetime import datetime

from selenium.webdriver.support.select import Select

from mind_your_stonks.web_driver import WebDriverSetup


BET_URL = "https://www.bet.co.za"

# Solution for creating a set of constants found here
# https://codereview.stackexchange.com/questions/193090/python-constant-class-different-enum-implementation

# Betting History table columns
# | Ticket | Event Date | Tournament | Event | Selection | Bet Type | Stake | Potential Win | Status |


class BetHistoryTableColumn(Constant):
    (TICKET, EVENT_DATE, TOURNAMENT, EVENT, SELECTION, BET_TYPE,
     STAKE, POTENTIAL_WIN, STATUS) = range(1, 10)


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
    ALL = "all"


class BetClient(object):
    """The BETcoza client allows users to navigate around the https://www.bet.co.za
    site and extract data from it.

    Attributes
    ----------
    driver : webdriver.Firefox instance
        Controls a browser by sending commands to a remote server.
    """
    def __init__(self, username, password, headless=True):
        """
        Parameters
        ----------
        username : str
            Registered username for the https://www.bet.co.za site.
        password : str
            Registered password for the https://www.bet.co.za site.
        headless : bool
            Flag to run the Firefox browser headless or not.
        """
        self._username = username
        self._password = password
        self.web_setup = WebDriverSetup(headless)
        self.driver = self.web_setup.driver

    def sign_in(self):
        """Log into the https://www.bet.co.za site using your credentials.
        """
        self.web_setup.open_session(BET_URL)
        self.driver.find_element_by_name("frmUsername").send_keys(self._username)
        self.driver.find_element_by_name("frmPassword").send_keys(self._password)
        self.driver.find_element_by_name("frmForceTerms").click()
        self.driver.find_element_by_name("submitted").click()

    def sign_out(self):
        """Log out of the https://www.bet.co.za site.
        """
        self.driver.find_element_by_xpath("//*[@id='block-logout']").click()
        self.web_setup.close_session()

    @property
    def timestamp(self):
        """Returns the current time displayed on https://www.bet.co.za site.

        Returns
        -------
        timestamp : str
            Current timestamp displayed on the site.
        """
        timestamp = self.driver.find_element_by_id("time").text.split("Your time: ")
        timestamp = timestamp[-1].strip()
        return timestamp

    @property
    def current_balance(self):
        """Returns the current account balance displayed on https://www.bet.co.za site.
        Returns
        -------
        account_balance : str
            Current account balance displayed on the site.
        """
        account_balance = (
            self.driver.find_element_by_id("blocklogout_userBalanceText").text)
        return account_balance

    def goto_betting_history(self):
        """Navigate the https://www.bet.co.za betting history page.
        """
        self.driver.find_element_by_link_text("My Betting History").click()

    def goto_account_history(self):
        """Navigate the https://www.bet.co.za account history page.
        """
        self.driver.find_element_by_link_text("My Account History").click()

    def filter_betting_history(self, status, month=BetMonth.LAST_7_DAYS,
                               year=str(datetime.now().year)):
        """Filter the https://www.bet.co.za betting history table according to the
        filter options.

        Parameters
        ----------
        status : BetStatus instance.
            Wager status.
        month : BetMonth instance
            Date filter value.
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
        """

        Returns
        -------
        num_of_pages : int
            The maximum number of pages for the table.
        """
        # Pages can come in different forms
        # '' ==> means just one page
        # '12»' ==> means just two pages in total
        # '1234567»[12]' ==> means 12 pages in total
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
        """Calculate the amount of money has been taken from the balance and placed
        in a bet(s).

        Returns
        -------
        money_invested : float
            The amount of money placed in a bet(s).
        """
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
