from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from inspect import getfile
from os import path, walk
from pathlib import Path
from sys import modules

from cmd2.table_creator import Column, SimpleTable
from genericpath import isfile


class PluginManager(object):

    def __init__(self) -> None:
        self.__loaded_plugins = {}

    def load_builtin_plugins(self) -> None:
        builtin_path = path.join(
            Path(__file__).parent.resolve(), "..", "..", "external", "trusted")
        self.load_plugins(builtin_path)

    def load_plugins(self, plugin_path: str) -> int:
        plugins = {}
        plugin_paths = [(plugin_path, path.basename(plugin_path))]
        if path.isdir(plugin_path):
            _, _, file_names = next(walk(plugin_path), (None, None, []))
            plugin_paths = [(path.join(plugin_path, fn), fn)
                            for fn in file_names]

        n_plugins_found = 0
        for p, fn in plugin_paths:
            if not isfile(p) or fn[-3:] != ".py" or fn == "__init__.py":
                continue
            else:
                module_name = "pywb.external.%s" % fn[:-3]
                spec = spec_from_file_location(module_name, p)
                module = module_from_spec(spec)
                modules[module_name] = module
                spec.loader.exec_module(module)
                # Storing dict of plugins for instance creation later
                try:
                    plugins[module.plugin.__name__] = module.plugin
                except AttributeError:
                    raise AttributeError("Unable to ingest external plugin @ path '%s' - "
                                         "Ensure module has attribute 'plugin' defined" % p)
                n_plugins_found += 1
        self.__loaded_plugins |= plugins
        return n_plugins_found

    @property
    def loaded_plugins(self):
        # Return a shallow copy of the loaded plugins
        return deepcopy(self.__loaded_plugins)

    def generate_loaded_plugins_table(self) -> str:
        plugin_list = []
        columns = []
        w_plugin_name = 20
        w_module_path = 90

        for k, v in self.__loaded_plugins.items():
            module_path = getfile(v)
            if len(module_path) > w_module_path:
                module_path = "%s..." % module_path[:(w_module_path-3)]
            plugin_list.append([str(k), module_path])

        n_plugins = len(plugin_list)
        columns.append(Column("Plugin Name", width=w_plugin_name))
        columns.append(Column("Module Path", width=w_module_path))
        t = SimpleTable(columns)
        return ("\n %s\n\nTOTAL PLUGINS LOADED: (%s)\n\n") % (t.generate_table(plugin_list), n_plugins)
