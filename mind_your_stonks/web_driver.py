import psutil
from psutil import NoSuchProcess

from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options


TIMEOUT = 60.00


class WebDriverSetup(object):

    def __init__(self, headless):
        self._timeout = TIMEOUT
        self._options = Options()
        self._options.headless = headless
        self._profile = self._disable_images_firefox_profile()
        self.logger = logger

        self.driver = webdriver.Firefox(
            firefox_profile=self._profile, options=self._options, timeout=self._timeout
        )

        if self._options.headless:
            self.logger.info("Headless Firefox Initialized.")

    def open_session(self, url):
        try:
            self.logger.debug(f"Navigating to {url}.")
            self.driver.get(url)
            self.driver.set_page_load_timeout(self._timeout)
            self.logger.debug(f"Successfully opened the url: {url}.")
        except TimeoutException:
            self.logger.exception("Timed-out while loading page.")
            self.close_session()

    def _disable_images_firefox_profile(self):
        """Summary
        Returns:
            Object: FirefoxProfile
        """
        # get the Firefox profile object
        firefoxProfile = webdriver.FirefoxProfile()
        # Disable images
        firefoxProfile.set_preference("permissions.default.image", 2)
        # Disable Flash
        firefoxProfile.set_preference(
            "dom.ipc.plugins.enabled.libflashplayer.so", "false"
        )
        # Set the modified profile while creating the browser object
        return firefoxProfile

    def close_session(self):
        """Close browser and cleanup"""
        self.logger.info("Closing the browser...")
        self.driver.close()
        self.driver.quit()
        PROCNAME = "geckodriver"
        self.logger.info(f"Cleaning up by killing {PROCNAME} process.")
        try:
            _ = [
                 proc.terminate()
                 for proc in psutil.process_iter()
                 if proc.name() == PROCNAME
            ]
        except NoSuchProcess:
            self.logger.debug(f"Process named {PROCNAME} process does not exist.")

        self.logger.info("Done...")
