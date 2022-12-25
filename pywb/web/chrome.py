
from os import environ, devnull

from selenium.webdriver import Chrome as SeleniumChrome
from selenium.webdriver import ChromeOptions

from pywb import ENVIRON_DEBUG_KEY, ENVIRON_DOCKER_CONTAINER_KEY
from pywb.web.browser import _Browser


class Chrome(_Browser):
    def load_driver(self) -> None:
        super().load_driver()

        options = ChromeOptions()
        options.headless = (
            ENVIRON_DEBUG_KEY not in environ or ENVIRON_DOCKER_CONTAINER_KEY in environ)
        options.add_argument("--no-sandbox")
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--window-size=3440x1440")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # Spoofing our own user agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "\
            "Chrome/107.0.0.0 Safari/537.36"
        options.add_argument('user-agent={0}'.format(user_agent))
        self._driver = SeleniumChrome(options=options, service_log_path=devnull)

    def emulate_location(self, g_lat, g_long) -> None:
        super().emulate_location(g_lat, g_long)
        self._driver.execute_cdp_cmd(
            "Browser.grantPermissions",
            {
                "permissions": ["geolocation"]
            }
        )

        location_data = {"latitude": float(
            g_lat), "longitude": float(g_long), "accuracy": 100}
        self._driver.execute_cdp_cmd(
            "Emulation.setGeolocationOverride", location_data
        )

    def __init__(self):
        super().__init__()
