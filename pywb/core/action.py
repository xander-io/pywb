from typing import Tuple

from yaml import YAMLError, safe_load

_REQUIRED_ENTRY_ITEMS = ["plugin", "urls"]


def _validate_yaml_entry(entry) -> Tuple[str, str]:
    items = []
    for item in _REQUIRED_ENTRY_ITEMS:
        if item not in entry:
            raise ValueError("'%s' not in entry" % item)
        items.append(entry[item])
        del entry[item]
    return tuple(items)


def _yaml_entry_to_site(title, entry):
    plugin, urls = _validate_yaml_entry(entry)
    return Action(title, plugin, urls, **entry)


def parse_actions(yaml_path):
    try:
        actions = []
        with open(yaml_path, "r") as f:
            yaml_data = safe_load(f)
        for title in yaml_data:
            yaml_action = yaml_data[title]
            for entry in yaml_action:
                actions.append(_yaml_entry_to_site(title, entry))
        return actions
    except (YAMLError, ValueError) as e:
        raise RuntimeError(
            "Unable to parse file at location '%s' - %s" % (yaml_path, str(e)))


class Action(object):
    def __init__(self, title, plugin_name, urls, **kwargs) -> None:
        super().__init__()
        self.title = title
        self.urls = urls
        self.plugin_name = plugin_name
        self.kwargs = kwargs
