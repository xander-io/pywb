
from time import sleep

from pywb.web.browser import _Browser
from selenium.webdriver import ChromeOptions
from selenium.webdriver import Chrome as SeleniumChrome

class Chrome(_Browser):

    def __init__(self, headless=True):
        driver_options = ChromeOptions()
        driver_options.headless = headless
        driver_options.add_argument('--ignore-certificate-errors')
        driver_options.add_argument('--ignore-ssl-errors')
        driver_options.add_argument("--log-level=3")
        driver_options.add_argument("--disable-infobars")
        driver_options.add_argument("--disable-extensions")
        super().__init__(SeleniumChrome(options=driver_options)
)  
