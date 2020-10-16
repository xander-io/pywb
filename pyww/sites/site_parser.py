import yaml
from pyww.core.logger import logger
from pyww.sites.site import NotifyOnType, SiteWatchType, Site

_REQUIRED_ENTRY_ITEMS = ["url", "watch-type", "notify-on", "text"]


def _validate_yaml_entry(entry):
    for item in _REQUIRED_ENTRY_ITEMS:
        if item not in entry:
            raise ValueError

    watch_type = entry["watch-type"].lower()
    if watch_type not in [i.value for i in SiteWatchType]:
        raise ValueError(
            "Watch type '{watch_type}' is invalid".format(watch_type=watch_type))

    notify_on = entry["notify-on"].lower()
    if notify_on not in [i.value for i in NotifyOnType]:
        raise ValueError(
            "Notify on '{notify_on}' is invalid".format(notify_on=notify_on))


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
    except (yaml.YAMLError, ValueError) as e:
        raise RuntimeError("Unable to parse file at location '{path}'. {error}".format(
            path=yaml_path, error=str(e)))
