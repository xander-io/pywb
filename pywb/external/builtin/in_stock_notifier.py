from enum import Enum

from pywb.core.logger import logger
from pywb.core.plugin import Plugin
from pywb.web import By


class InStockNotifier(Plugin):
    VERSION = "0.1"

    ACTION_KWARG_WATCH = "watch"
    ACTION_KWARG_TEXT = "text"
    ACTION_KWARG_NOTIFY_ON = "notify_on"

    NotifyOnType = Enum("NotifyOnType", ["APPEAR", "DISAPPEAR"])

    def __init__(self) -> None:
        self.__baseline = {}
        super().__init__(__class__.__name__, self.VERSION)

    def __validate_action_kwargs(self) -> None:
        for k, v in self._action.kwargs.items():
            if type(v) != list:
                raise ValueError(
                    "For self._action '%s' - '%s' must be a list" % (self._action.title, k))
            if len(v) != len(self._action.urls):
                raise ValueError(
                    "For self._action '%s' - '%s' must have %s values" % (self._action.title, k, len(self._action.urls)))

    def initialize(self, browser, run_cfg) -> None:
        super().initialize(browser, run_cfg)

    def validate(self) -> None:
        super().validate()
        self.__validate_action_kwargs()

    def run(self) -> None:
        super().run()
        # Replace watch and notify string strings with element types
        self._action.kwargs[self.ACTION_KWARG_WATCH] = [By[watch_type.upper()]
                                                        for watch_type in self._action.kwargs[self.ACTION_KWARG_WATCH]]
        self._action.kwargs[self.ACTION_KWARG_NOTIFY_ON] = [self.NotifyOnType[notify_type.upper()]
                                                            for notify_type in self._action.kwargs[self.ACTION_KWARG_NOTIFY_ON]]

        while not self._shut_down:
            self.__notify_changes(self._browser.scrape(
                self._action.urls, self._action.kwargs[self.ACTION_KWARG_WATCH], self._action.kwargs[self.ACTION_KWARG_TEXT]))
            self._sleep_on_refresh_rate()
            if not self._shut_down:
                self._browser.refresh_sites()

    def stop(self) -> None:
        return super().stop()

    def __notify_changes(self, scrape_results) -> None:
        stats = self.__compile_results(self._action.urls, scrape_results)
        if self._action.title not in self.__baseline:
            logger.info("Tracking changes for action '%s'" %
                        self._action.title)
            self.__baseline[self._action.title] = stats

        for i in range(len(self._action.urls)):
            notify = False
            url = self._action.urls[i]
            watch_type = self._action.kwargs[self.ACTION_KWARG_WATCH][i]
            notify_type = self._action.kwargs[self.ACTION_KWARG_NOTIFY_ON][i]
            text = self._action.kwargs[self.ACTION_KWARG_TEXT][i]
            notify |= (stats[url] > self.__baseline[self._action.title][url]
                       or stats[url] != 0 and notify_type == self.NotifyOnType.APPEAR)
            notify |= ((stats[url] < self.__baseline[self._action.title][url]
                        or stats[url] == 0) and notify_type == self.NotifyOnType.DISAPPEAR)
            if notify:
                title = "'%s'" % self._action.title
                message = "%s:%s['%s']" % (
                    str(watch_type), str(notify_type), text)
                logger.info("**** %s: %s (%s) ****" % (title, message, url))
                self._notifier.notify(title, message, url)

    def __compile_results(self, urls, scrape_results) -> dict:
        stats = {}
        for r in scrape_results:
            if r.url not in stats:
                stats[r.url] = 1
            else:
                stats[r.url] = stats[r.url] + 1
        # Fill in urls that did not have any results from web scrape
        for url in urls:
            if url not in stats:
                stats[url] = 0
        return stats


plugin = InStockNotifier
