from threading import Thread
from time import sleep

from pywb.core.logger import logger


class RunConfig(object):
    def __init__(self, action=None, interval=None, notifier=None, browser=None) -> None:
        self.actions = action
        self.interval = interval
        self.notifier = notifier
        self.browser = browser

    @classmethod
    def from_run_config(cls, run_cfg) -> 'RunConfig':
        new_cfg = cls()
        new_cfg.__dict__.update(run_cfg.__dict__)
        return new_cfg


class Runner(Thread):
    def __init__(self, plugin, run_cfg) -> None:
        logger.debug("Initializing runner")
        super().__init__()
        self._shutdown = False
        self._run_cfg = run_cfg
        self._plugin = plugin()

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
            self._plugin.initialize(self._run_cfg.actions, self._run_cfg.browser,
                                    self._run_cfg.interval, self._run_cfg.notifier)
            logger.info("\n" + self._plugin.ascii())
            self._plugin.start()
        except Exception as e:
            logger.error(str(e))

    def shut_down(self):
        self._shutdown = True
