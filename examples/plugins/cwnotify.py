from enum import Enum
from time import sleep
from pywb.core.logger import logger
from pywb.core.plugin import Plugin


class CWNotify(Plugin):
    VERSION = "0.1"

    def __init__(self) -> None:
        super().__init__(__class__.__name__, self.VERSION)

    def validate_action_kwargs(self, action_kwargs) -> None:
        super().validate_action_kwargs(action_kwargs)
        watch_types = Enum("WatchType", ["BUTTON"])

        for kwargs in action_kwargs:
            import pdb; pdb.set_trace()


    def init_run(self, actions, interval, notifier, browser) -> None:
        super().init_run(actions, interval, notifier, browser)

    def start(self) -> None:
        super().start()
        logger.info("I am starting this plugin up...")

        while not self._shut_down:
            #self._track_changes(self._browser.scrape())
            self._sleep_on_interval()
            if not self._shut_down:
                self._browser.refresh_sites()

    def stop(self) -> None:
        return super().stop()


plugin = CWNotify


"""
def _evaluate_baseline(self, site, n_elements):
    site_notify_type = site.get_notify_type()
    element_baseline = None
    if (n_elements == 0 and site_notify_type == NotifyOnType.APPEAR) or \
            (n_elements > 0 and site_notify_type == NotifyOnType.DISAPPEAR):
        logger.info("Tracking '%s:%s[%s]' for site '%s'",
                    site.get_watch_type().value, site.get_text(),
                    site_notify_type.value, site.get_url(friendly=True))
        element_baseline = n_elements
        logger.debug("'%s': [baseline=%d]",
                        element_baseline, site.get_url(friendly=True))
    else:
        logger.warning("Unable to establish an accurate baseline with '%s:%s[%s]' for site '%s' - "
                        "Action may have already occurred?", site.get_watch_type().value, site.get_text(),
                        site_notify_type.value, site.get_url(friendly=True))
    site.set_element_baseline(element_baseline)
    return element_baseline
"""

"""

def _track_changes(self, scrape_results):
    for site, n_elements in scrape_results:
        site_url = site.get_url(friendly=True)
        site_notify_type = site.get_notify_type()
        element_baseline = site.get_element_baseline()
        if element_baseline is None:
            element_baseline = self._evaluate_baseline(site, n_elements)
            # Unable to track changes if a baseline is not established
            if element_baseline is None:
                logger.warning(
                    "Skipping tracking '%s'...", site_url)
                continue

        if (n_elements > element_baseline and site_notify_type == NotifyOnType.APPEAR) or \
                (n_elements < element_baseline and site_notify_type == NotifyOnType.DISAPPEAR):
            # Action occurred - alert user
            logger.info("ALERT '%s:%s[%s]' in '%s'",
                        site.get_watch_type().value, site.get_text(), site_notify_type.value, site_url)
            logger.debug("'%s': [baseline=%d, [n_elements=%d]",
                            site_url, element_baseline, n_elements)
            self._send_notification(site)
        else:
            # No changes found yet
            logger.info("No changes found in '%s'", site_url)
"""


"""
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
"""

"""
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
"""
