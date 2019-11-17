import pytest
from mock import Mock, call, patch

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from  selenium.common.exceptions import TimeoutException
from mind_your_stonks.bet_client import BetClient, BET_URL, TIMEOUT


@pytest.fixture(scope="class")
def bet_client():
    _username = "pytester"
    _password = "pytester3.6.8"
    bet_client = BetClient(_username, _password)

    yield bet_client

@pytest.fixture()
def driver():
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(
        "file:///home/kmadisa47/src/personal/mind-your-stonks/sandbox/sign_in.html")

    yield driver

@pytest.mark.usefixtures("bet_client")
class TestBetClient(object):

    def test_sign_in(self, bet_client, driver):

        bet_client.driver = driver

        bet_client.web_setup.open_session = Mock()

        FirefoxWebElement.send_keys = Mock()
        FirefoxWebElement.click = Mock()

        with pytest.raises(TimeoutException):
            bet_client.sign_in()

        assert FirefoxWebElement.send_keys.call_count == 2
        assert FirefoxWebElement.send_keys.call_args_list == [
            call("pytester"), call("pytester3.6.8")
        ]
        assert FirefoxWebElement.click.call_count == 2

    def test_sign_out(self, bet_client, driver):
        pass

    def test_timestamp(self, bet_client):
        pass

    def test_goto_betting_history(self):
        pass

    def test_goto_account_history(self):
        pass

    def test_filter_betting_history(self):
        pass

    def test_export_betting_history_data(self):
        pass
