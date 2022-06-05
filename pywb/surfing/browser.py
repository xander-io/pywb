from abc import ABC, abstractmethod
from enum import Enum

from pywb.core.logger import logger

BrowserType = Enum("BrowserType", ["CHROME"])

class Browser(ABC):

    def __init__(self, driver) -> None:
        super().__init__()
        self._driver = driver

    def find_elements():
        pass

    @abstractmethod
    def load_urls(self, sites) -> bool:
        pass

    def refresh(self):
        logger.info("Refreshing all browser windows")

        for handle in self._driver.window_handles:
            self._driver.switch_to_window(handle)
            self._driver.refresh()
        self._switch_to_main_window()

    def close(self):
        self._driver.quit()

    def _switch_to_main_window(self):
        self._driver.switch_to_window(self._driver.window_handles[0])
