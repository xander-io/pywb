from abc import ABC, abstractmethod
from enum import Enum
from helium import get_driver, go_to, find_all, Window, switch_to, refresh
from time import sleep

from pywb.core.logger import logger

BrowserType = Enum("BrowserType", ["CHROME"])


class Browser(ABC):

    def __init__(self) -> None:
        super().__init__()
        self._urls = None

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
        self._switch_to_first_window()

    def refresh_sites(self):
        logger.info("Refreshing all browser windows")
        for handle in find_all(Window()):
            switch_to(handle)
            refresh()
        self._switch_to_first_window()

    def _switch_to_first_window(self):
        switch_to(find_all(Window())[0])

    def scrape(self, by):
        if not self._urls:
            return None

        logger.info("Scraping sites for data...")
        scrape_results = []
        for i in range(len(self._driver.window_handles)):
            self._driver.switch_to_window(self._driver.window_handles[i])
            site = self._sites[i]
            n_elements = 0
            for xpath in site.get_xpaths():
                tmp_n_elements = len(
                    self._driver.find_elements_by_xpath(xpath))
                if tmp_n_elements and n_elements > 0:
                    # Multiple elements with same text - too ambiguous to refine search
                    raise ValueError(
                        "Multiple elements found containing '{text}' - is ambiguous".format(text=site.get_text()))
                elif n_elements == 0:
                    n_elements = tmp_n_elements
            scrape_results.append((site, n_elements))
        self._switch_to_first_window()
        return scrape_results
