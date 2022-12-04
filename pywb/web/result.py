

class Result(object):
    def __init__(self, element, url, window_handle, browser):
        self.url = url
        self.window_handle = window_handle
        self.__browser = browser
        self.__element = element

    @property
    def element(self):
        # Selenium throws a stale reference if not on the active window - switch to the window before returning the element
        self.__browser.switch_to(self.window_handle)
        return self.__element
