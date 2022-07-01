
from time import sleep

from pywb.core.logger import logger
from pywb.web.browser import Browser
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
        super().load_urls(urls)        
