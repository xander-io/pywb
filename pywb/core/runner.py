from threading import Thread
from time import sleep
from os import environ

from pywb import ENVIRON_DEBUG_KEY
from pywb.core.logger import logger
from pywb.web.chrome import Chrome


class RunConfig(object):
    def __init__(self, action=None, interval=None, notifier=None) -> None:
        self.actions = action
        self.interval = interval
        self.notifier = notifier

    @classmethod
    def from_run_config(cls, run_cfg) -> 'RunConfig':
        new_cfg = cls()
        new_cfg.__dict__.update(run_cfg.__dict__)
        return new_cfg


class Runner(Thread):
    def __init__(self, plugin, browser, run_cfg) -> None:
        super().__init__()
        self._run_cfg = run_cfg
        self._plugin = plugin()
        self._browser = browser()
        logger.debug("Initialized runner for plugin '%s'..." %
                     str(self._plugin.name))

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
            self._plugin.init_run(self._run_cfg.actions, self._run_cfg.interval,
                                  self._run_cfg.notifier, self._browser)
            logger.info("\n" + self._plugin.ascii())
            self._plugin.start()
        except Exception as e:
            # Generically catching errors as a catch-all for any exceptions thrown by the plugin
            if (self._err_from_driver(e)):
                logger.debug(self._plugin.name + ": " + str(e))
            else:
                logger.error(self._plugin.name + ": " + str(e))
        self._browser.quit()

    def _err_from_driver(self, err):
        # Common errors associated with the driver are from selenium and urllib3
        # Generically identifying them here - otherwise except statement would be massive...
        return hasattr(err, "__module__") and \
            ("selenium" in err.__module__ or "urllib3" in err.__module__)

    def shut_down(self):
        self._plugin.stop()
