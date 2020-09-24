from .browser.base_browser import BaseBrowser
from .browser.chrome import Chrome
from time import sleep
from threading import Thread
from .logger import logger


class Watcher(Thread):
    def __init__(self, browser, interval, notifier):
        super().__init__()
        self._browser = browser
        self._shutdown = False
        self._interval = interval
        self._notifier = notifier

    def _teardown(self):
        self._browser.close()

    def _watch(self):
        sites_loaded = self._browser.load_sites()
        sleep(self._interval)

        while sites_loaded and not self._shutdown:
            logger.info("Refreshing site")
            site_matches = self._browser.scrape_sites()
            for site in site_matches:
               self._send_notification(site)
            sleep(self._interval)

    def _send_notification(self, site):
        site_url =site.get_url()
        self._notifier.notify(
            "{item}".format(item=site.get_item_name()),
            "Watcher signaled at URL {url}".format(url=site_url),
            site_url
        )

    def run(self):
        self._watch()
        self._teardown()

    def shut_down(self):
        self._shutdown = True
