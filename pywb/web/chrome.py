
from os import environ

from selenium.webdriver import Chrome as SeleniumChrome
from selenium.webdriver import ChromeOptions

from pywb import ENVIRON_DEBUG_KEY
from pywb.web.browser import _Browser


class Chrome(_Browser):
    DEFAULT_PORT = 9515

    def _load_driver(self):
        super()._load_driver()
        options = ChromeOptions()
        options.headless = (not ENVIRON_DEBUG_KEY in environ)
        options.add_argument('--no-sandbox')  # Bypass OS security model
        options.add_argument('--disable-gpu')  # applicable to windows os only
        options.add_argument('start-maximized')
        options.add_argument('disable-infobars')
        options.add_argument("--log-level=3")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        self._driver = SeleniumChrome(options=options)

    def __init__(self):
        super().__init__()
