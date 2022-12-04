from abc import ABC, abstractmethod
from time import sleep

from pywb.core.logger import logger


class Plugin(ABC):
    def __init__(self, name, version) -> None:
        super().__init__()
        self.name = name
        self.version = version
        self._shut_down = False
        self._run_initialized = False
        self._action = self._refresh_rate = self._notifier = self._browser = None

    def ascii(self) -> str:
        return "=========== " + self.name + " (" + self.version + ")" + " ==========="

    @abstractmethod
    def initialize(self, browser, run_cfg) -> None:
        assert not self._run_initialized, "Critical Error - Plugin has already been initialized!"

        self._action = run_cfg.action
        self._refresh_rate = run_cfg.refresh_rate
        self._notifier = run_cfg.notifier
        self._browser = browser

        self._browser.load_driver()
        if run_cfg.geolocation:
            g_lat, g_long = run_cfg.geolocation
            logger.info(
                "Geolocation - Emulating latitude[%s], longitude[%s]" % (g_lat, g_long))
            self._browser.emulate_location(g_lat, g_long)
        else:
            logger.warning(
                "No geolocation information given - Attempting to load browser using current location")
        self._run_initialized = True

    def __load_urls(self):
        self._browser.load_urls(self._action.urls)

    @abstractmethod
    def validate(self) -> None:
        pass

    @abstractmethod
    def run(self) -> None:
        assert self._run_initialized, "Critical Error - Unable to start plugin. Run has not been initialized!"
        self.__load_urls()

    @abstractmethod
    def stop(self) -> None:
        self._shut_down = True

    def _sleep_on_refresh_rate(self):
        logger.info("Waiting for (%ds) to refresh action", self._refresh_rate)
        for _ in range(self._refresh_rate):
            if self._shut_down:
                logger.debug(
                    "While sleeping, plugin received shutdown signal!")
                break
            sleep(1)

    def __str__(self) -> str:
        return self.name
