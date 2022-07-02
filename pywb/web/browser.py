from abc import ABC, abstractmethod
from enum import Enum
from helium import get_driver, go_to, find_all, Window, switch_to, refresh, Button
from time import sleep

from pywb.core.logger import logger

BrowserType = Enum("BrowserType", ["CHROME"])
By = Enum("By", {"BUTTON": Button})

class Browser(ABC):

    def __init__(self) -> None:
        super().__init__()
        self._windows = None

    @staticmethod
    def kill_all():
        driver = get_driver()
        if driver:
            driver.quit()

    def load_urls(self, urls) -> bool:
        driver = get_driver()
        if not driver:
            raise RuntimeError("Unable to find web driver")

        for i in range(len(urls)):
            url = urls[i]
            logger.info("Loading '%s'", url)
            # Load url for the current window
            if i == 0:
                go_to(url)
            else:
                driver.execute_script(
                    "window.open('%s', '_blank');" % url)

            # Make sure the driver window handles are updated before loading another site
            expected_handles = i + 1
            while len(find_all(Window())) != expected_handles:
                logger.debug("Waiting for %d window handles from driver..." %
                             expected_handles)
                sleep(0.1)
        self._windows = find_all(Window())
        self._switch_to_first_window()

    def refresh_sites(self):
        logger.info("Refreshing all browser windows")
        for handle in self._windows:
            switch_to(handle)
            refresh()

    def _switch_to_first_window(self):
        switch_to(self._windows[0])

    def scrape(self, by, text=None):
        if not self._windows:
            return None

        logger.info("Scraping sites for data...")
        scrape_results = []
        for i in range(len(self._windows)):
            switch_to(self._windows[i])
            scrape_results.append(find_all(by(text)))
        return scrape_results
