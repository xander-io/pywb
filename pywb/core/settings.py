from cmd2 import Cmd, Settable

from pywb.web import BrowserType
from pywb.core.logger import DEFAULT_LOG_PATH, set_logger_output_path


class Settings(object):
    PARAM_BROWSER = "browser"
    PARAM_REFRESH_RATE = "refresh_rate"
    PARAM_REMOTE_NOTIFICATIONS = "remote_notifications"
    PARAM_GEOLOCATION = "geolocation"
    PARAM_LOG_PATH = "log_path"

    PARAMS_RESTART_REQUIRED = [
        PARAM_BROWSER, PARAM_REFRESH_RATE, PARAM_REMOTE_NOTIFICATIONS, PARAM_GEOLOCATION]

    def __init__(self, app_ctx: Cmd) -> None:
        # Internal - Defaults
        self.actions_path = None
        
        # Custom settable attributes - Defaults
        self.__browser = "Chrome"
        self.__refresh_rate = 60
        self.__log_path = DEFAULT_LOG_PATH
        self.__remote_notifications = False
        self.__geolocation = []

        self.__add_custom_settables(app_ctx)
        self.__delete_cmd2_builtins(app_ctx)

    def __add_custom_settables(self, app_ctx):
        # Add custom settings
        app_ctx.add_settable(Settable(self.PARAM_BROWSER, str, "Browser used by pywb (Supported: %s)" % str(
            [i.name.capitalize() for i in BrowserType]), self, onchange_cb=app_ctx.change_setting))
        app_ctx.add_settable(
            Settable(self.PARAM_REFRESH_RATE, int, "Refresh rate in seconds to poll actions",
                     self, onchange_cb=app_ctx.change_setting))
        app_ctx.add_settable(Settable(self.PARAM_LOG_PATH, str, "Path to log file for web bot output",
                                      self, onchange_cb=app_ctx.change_setting))
        app_ctx.add_settable(
            Settable(self.PARAM_REMOTE_NOTIFICATIONS, bool, "Receive remote notifcations from pywb",
                     self, onchange_cb=app_ctx.change_setting))
        app_ctx.add_settable(
            Settable(self.PARAM_GEOLOCATION, str, "Zipcode for emulating geolocation on websites",
                     self, onchange_cb=app_ctx.change_setting))

    @property
    def log_path(self):
        return self.__log_path

    @log_path.setter
    def log_path(self, new_log_path):
        set_logger_output_path(new_log_path)

    @property
    def remote_notifications(self):
        return self.__remote_notifications

    @property
    def refresh_rate(self):
        return self.__refresh_rate

    @refresh_rate.setter
    def refresh_rate(self, new_rate):
        if new_rate < 0:
            raise ValueError(
                "Refresh rate must be greater than zero")
        self.__refresh_rate = new_rate

    @property
    def geolocation(self):
        return self.__geolocation

    @geolocation.setter
    def geolocation(self, new_geo):
        format_err = False
        # Turns off geolocation for the browser
        if len(new_geo) == 0:
            self.__geolocation = []
            return

        if new_geo.find(",") < 0:
            format_err = True
        else:
            new_geo = new_geo.split(",")
            if len(new_geo) < 2 or not new_geo[0] or not new_geo[1]:
                format_err = True
        if format_err:
            raise ValueError(
                "Unsupported format for geolocation - must be [lat],[long]")
        else:
            new_geo[0] = float(new_geo[0].strip())
            new_geo[1] = float(new_geo[1].strip())
            self.__geolocation = new_geo

    @property
    def browser(self):
        return self.__browser

    @browser.setter
    def browser(self, new_browser):
        try:
            # Attempt to set new browser type
            tmp = BrowserType[new_browser.upper()]
        except:
            raise ValueError("Browser '%s' is unsupported" % new_browser)
        # Format string
        self.__browser = new_browser.capitalize()

    def __delete_cmd2_builtins(self, app_ctx):
        delattr(Cmd, "do_alias")
        delattr(Cmd, "do_macro")
        app_ctx.remove_settable("debug")
