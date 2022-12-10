from json import dumps, load
from json.decoder import JSONDecodeError
from os import path

from cmd2 import Cmd, Settable

from pywb.core.logger import DEFAULT_LOG_PATH, set_logger_output_path
from pywb.web import BrowserType


class Settings(object):
    __PARAM_BROWSER = "browser"
    __PARAM_REFRESH_RATE = "refresh_rate"
    __PARAM_REMOTE_NOTIFICATIONS = "remote_notifications"
    __PARAM_GEOLOCATION = "geolocation"
    __PARAM_LOG_PATH = "log_path"

    CUSTOM_PARAMS = [__PARAM_BROWSER, __PARAM_REFRESH_RATE,
                     __PARAM_REMOTE_NOTIFICATIONS, __PARAM_GEOLOCATION, __PARAM_LOG_PATH]

    PARAMS_BOT_RESTART_REQUIRED = [
        __PARAM_BROWSER, __PARAM_REFRESH_RATE, __PARAM_REMOTE_NOTIFICATIONS, __PARAM_GEOLOCATION]

    SAVE_FILE = path.join(path.dirname(__file__), "user_settings.json")

    def __init__(self) -> None:
        # Internal - Defaults
        self.actions_path = None

        # Custom settable attributes - Defaults
        self.__browser = "Chrome"
        self.__refresh_rate = 60
        self.__log_path = DEFAULT_LOG_PATH
        self.__remote_notifications = False
        self.__geolocation = []
        self.__app_ctx = None

    def load(self) -> None:
        saved_settings = self.__load_from_save_file()
        for s_name, value in saved_settings.items():
            if s_name in self.CUSTOM_PARAMS:
                ctx = self
                # Access the private member version to avoid unnecessary checks/initialization
                s_name = "_%s__%s" % (self.__class__.__name__, s_name)
            else:
                ctx = self.__app_ctx
            setattr(ctx, s_name, value)

    def __load_from_save_file(self) -> dict:
        assert self.__app_ctx, "App ctx must have a value when loading settings from file"
        saved_settings = {}
        if path.exists(self.SAVE_FILE):
            with open(self.SAVE_FILE, "r") as settings_file:
                try:
                    saved_settings = load(settings_file)
                except JSONDecodeError:
                    pass
        return saved_settings

    def save(self, param: str) -> None:
        saved_settings = self.__load_from_save_file()
        value = getattr(self, param) if param in self.CUSTOM_PARAMS else getattr(
            self.__app_ctx, param)
        saved_settings[param] = value

        with open(self.SAVE_FILE, "w") as settings_file:
            settings_file.write(dumps(saved_settings))

    def __add_custom_settables(self, app_ctx):
        # Add custom settings
        app_ctx.add_settable(Settable(self.__PARAM_BROWSER, str, "Browser used by pywb (Supported: %s)" % str(
            [i.name.capitalize() for i in BrowserType]), self, onchange_cb=app_ctx.change_setting))
        app_ctx.add_settable(
            Settable(self.__PARAM_REFRESH_RATE, int, "Refresh rate in seconds to poll actions",
                     self, onchange_cb=app_ctx.change_setting))
        app_ctx.add_settable(Settable(self.__PARAM_LOG_PATH, str, "Path to log file for web bot output",
                                      self, onchange_cb=app_ctx.change_setting))
        app_ctx.add_settable(
            Settable(self.__PARAM_REMOTE_NOTIFICATIONS, bool, "Receive remote notifcations from pywb",
                     self, onchange_cb=app_ctx.change_setting))
        app_ctx.add_settable(
            Settable(self.__PARAM_GEOLOCATION, str, "Used for emulating location (format: [lat],[long])",
                     self, onchange_cb=app_ctx.change_setting))

        # Hacky way to save builtin settings with cmd2
        for param, settable in app_ctx._settables.items():
            if param not in self.CUSTOM_PARAMS:
                settable.onchange_cb = app_ctx.change_setting

    @property
    def app_ctx(self) -> Cmd:
        return self.__app_ctx

    @app_ctx.setter
    def app_ctx(self, ctx) -> None:
        self.__delete_cmd2_builtins(ctx)
        self.__add_custom_settables(ctx)
        self.__app_ctx = ctx

    @property
    def remote_notifications(self):
        return self.__remote_notifications

    @remote_notifications.setter
    def remote_notifications(self, new_rn):
        self.__remote_notifications = new_rn

    @property
    def log_path(self):
        return self.__log_path

    @log_path.setter
    def log_path(self, new_log_path):
        set_logger_output_path(new_log_path)
        self.__log_path = new_log_path

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
    def geolocation(self) -> list[float]:
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
            BrowserType[new_browser.upper()]
        except KeyError:
            raise ValueError("Browser '%s' is unsupported" % new_browser)
        # Format string
        self.__browser = new_browser.capitalize()

    def __delete_cmd2_builtins(self, app_ctx):
        delattr(Cmd, "do_alias")
        delattr(Cmd, "do_macro")

        app_ctx.remove_settable("allow_style")
        app_ctx.remove_settable("debug")
        app_ctx.remove_settable("always_show_hint")
        app_ctx.remove_settable("echo")
        app_ctx.remove_settable("max_completion_items")
        app_ctx.remove_settable("feedback_to_output")
        app_ctx.remove_settable("quiet")


SETTINGS = Settings()
