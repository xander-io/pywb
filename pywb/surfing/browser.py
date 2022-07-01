from abc import ABC, abstractmethod
from enum import Enum
from selenium.webdriver.common.by import By as SeleniumBy

from pywb.core.logger import logger

BrowserType = Enum("BrowserType", ["CHROME"])
By = Enum("By",
          {"ID": SeleniumBy.ID, "XPATH": SeleniumBy.XPATH,
           "LINK_TEXT": "link text", "PARTIAL_LINK_TEXT": SeleniumBy.PARTIAL_LINK_TEXT,
           "NAME": SeleniumBy.NAME, "TAG_NAME": SeleniumBy.TAG_NAME, "CLASS_NAME": SeleniumBy.CLASS_NAME,
           "CSS_SELECTOR": SeleniumBy.CSS_SELECTOR})


class Browser(ABC):

    def __init__(self, driver) -> None:
        super().__init__()
        self._driver = driver
        self._urls = None

    @abstractmethod
    def load_urls(self, urls) -> bool:
        self._urls = urls

    def refresh(self):
        logger.info("Refreshing all browser windows")

        for handle in self._driver.window_handles:
            self._driver.switch_to_window(handle)
            self._driver.refresh()
        self._switch_to_main_window()

    def close(self):
        self._driver.quit()

    def _switch_to_main_window(self):
        self._driver.switch_to_window(self._driver.window_handles[0])

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
        self._switch_to_main_window()
        return scrape_results
