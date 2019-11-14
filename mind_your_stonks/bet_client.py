import time
import collections
from aenum import Constant
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as condition
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from mind_your_stonks.web_driver import WebDriverSetup


BET_URL = "https://www.bet.co.za"
TIMEOUT = 2.00
TABLE_METADATA, TABLE_FIELDS, TICKET_TABLES = 0, 1, 2

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
    ALL = "All"


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
        WebDriverWait(self.driver, TIMEOUT).until(
            condition.url_to_be("https://www.bet.co.za/index.php/user/account/"))
        self.web_setup.logger.info(f"Succesfully logged into {BET_URL}.")

    def sign_out(self):
        """Log out of the https://www.bet.co.za site.
        """
        self.driver.find_element_by_xpath("//*[@id='block-logout']").click()
        self.web_setup.logger.info("Succesfully logged out of {BET_URL}.")
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
        WebDriverWait(self.driver, TIMEOUT).until(
            condition.url_to_be(
                "https://www.bet.co.za/index.php/betting/history/action/betHistory/"))
        self.web_setup.logger.info("Switched to the Betting History page.")

    def goto_account_history(self):
        """Navigate the https://www.bet.co.za account history page.
        """
        self.driver.find_element_by_link_text("My Account History").click()
        WebDriverWait(self.driver, TIMEOUT).until(
            condition.url_to_be(
                "https://www.bet.co.za/index.php/betting/history/action/translog/"))
        self.web_setup.logger.info("Switched to the Account History page.")

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
        WebDriverWait(self.driver, TIMEOUT).until(
            condition.presence_of_element_located((By.CLASS_NAME, "stdTable")))

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

    # TODO (kmadisa 06-09-2019) Find a way to refactor the duplicate code inside
    # the `compute_money_invested` and `export_betting_history_data` methods.
    def compute_money_invested(self):
        """Calculate the amount of money has been taken from the balance and placed
        in a bet(s).

        Returns
        -------
        money_invested : float
            The amount of money placed in a bet(s).
        """
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
                WebDriverWait(self.driver, TIMEOUT).until(
                    condition.presence_of_element_located((By.CLASS_NAME, "stdTable")))

            # Get the table object
            table = self.driver.find_element_by_class_name("stdTable")
            # Get all the rows on column number 7 (Stake)
            stakes = table.find_elements_by_xpath(
                "//tr/td["+str(BetHistoryTableColumn.STAKE)+"]")

            for stake in stakes:
                money_invested += float(stake.text)

        return money_invested

    def export_betting_history_data(self, month=str(BetMonth.ALL)):
        """
        Parameters
        ----------
        month : str
            A string representation of the BetMonth instance.

        Returns
        -------
        betting_history : dict
            The key represent the bet ID and the value is the tuple of lists
            with the bet data.
            e.g.
                {
                    "BET1234567890": (
                        [[metadata],],
                        [[columns],],
                        [[table],]
                    )
                }
        """
        self.filter_betting_history(BetStatus.ALL, month=month)
        betting_history = {}
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
                WebDriverWait(self.driver, TIMEOUT).until(
                    condition.presence_of_element_located((By.CLASS_NAME, "stdTable")))

            # Get the table object
            table = self.driver.find_element_by_class_name("stdTable")

            # Get all the rows on columns. Attempted to extract the data by rows,
            # however the getting the .text attribute resulted in string that would be
            # difficult to split up (no unique delimiter).
            tickets = table.find_elements_by_xpath(
                "//tr/td["+str(BetHistoryTableColumn.TICKET)+"]")

            for ticket in tickets:
                self.web_setup.logger(f"Processing ticket {ticket.text}")
                ticket_link = self.driver.find_element_by_link_text(ticket.text)
                window_handles = self.driver.window_handles
                betting_history_window = window_handles[0]
                ticket_link.click()
                time.sleep(TIMEOUT)
                betting_history[ticket.text] = self._extract_ticket_data()
                self.driver.switch_to.window(betting_history_window)

        return betting_history

    def _extract_ticket_data(self):
        """Extracts the data in the betting ticket.

        Parameters
        ----------
        None

        Returns
        -------
        ticket_data : tuple
            A tuple of three lists.
                0: table metadata
                1: table column names
                2: table of bet entries
        """
        # Get ticket date
        # <tr>
        #     <td>Bet Date:</td>
        #     <td>yyyy-mm-dd hh:mm:ss</td>
        # <tr>
        ticket_date_elts = self.driver.find_elements_by_xpath(
            "/html/body/div[1]/table/tbody/tr[5]/td")
        ticket_date, ticket_time = ticket_date_elts[-1].text.split(" ")
        self.web_setup.logger.debug("Successfully extracted ticket date and time.")

        ticket_data = ([], [], [])

        # Get all tables in the ticket.
        tables = self.driver.find_elements_by_xpath(
            "/html/body/div[2]/table/tbody/tr/td/table")

        if not isinstance(tables, collections.Iterable):
            tables = [tables]

        self.web_setup.logger.debug(f"Found {len(tables)} tables in the ticket.")
        for number, table in enumerate(tables):
            self.web_setup.logger.debug(f"Processing table number: {number}.")
            headers = table.find_elements_by_xpath("thead/tr[2]/td")
            metadata = []
            metadata.extend([ticket_date, ticket_time])
            for header in headers:
                metadata.append(header.text)

            # Get table column names
            #  <tr>
            #      <th>Event</th>
            #      <th>Draw Id</th> (for lucky numbers)
            #      <th>Event Date</th>
            #      <th>Selection</th>
            #      <td>Places</td>   (for accumulator bet type)
            #      <th>Price</th>
            #      <th>Bet</th>
            #      <th>Returned</th>
            #      <th>Status</th>
            #      <th>Venue</th>
            #      <th>Bet Type</th>
            #  </tr>
            column_elts = table.find_elements_by_xpath("thead/tr[3]/th")
            column_names = [column_elt.text for column_elt in column_elts]
            ticket_data[TABLE_FIELDS].append(column_names)

            # Get bet entries in the table by row.
            bet_elts = table.find_elements_by_xpath("tbody/tr")
            bet_table = []
            for bet_elt in bet_elts:
                bet_info_elts = bet_elt.find_elements_by_xpath("td")
                bet_entry = []

                for bet_info_elt in bet_info_elts:
                    bet_entry.append(bet_info_elt.text)

                bet_table.append(bet_entry)

            ticket_data[TABLE_METADATA].append(metadata)
            ticket_data[TICKET_TABLES].append(bet_table)
            self.web_setup.logger.debug(f"Succesfully processed table number: {number}.")

        self.web_setup.logger.debug("COMPLETE: Extracting ticket data.")

        return ticket_data
