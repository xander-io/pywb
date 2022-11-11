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
        self._actions = self._interval = self._notifier = self._browser = None

    def ascii(self) -> str:
        return "=========== " + self.name + " (" + self.version + ")" + " ==========="

    @abstractmethod
    def init_run(self, actions, interval, notifier, browser) -> None:
        assert not self._run_initialized, "Critical Error - Plugin has already been initialized!"

        self._actions = actions
        self._interval = interval
        self._notifier = notifier
        self._browser = browser

        self._run_initialized = True

    def __load_urls(self):
        urls = []
        for action in self._actions:
            urls += action.urls
        self._browser.load_urls(urls)

    @abstractmethod
    def start(self) -> None:
        assert self._run_initialized, "Critical Error - Unable to start plugin. Run has not been initialized!"
        self.__load_urls()

    @abstractmethod
    def stop(self) -> None:
        self._shut_down = True

    def _sleep_on_interval(self):
        logger.info("Waiting on interval (%ds)", self._interval)
        for _ in range(self._interval):
            if self._shut_down:
                logger.debug(
                    "While sleeping, plugin received shutdown signal!")
                break
            sleep(1)
