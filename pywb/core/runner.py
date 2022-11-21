from os import environ
from threading import Thread
from time import sleep

from pywb import ENVIRON_DEBUG_KEY
from pywb.core.logger import logger
from pywb.web.chrome import Chrome


class RunConfig(object):
    def __init__(self, action=None, actions_path=None, refresh_rate=None, geolocation=None, notifier=None) -> None:
        self.action = action
        self.actions_path = actions_path
        self.refresh_rate = refresh_rate
        self.geolocation = geolocation
        self.notifier = notifier


class Runner(Thread):
    def __init__(self, plugin, browser, run_cfg) -> None:
        super().__init__()
        self.__run_cfg = run_cfg
        self.__plugin = plugin()
        self.__browser = browser()
        logger.debug("Initialized runner for plugin '%s'..." %
                     str(self.__plugin.name))

    def _send_notification(self, site):
        site_item = site.get_item_name()
        logger.info("Sending notification for '%s'", site_item)
        self._notifier.notify(
            site.get_url(friendly=True),
            "Watcher signaled for item '{item}'".format(item=site_item),
            site.get_url()
        )

    @property
    def action(self):
        return self.__run_cfg.action

    @property
    def plugin(self):
        return self.__plugin

    def run(self):
        try:
            self.__plugin.initialize(self.__browser, self.__run_cfg)
            self.__plugin.validate()
            logger.info("\n" + self.__plugin.ascii())
            self.__plugin.run()
        except Exception as e:
            # Generically catching errors as a catch-all for any exceptions thrown by the plugin
            if (self._err_from_driver(e)):
                logger.debug(self.__plugin.name + ": " + str(e))
            else:
                logger.error(self.__plugin.name + ": " + str(e))
        self.__browser.quit()

    def _err_from_driver(self, err):
        # Common errors associated with the driver are from selenium and urllib3
        # Generically identifying them here - otherwise except statement would be massive...
        return hasattr(err, "__module__") and \
            ("selenium" in err.__module__ or "urllib3" in err.__module__)

    def shut_down(self):
        self.__plugin.stop()
