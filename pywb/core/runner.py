from threading import Thread
from time import sleep

from pywb.core.logger import logger
from pywb.surfing.browser import BrowserType


class RunConfig(object):
    def __init__(self, action=None, interval=None, notifier=None, browser_type=BrowserType.CHROME) -> None:
        self.actions = action
        self.interval = interval
        self.notifier = notifier
        self.browser_type = browser_type

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

            self._plugin.initialize(self._run_cfg.actions, self._run_cfg.interval,
                                    self._run_cfg.notifier, self._run_cfg.browser_type)
            logger.info("\n" + self._plugin.ascii())
            self._plugin.start()
        except Exception as e:
            # Generically catching errors here as a catch all for any exceptions thrown by the plugin
            # Only display errors that matter to the user
            if (self._err_from_plugin(e)):
                logger.error(str(e))

    def _err_from_plugin(self, err):
        return not "selenium" in err.__module__ and not "urllib3" in err.__module__

    def shut_down(self):
        self._shutdown = True
