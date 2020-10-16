from enum import Enum
from urllib.parse import urlsplit


class NotifyOnType(Enum):
    APPEAR = "appear"
    DISAPPEAR = "disappear"


class SiteWatchType(Enum):
    # Matches with the sites parser
    LINK = "link"
    BUTTON = "button"
    TEXT = "text"


_SITE_ELEMENTS = {
    SiteWatchType.LINK.value: ["a"],
    SiteWatchType.BUTTON.value: ["button", "a", "input"],
    SiteWatchType.TEXT.value: ["span", "p"]
}


class Site(object):
    def __init__(self, item_name, url, watch_type, notify_on, text):
        self._item_name = item_name
        self._url = url
        self._watch_type = watch_type
        self._notify_on = notify_on
        self._text = text
        self._element_baseline = None
        self._xpaths = self._generate_xpaths()

    def get_element_baseline(self):
        return self._element_baseline

    def set_element_baseline(self, element_baseline):
        self._element_baseline = element_baseline

    def get_text(self):
        return self._text

    def get_url(self, friendly=False):
        if friendly:
            return urlsplit(self._url).netloc
        return self._url

    def get_item_name(self):
        return self._item_name

    def get_notify_type(self):
        return self._notify_on

    def get_watch_type(self):
        return self._watch_type

    def get_xpaths(self):
        return self._xpaths

    def _generate_xpaths(self):
        xpaths = []
        try:
            elements = _SITE_ELEMENTS[self._watch_type.value]
        except KeyError:
            raise ValueError("Elements do not exist for watch type '{watch_type}'".format(
                watch_type=self._watch_type.value))

        for element in elements:
            element_xpath = "//{element}[contains(translate(text(), '{text_upper}', '{text_lower}'),'{text_lower}')]".format(
                element=element, text_upper=self._text.upper(), text_lower=self._text.lower())
            xpaths.append(element_xpath)
        return xpaths
