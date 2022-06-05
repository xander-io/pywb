from abc import ABC, abstractmethod
from enum import Enum
from genericpath import isfile
from importlib.util import module_from_spec, spec_from_file_location
from os import walk
from os.path import isdir, basename, join
from sys import modules
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

class PluginError(Enum):
    PLUGIN_SUCCESS = 0
    PLUGIN_FAILURE = 1

class Plugin(ABC):
    def __init__(self, name, version) -> None:
        super().__init__()
        self.name = name
        self.version = version
        self._actions = self._browser = self._interval = None

    def ascii(self) -> str:
        return "=========== " + self.name.upper() + " (" + self.version + ")" + " ==========="

    @abstractmethod
    def initialize(self, actions, browser, interval) -> PluginError:
        self._actions = actions
        self._browser = browser
        self._interval = interval

    @abstractmethod
    def start(self) -> PluginError:
        pass

    @abstractmethod
    def stop(self) -> PluginError:
        pass
