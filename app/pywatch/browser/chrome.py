import os
import signal
import subprocess
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from .base_browser import BaseBrowser
from ..sites.site import NotifyOnType
from ..logger import logger

_CHROME_DRIVER_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "drivers", "chromedriver_v85.exe")


class Chrome(BaseBrowser):
    def __init__(self, sites, headless=False):
        super().__init__()
        self._sites = sites
        driver_options = webdriver.ChromeOptions()
        if headless:
            driver_options.add_argument("--headless")
        driver_options.add_argument('--ignore-certificate-errors')
        driver_options.add_argument('--ignore-ssl-errors')
        driver_options.add_argument("--log-level=OFF")

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

    def load_sites(self):
        if not self._sites:
            return False

        self._driver.get(self._sites[0].get_url())
        for site in self._sites[1:]:
            self._driver.execute_script(
                'window.open("{url}", "_blank");'.format(url=site.get_url()))
        self._switch_to_main_window()
        return True

    def scrape_sites(self):
        site_matches = []
        for i in range(len(self._driver.window_handles)):
            self._driver.switch_to_window(self._driver.window_handles[i])
            element_exists = bool(len(self._driver.find_elements_by_xpath(
                    self._sites[i].get_element_xpath())))
            site_notify_type = self._sites[i].get_notify_type()
            if element_exists and site_notify_type == NotifyOnType.APPEAR or\
                    (not element_exists and site_notify_type == NotifyOnType.DISAPPEAR):
                    site_matches.append(self._sites[i])
            self._driver.refresh()
        self._switch_to_main_window()
        return site_matches

    def close(self):
        self._driver.quit()
        self._driver_process.kill()

    def _switch_to_main_window(self):
        self._driver.switch_to_window(self._driver.window_handles[0])
