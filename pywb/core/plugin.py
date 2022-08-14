from abc import ABC, abstractmethod
from enum import Enum
from importlib.util import module_from_spec, spec_from_file_location
from os import walk
from os.path import basename, isdir, join
from sys import modules
from time import sleep

from genericpath import isfile
from pywb.core.logger import logger


def load_plugins(plugin_path) -> list:
    plugins = {}
    plugin_paths = [(plugin_path, basename(plugin_path))]
    if isdir(plugin_path):
        _, _, file_names = next(walk(plugin_path), (None, None, []))
        plugin_paths = [(join(plugin_path, file_name), file_name)
                        for file_name in file_names]

    for path, file_name in plugin_paths:
        if not isfile(path) or file_name[-3:] != ".py":
            logger.warning(
                "Unable to load pywb plugin file '%s' - Must be a .py file... Skipping" % file_name)
        else:
            module_name = "pywb.external.%s" % file_name[:-3]
            spec = spec_from_file_location(module_name, path)
            module = module_from_spec(spec)
            modules[module_name] = module
            spec.loader.exec_module(module)
            # Storing dict of plugins for instance creation later
            try:
                plugins[module.plugin.__name__] = module.plugin
            except AttributeError:
                raise AttributeError("Unable to ingest external plugin @ path '%s' - "
                                     "Ensure module has attribute 'plugin' defined" % path)
    return plugins


class Plugin(ABC):
    def __init__(self, name, version) -> None:
        super().__init__()
        self.name = name
        self.version = version
        self._shut_down = False
        self._run_initialized = False
        self._actions = self._interval = self._notifier = self._browser = None

    def ascii(self) -> str:
        return "=========== " + self.name.upper() + " (" + self.version + ")" + " ==========="

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
                break
            sleep(1)
