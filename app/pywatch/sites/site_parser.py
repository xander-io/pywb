import yaml
from ..logger import logger
from .site import NotifyOnType, SiteWatchType, Site

_REQUIRED_ENTRY_ITEMS = ["url", "watch-type", "notify-on", "text"]


def _validate_yaml_entry(entry):
    for item in _REQUIRED_ENTRY_ITEMS:
        if item not in entry:
            raise ValueError

    if entry["watch-type"].lower() not in [i.value for i in SiteWatchType]:
        raise ValueError

    if entry["notify-on"].lower() not in [i.value for i in NotifyOnType]:
        raise ValueError


def _yaml_entry_to_site(item_name, entry):
    _validate_yaml_entry(entry)
    return Site(item_name, entry["url"], SiteWatchType(entry["watch-type"].lower()),
                NotifyOnType(entry["notify-on"].lower()), entry["text"])


def parse(yaml_path):
    try:
        sites = []
        with open(yaml_path, "r") as f:
            yaml_data = yaml.safe_load(f)
        for item_name in yaml_data:
            yaml_sites = yaml_data[item_name]
            for entry in yaml_sites:
                sites.append(_yaml_entry_to_site(item_name, entry))
        return sites
    except (yaml.YAMLError, ValueError):
        raise RuntimeError("""Unable to parse file at location {} -
                                file is corrupt or syntax is incorrect".format(yaml_path)""")
