from enum import Enum


class NotifyOnType(Enum):
    APPEAR = "appear"
    DISAPPEAR = "disappear"


class SiteWatchType(Enum):
    LINK = "link",
    BUTTON = "button"


class Site(object):
    def __init__(self, item_name, url, watch_type, notify_on, text):
        self._item_name = item_name
        self._url = url
        self._watch_type = watch_type
        self._notify_on = notify_on
        self._text = text

    def get_url(self):
        return self._url

    def get_item_name(self):
        return self._item_name

    def get_notify_type(self):
        return self._notify_on

    def get_element_xpath(self):
        element_xpath = "//"
        if self._watch_type == SiteWatchType.LINK:
            element_xpath += "a["
        else:  # SitWatchType.BUTTON
            element_xpath += "{watch_type}[".format(
                watch_type=self._watch_type.value)
        element_xpath += "text()='{text}']".format(text=self._text)
        return element_xpath
