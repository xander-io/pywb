from datetime import datetime, timedelta
from enum import Enum
from urllib.parse import urlparse

from pywb.core.logger import logger
from pywb.core.plugin.plugin import Plugin
from pywb.web import By


class ChangeNotifier(Plugin):
    VERSION = "0.1"

    ACTION_KWARG_WATCH = "watch"
    ACTION_KWARG_TEXT = "text"
    ACTION_KWARG_NOTIFY_ON = "notify_on"

    NotifyOnType = Enum("NotifyOnType", ["APPEAR", "DISAPPEAR"])

    def __init__(self) -> None:
        self.__element_baseline = {}
        self.__last_notify_time = {}
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
        self._action.kwargs[self.ACTION_KWARG_WATCH] = [By[watch_type.upper(
        )] for watch_type in self._action.kwargs[self.ACTION_KWARG_WATCH]]

        self._action.kwargs[self.ACTION_KWARG_NOTIFY_ON] = [self.NotifyOnType[notify_type.upper(
        )] for notify_type in self._action.kwargs[self.ACTION_KWARG_NOTIFY_ON]]

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
        if not self.__element_baseline:
            self.__element_baseline = stats
            baseline_str = "\n".join(["URL=[%s], Baseline # of Elements=[%s]" % (
                k, v) for k, v in self.__element_baseline.items()])
            logger.info("Tracking changes for action '%s'\n%s" %
                        (self._action.title, baseline_str))

        for i in range(len(self._action.urls)):
            notification = None
            url = self._action.urls[i]
            notify_type = self._action.kwargs[self.ACTION_KWARG_NOTIFY_ON][i]
            text = self._action.kwargs[self.ACTION_KWARG_TEXT][i]
            netloc = urlparse(url).netloc

            notification_duration = (datetime.now(
            ) - self.__last_notify_time[url]) if url in self.__last_notify_time else timedelta()

            # NOTE: Notification works in two ways, (1) on APPEAR, the # of elements from the baseline has increased
            # (2) on DISAPPEAR, the # of elements from the baseline has decreased OR there are no elements found on the page
            # For APPEAR, the plugin is designed to not notify if elements are present but not greater than the baseline
            # This is to avoid notifying on irrelevant elements
            if notify_type == self.NotifyOnType.APPEAR:
                # On appear, only send the notification once per hour if already sent
                if stats[url] > self.__element_baseline[url] and (notification_duration >= timedelta(hours=1)
                                                                  or url not in self.__last_notify_time):
                    self.__last_notify_time[url] = datetime.now()
                    notification = ("ALERT: '%s'" % self._action.title, "'%s' has appeared at %s" % (
                        text, netloc))
                # On appear, send a notification if we've reported the element appeared in the past but now it's gone
                elif stats[url] == self.__element_baseline[url] and url in self.__last_notify_time:
                    # Reset the last notify time
                    del self.__last_notify_time[url]
                    notification = ("NOTICE: '%s'" % self._action.title, "'%s' no longer appears at %s" % (
                        text, netloc))
            elif notify_type == self.NotifyOnType.DISAPPEAR:
                if (stats[url] < self.__element_baseline[url] or stats[url] == 0) and \
                        (notification_duration >= timedelta(hours=1) or url not in self.__last_notify_time):
                    self.__last_notify_time[url] = datetime.now()
                    notification = ("ALERT: '%s'" % self._action.title, "'%s' disappeared at %s" % (
                        text, netloc))
                # On disappear, send a notification if we've reported the element gone in the past
                elif stats[url] == self.__element_baseline[url] and stats[url] > 0 and url in self.__last_notify_time:
                    # Reset the last notify time
                    del self.__last_notify_time[url]
                    notification = ("NOTICE: '%s'" % self._action.title, "'%s' has reappeared at %s" % (
                        text, netloc))
            if notification:
                logger.info("**** %s: %s (%s) ****" % (*notification, netloc))
                self.notify(*notification, url=url)

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


plugin = ChangeNotifier
