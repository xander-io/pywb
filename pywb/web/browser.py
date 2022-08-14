from abc import ABC
from enum import Enum
from time import sleep

from pywb.web.result import Result
from pywb.core.logger import logger

BrowserType = Enum("BrowserType", ["CHROME"])
By = Enum("By",
          {"BUTTON": "//button[text()='%s']",
           "LINK": "//a[text()='%s']",
           "TEXT": "//*[not(self::a) and not(self::button) and text()='%s']"})


class _Browser(ABC):

    def __init__(self, driver) -> None:
        super().__init__()
        self._driver = driver
        self._window_map = {}

    def quit(self):
        if self._driver:
            self._driver.quit()

    def load_urls(self, urls) -> None:
        for i in range(len(urls)):
            url = urls[i]
            # Only need to load the url once
            if url in self._window_map:
                continue
            logger.info("Loading '%s'", url)
            # Load url for the current window
            if i == 0:
                self._driver.get(url)
            else:
                self._driver.execute_script(
                    "window.open('%s', '_blank');" % url)
            # Make sure the driver window handles are updated before loading another site
            expected_handles = i + 1
            while len(self._driver.window_handles) != expected_handles:
                logger.debug("Waiting for %d window handles from driver..." %
                             expected_handles)
                sleep(0.5)
            self._window_map[url] = self._driver.window_handles[i]

    def switch_to(self, window_handle) -> None:
        if self._driver.current_window_handle != window_handle:
            self._driver.switch_to.window(window_handle)

    def refresh_sites(self) -> None:
        logger.info("Refreshing all windows")
        for _, window_handle in self._window_map.items():
            self.switch_to(window_handle)
            self._driver.refresh()

    def scrape(self, urls, bys, texts) -> list[Result]:
        if not self._window_map:
            raise RuntimeError("Browser windows are not intialized!")
        elif not texts:
            return []

        scrape_results = []
        for i in range(len(urls)):
            if urls[i] not in self._window_map:
                logger.debug(
                    "Some URLs not found - Loading before scraping data...")
                self.load_urls(urls)
            window_handle = self._window_map[urls[i]]
            xpath = bys[i].value % texts[i]
            logger.debug("Scraping window['%s']; xpath['%s']" % (window_handle, xpath))
            self.switch_to(window_handle)
            elements = self._driver.find_elements_by_xpath(xpath)
            for e in elements:
                scrape_results.append(Result(e, urls[i], window_handle, self))
        return scrape_results
