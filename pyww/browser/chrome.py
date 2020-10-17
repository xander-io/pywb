import os
import signal
import subprocess
import psutil
from pathlib import Path
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from pyww.browser.base_browser import BaseBrowser
from pyww.core.logger import logger

_CHROME_DRIVER_NAME = "chromedriver.exe"
_CHROME_DRIVER_PATH = os.path.join(
    str(Path.home()), "drivers", _CHROME_DRIVER_NAME)


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

        self._kill_stale_driver()
        self._driver_process = subprocess.Popen(_CHROME_DRIVER_PATH,
                                                shell=False,
                                                stdout=subprocess.DEVNULL,
                                                stdin=subprocess.DEVNULL,
                                                creationflags=(
                                                    subprocess.CREATE_NO_WINDOW)
                                                )

        # Using remote to spawn my own driver process I can control
        self._driver = webdriver.Remote(
            "http://127.0.0.1:9515",
            desired_capabilities=webdriver.DesiredCapabilities.CHROME,
            options=driver_options)

    def _kill_stale_driver(self):
        for proc in psutil.process_iter():
            if proc.name() == _CHROME_DRIVER_NAME:
                while proc.is_running():
                    logger.debug(
                        "Found a stale chrome driver process... KILLING!")
                    proc.terminate()
                    sleep(0.1)

    def load_sites(self):
        if not self._sites:
            return False

        for i in range(len(self._sites)):
            site = self._sites[i]
            logger.info("Loading '{url}' for '{item}'".format(
                url=site.get_url(friendly=True), item=site.get_item_name()))
            if i == 0:
                self._driver.get(site.get_url())
            else:
                self._driver.execute_script(
                    "window.open('{url}', '_blank');".format(url=site.get_url()))

            # Make sure the driver window handles are updated before loading another site
            expected_handles = i + 1
            while len(self._driver.window_handles) != expected_handles:
                logger.debug("Waiting for {expected_handles} window handles from driver...".format(
                    expected_handles=expected_handles))
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
        self._driver_process.kill()

    def _switch_to_main_window(self):
        self._driver.switch_to_window(self._driver.window_handles[0])
