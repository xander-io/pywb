
from time import sleep

from pywb.core.logger import logger
from pywb.web.browser import Browser
from selenium.webdriver import ChromeOptions
from helium import start_chrome


class Chrome(Browser):

    def __init__(self, headless=True):
        driver_options = ChromeOptions()
        driver_options.add_argument('--ignore-certificate-errors')
        driver_options.add_argument('--ignore-ssl-errors')
        driver_options.add_argument("--log-level=3")
        start_chrome(headless=headless, options=driver_options)
        super().__init__()  
