import os
import signal
from pathlib import Path
from time import sleep

import psutil
from pyww.browser.base_browser import BaseBrowser
from pyww.core.logger import logger
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options


class Chrome(BaseBrowser):
    def __init__(self, sites, headless=True):
        super().__init__()
        self._sites = sites
        driver_options = webdriver.ChromeOptions()
        if headless:
            driver_options.add_argument("--headless")
        driver_options.add_argument('--ignore-certificate-errors')
        driver_options.add_argument('--ignore-ssl-errors')
        driver_options.add_argument("--log-level=OFF")

        self._driver = webdriver.Chrome(
            options=driver_options)

    def load_sites(self):
        if not self._sites:
            return False

        for i in range(len(self._sites)):
            site = self._sites[i]
            logger.info("Loading '%s' for '%s'",
                        site.get_url(friendly=True), site.get_item_name())
            if i == 0:
                self._driver.get(site.get_url())
            else:
                self._driver.execute_script(
                    "window.open('{url}', '_blank');".format(url=site.get_url()))

            # Make sure the driver window handles are updated before loading another site
            expected_handles = i + 1
            while len(self._driver.window_handles) != expected_handles:
                logger.debug("Waiting for %d window handles from driver...",
                             expected_handles)
                sleep(0.1)
        self._switch_to_main_window()
        return True

    def scrape_sites_by_xpath(self):
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

    def refresh_sites(self):
        logger.info("Refreshing sites")

        for handle in self._driver.window_handles:
            self._driver.switch_to_window(handle)
            self._driver.refresh()
        self._switch_to_main_window()

    def close(self):
        self._driver.quit()

    def _switch_to_main_window(self):
        self._driver.switch_to_window(self._driver.window_handles[0])
