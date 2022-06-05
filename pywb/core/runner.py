from threading import Thread
from time import sleep

from pywb.core.logger import logger


class RunConfig(object):
    def __init__(self, action=None, plugin=None, interval=None, notifier=None) -> None:
        self.action = action
        self.plugin = plugin
        self.interval = interval
        self.notifier = notifier

    @staticmethod
    def copy(run_cfg) -> 'RunConfig':
        cfg_copy = RunConfig()
        cfg_copy.__dict__.update(run_cfg.__dict__)
        return cfg_copy


class Runner(Thread):
    def __init__(self):
        logger.debug("Initializing runner")
        super().__init__()
        self._shutdown = False
        # self._browser = browser
        # self._interval = interval
        # self._notifier = notifier

    def _teardown(self):
        logger.debug("Tearing down runner")
        self._browser.close()

    def _run_plugin(self):
        sites_loaded = self._browser.load_urls()
        while sites_loaded and not self._shutdown:
            self._track_changes(self._browser.scrape_sites_by_xpath())
            self._sleep_on_interval()
            if not self._shutdown:
                self._browser.refresh_sites()

    def _send_notification(self, site):
        site_item = site.get_item_name()
        logger.info("Sending notification for '%s'", site_item)
        self._notifier.notify(
            site.get_url(friendly=True),
            "Watcher signaled for item '{item}'".format(item=site_item),
            site.get_url()
        )

    def run(self):
        try:
            while (not self._shutdown):
                print("Running...")
                sleep(10)

            print("Runner is leaving now")
            # self._run_action()
            # self._teardown()
        except Exception as e:
            logger.error(str(e))

    def shut_down(self):
        self._shutdown = True
