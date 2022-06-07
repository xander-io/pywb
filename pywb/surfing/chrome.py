
from time import sleep

from pywb.core.logger import logger
from pywb.surfing.browser import Browser
from selenium.webdriver import Chrome as SeleniumChrome
from selenium.webdriver import ChromeOptions


class Chrome(Browser):

    def __init__(self, headless=True):
        driver_options = ChromeOptions()
        if headless:
            driver_options.add_argument("--headless")
        driver_options.add_argument('--ignore-certificate-errors')
        driver_options.add_argument('--ignore-ssl-errors')
        driver_options.add_argument("--log-level=3")
        super().__init__(SeleniumChrome(options=driver_options))

    def load_urls(self, urls):
        for i in range(len(urls)):
            url = urls[i]
            logger.info("Loading '%s'", url)
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
                sleep(0.1)
        self._switch_to_main_window()
        return True

# TODO: This will probably get moved
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
