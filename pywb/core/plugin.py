from abc import ABC, abstractmethod
from enum import Enum
from importlib.util import module_from_spec, spec_from_file_location
from os import environ, walk
from os.path import basename, isdir, join
from sys import modules

from genericpath import isfile
from pywb import ENVIRON_DEBUG_KEY
from pywb.core.logger import logger
from pywb.surfing.browser import BrowserType
from pywb.surfing.chrome import Chrome


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


PluginError = Enum("PluginError", ["PLUGIN_SUCCESS", "PLUGIN_ERROR"], start=0)


class Plugin(ABC):
    def __init__(self, name, version) -> None:
        super().__init__()
        self.name = name
        self.version = version
        self._actions = self._interval = self._notifier = self._browser = None

    def ascii(self) -> str:
        return "=========== " + self.name.upper() + " (" + self.version + ")" + " ==========="

    @abstractmethod
    def initialize(self, actions, interval, notifier, browser_type) -> PluginError:
        self._actions = actions
        self._interval = interval
        self._notifier = notifier

        if browser_type == BrowserType.CHROME:
            self._browser = Chrome(headless=not (ENVIRON_DEBUG_KEY in environ))
        else:
            raise ValueError("Unsupported browser type '%s'" %
                             browser_type.name.lower())

    @abstractmethod
    def start(self) -> PluginError:
        pass

    @abstractmethod
    def stop(self) -> PluginError:
        pass
