from abc import ABC, abstractmethod
from os import environ, mkdir, path
from time import sleep
from urllib.parse import urlparse

from pywb import ENVIRON_DEBUG_KEY
from pywb.core.logger import logger
from pywb.web.result import Result


class _Browser(ABC):

    def __init__(self) -> None:
        super().__init__()
        self._driver = None
        self._window_map = {}

    def quit(self):
        if self._driver:
            self._driver.quit()

    @abstractmethod
    def load_driver(self) -> None:
        pass

    @abstractmethod
    def emulate_location(self, lat, long) -> None:
        pass

    def load_urls(self, urls) -> None:
        if not self._driver:
            raise RuntimeError(
                "Unable to load urls - driver has not been loaded!")

        for i in range(len(urls)):
            url = urls[i]
            # Only need to load the url once
            if url in self._window_map:
                continue
            logger.info("Loading '%s'", url)
            # Load url for the current window
            if i == 0:
                self._driver.get(url)
            else:
                self._driver.execute_script(
                    "window.open('%s', '_blank');" % url)
            # Make sure the driver window handles are updated before loading another site
            expected_handles = i + 1
            while len(self._driver.window_handles) != expected_handles:
                logger.debug("Waiting for %d window handles from driver..." %
                             expected_handles)
                sleep(0.5)
            self._window_map[url] = self._driver.window_handles[i]
            self.__wait_on_loading_page()

    def switch_to(self, window_handle) -> None:
        if self._driver.current_window_handle != window_handle:
            self._driver.switch_to.window(window_handle)

    def refresh_sites(self) -> None:
        logger.info("Refreshing all windows")
        for _, window_handle in self._window_map.items():
            self.switch_to(window_handle)
            self._driver.refresh()
            self.__wait_on_loading_page()

    def __wait_on_loading_page(self) -> None:
        page_state = ""
        logger.debug("Waiting for {} page to be loaded.".format(
            self._driver.current_url))
        while page_state != "complete":
            page_state = self._driver.execute_script(
                'return document.readyState;')
            if page_state != "complete":
                logger.debug("Page has not loaded yet... Waiting")
            sleep(1)
        logger.debug("Page successfully loaded")

    def scrape(self, urls, bys, texts) -> list[Result]:
        if not self._window_map:
            raise RuntimeError("Browser windows are not intialized!")
        elif not texts:
            return []

        scrape_results = []
        for i in range(len(urls)):
            if urls[i] not in self._window_map:
                logger.debug(
                    "Some URLs not found - Loading before scraping data...")
                self.load_urls(urls)
            window_handle = self._window_map[urls[i]]
            xpath = bys[i].value % texts[i]
            logger.debug("Scraping window['%s']; xpath['%s']" % (
                window_handle, xpath))
            self.switch_to(window_handle)
            elements = self._driver.find_elements("xpath", xpath)
            for e in elements:
                if ENVIRON_DEBUG_KEY in environ:
                    self.__save_element_image(
                        e.screenshot_as_png, "%s-%s.png" % (urlparse(urls[i]).netloc, window_handle))
                scrape_results.append(Result(e, urls[i], window_handle, self))
        return scrape_results

    def __save_element_image(self, img, filename):
        IMAGE_DIR = "pywb_scrape_results"

        if not path.exists(IMAGE_DIR):
            mkdir(IMAGE_DIR)
        screenshot_path = path.join(IMAGE_DIR, filename)
        if path.exists(screenshot_path):
            return
        with open(screenshot_path, "wb") as f:
            f.write(img)
