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
        for action in self._actions:
            for k, v in action.kwargs.items():
                if type(v) != list:
                    raise ValueError(
                        "For action '%s' - '%s' must be a list" % (action.title, k))
                if len(v) != len(action.urls):
                    raise ValueError(
                        "For action '%s' - '%s' must have %s values" % (action.title, k, len(action.urls)))

    def init_run(self, actions, interval, notifier, browser) -> None:
        super().init_run(actions, interval, notifier, browser)
        self.__validate_action_kwargs()

    def start(self) -> None:
        super().start()
        # Combine action properties into one list
        for action in self._actions:
            # Replace watch and notify string strings with element types
            action.kwargs[self.ACTION_KWARG_WATCH] = [By[watch_type.upper()]
                                                      for watch_type in action.kwargs[self.ACTION_KWARG_WATCH]]
            action.kwargs[self.ACTION_KWARG_NOTIFY_ON] = [self.NotifyOnType[notify_type.upper()]
                                                          for notify_type in action.kwargs[self.ACTION_KWARG_NOTIFY_ON]]

        while not self._shut_down:
            for action in self._actions:
                self.__notify_changes(action, self._browser.scrape(
                    action.urls, action.kwargs[self.ACTION_KWARG_WATCH], action.kwargs[self.ACTION_KWARG_TEXT]))
            self._sleep_on_interval()
            if not self._shut_down:
                self._browser.refresh_sites()

    def stop(self) -> None:
        return super().stop()

    def __notify_changes(self, action, scrape_results) -> None:
        stats = self.__compile_results(action.urls, scrape_results)
        if action.title not in self.__baseline:
            logger.info("Tracking changes for action '%s'" % action.title)
            self.__baseline[action.title] = stats

        for i in range(len(action.urls)):
            notify = False
            url = action.urls[i]
            watch_type = action.kwargs[self.ACTION_KWARG_WATCH][i]
            notify_type = action.kwargs[self.ACTION_KWARG_NOTIFY_ON][i]
            text = action.kwargs[self.ACTION_KWARG_TEXT][i]
            notify |= (stats[url] > self.__baseline[action.title]
                       [url] and notify_type == self.NotifyOnType.APPEAR)
            notify |= ((stats[url] < self.__baseline[action.title][url]
                        or stats[url] == 0) and notify_type == self.NotifyOnType.DISAPPEAR)
            if notify:
                title = "'%s'" % action.title
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
