from datetime import datetime, timedelta
from enum import Enum
from urllib.parse import urlparse

from pywb.core.action import Action
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
        self.__element_baseline = {}
        self.__last_notify_time = None
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
            self.__track_changes(self._browser.scrape(
                self._action.urls, self._action.kwargs[self.ACTION_KWARG_WATCH], self._action.kwargs[self.ACTION_KWARG_TEXT]))
            self._sleep_on_refresh_rate()
            if not self._shut_down:
                self._browser.refresh_sites()

    def stop(self) -> None:
        return super().stop()

    def __track_changes(self, scrape_results) -> None:
        stats = self.__compile_results(self._action.urls, scrape_results)
        if self._action.title not in self.__element_baseline:
            logger.info("Tracking changes for action '%s'" %
                        self._action.title)
            self.__element_baseline[self._action.title] = stats

        for i in range(len(self._action.urls)):
            notify = False
            url = self._action.urls[i]
            is_gt_baseline = (stats[url] > self.__element_baseline[self._action.title][url]
                              or stats[url] != 0)
            is_lt_baseline = (stats[url] < self.__element_baseline[self._action.title][url]
                              or stats[url] == 0)
            self.__track_notifications(i, is_gt_baseline, is_lt_baseline)

    def __track_notifications(self, i_url: int, is_gt_baseline: bool, is_lt_baseline: bool) -> None:
        notify = False
        notify_type = self._action.kwargs[self.ACTION_KWARG_NOTIFY_ON][i_url]
        text = self._action.kwargs[self.ACTION_KWARG_TEXT][i_url]
        netloc = urlparse(self._action.urls[i_url]).netloc
        notification_duration = (datetime.now(
        ) - self.__last_notify_time) if self.__last_notify_time else timedelta()

        if notify_type == self.NotifyOnType.APPEAR:
            # On appear, only send the notification once per hour if already sent
            if is_gt_baseline and (notification_duration >= timedelta(hours=1) or not self.__last_notify_time):
                notify = True
                self.__last_notify_time = datetime.now()
                msg = "'%s' has appeared at %s" % (
                    text, netloc)
            # On appear, send a notification if we've reported the element appeared in the past
            elif is_lt_baseline and self.__last_notify_time:
                notify = True
                # Reset the last notify time
                self.__last_notify_time = None
                msg = "'%s' no longer appears at %s" % (
                    text, netloc)
        elif notify_type == self.NotifyOnType.DISAPPEAR:
            if is_lt_baseline and (notification_duration >= timedelta(hours=1) or not self.__last_notify_time):
                notify = True
                self.__last_notify_time = datetime.now()
                msg = "'%s' disappeared at %s" % (
                    text, netloc)
            # On disappear, send a notification if we've reported the element gone in the past
            elif is_gt_baseline and self.__last_notify_time:
                notify = True
                # Reset the last notify time
                self.__last_notify_time = None
                msg = "'%s' has reappeared at %s" % (
                    text, netloc)

        if notify:
            title = "%s: '%s'" % (self.name, self._action.title)
            logger.info("**** %s: %s (%s) ****" % (title, msg, netloc))
            self._notifier.notify(title, msg, netloc)

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
