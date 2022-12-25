from json import dumps, load
from json.decoder import JSONDecodeError
from os import path, environ, sep

from cmd2 import Cmd, Settable

from pywb.core.logger import DEFAULT_LOG_PATH, set_logger_output_path
from pywb.web import BrowserType
from pywb.core.notify.ifttt_notifier import IftttNotifier, IftttException
from pywb import ENVIRON_DOCKER_CONTAINER_KEY

PARAM_BROWSER = "browser"
PARAM_REFRESH_RATE = "refresh_rate"
PARAM_IFTTT_WEBHOOK_EVENT_NAME = "ifttt_webhook_event_name"
PARAM_IFTTT_WEBHOOK_API_KEY = "ifttt_webhook_api_key"
PARAM_GEOLOCATION = "geolocation"
PARAM_LOG_PATH = "log_path"

CUSTOM_PARAMS = [PARAM_BROWSER, PARAM_REFRESH_RATE,
                 PARAM_IFTTT_WEBHOOK_EVENT_NAME, PARAM_IFTTT_WEBHOOK_API_KEY,
                 PARAM_GEOLOCATION, PARAM_LOG_PATH]

PARAMS_BOT_RESTART_REQUIRED = [
    PARAM_BROWSER, PARAM_REFRESH_RATE, PARAM_IFTTT_WEBHOOK_EVENT_NAME,
    PARAM_IFTTT_WEBHOOK_API_KEY, PARAM_GEOLOCATION]


class Settings(object):

    SAVE_FILE = path.join(sep, "app", "data", "user_settings.json") \
        if ENVIRON_DOCKER_CONTAINER_KEY in environ else path.join(path.dirname(__file__), "user_settings.json")

    def __init__(self, app_ctx) -> None:
        # Internal - Defaults
        self.actions_path = None

        # Custom settable attributes - Defaults
        self.__browser = "Chrome"
        self.__refresh_rate = 60
        self.__log_path = DEFAULT_LOG_PATH
        self.__ifttt_webhook_event_name = ""
        self.__ifttt_webhook_api_key = ""
        self.__geolocation = []
        self.__app_ctx = app_ctx

    def load(self) -> None:
        self.__delete_cmd2_builtins()
        self.__add_custom_settables()

        saved_settings = self.__load_from_save_file()
        for s_name, value in saved_settings.items():
            if s_name in CUSTOM_PARAMS:
                ctx = self
                # Access the private member version to avoid unnecessary checks/initialization
                s_name = "_%s__%s" % (self.__class__.__name__, s_name)
            else:
                ctx = self.__app_ctx
            setattr(ctx, s_name, value)

    def __load_from_save_file(self) -> dict:
        saved_settings = {}
        if path.exists(self.SAVE_FILE):
            with open(self.SAVE_FILE, "r") as settings_file:
                try:
                    saved_settings = load(settings_file)
                except JSONDecodeError:
                    pass
        return saved_settings

    def save(self, params: list[str]) -> None:
        saved_settings = self.__load_from_save_file()
        for param in params:
            value = getattr(self, param) if param in CUSTOM_PARAMS else getattr(
                self.__app_ctx, param)
            if not value:
                # Delete existing entries that are now empty values
                if param in saved_settings:
                    del saved_settings[param]
            else:
                saved_settings[param] = value

        with open(self.SAVE_FILE, "w") as settings_file:
            settings_file.write(dumps(saved_settings))

    def __add_custom_settables(self):
        # Add custom settings
        self.__app_ctx.add_settable(Settable(PARAM_BROWSER, str, "Browser used by pywb (Supported: %s)" % str(
            [i.name.capitalize() for i in BrowserType]), self, onchange_cb=self.__app_ctx.on_setting_change))
        self.__app_ctx.add_settable(
            Settable(PARAM_REFRESH_RATE, int, "Refresh rate in seconds to poll actions",
                     self, onchange_cb=self.__app_ctx.on_setting_change))
        self.__app_ctx.add_settable(Settable(PARAM_LOG_PATH, str, "Path to log file for web bot output",
                                             self, onchange_cb=self.__app_ctx.on_setting_change))
        self.__app_ctx.add_settable(
            Settable(PARAM_IFTTT_WEBHOOK_EVENT_NAME, str, "The event name for the IFTTT applet when "
                     "creating the webhook trigger",
                     self, onchange_cb=self.__app_ctx.on_setting_change))
        self.__app_ctx.add_settable(
            Settable(PARAM_IFTTT_WEBHOOK_API_KEY, str, "The api key for the IFTTT applet when creating the webhook trigger. "
                     "To find this, open the documentation tab of the webhook trigger",
                     self, onchange_cb=self.__app_ctx.on_setting_change))
        self.__app_ctx.add_settable(
            Settable(PARAM_GEOLOCATION, str, "Used for emulating location (format: [lat],[long])",
                     self, onchange_cb=self.__app_ctx.on_setting_change))

        # Hacky way to save builtin settings with cmd2
        for param, settable in self.__app_ctx._settables.items():
            if param not in CUSTOM_PARAMS:
                settable.onchange_cb = self.__app_ctx.on_setting_change

    def __test_ifttt_api(self):
        try:
            IftttNotifier.test_api(
                self.__ifttt_webhook_api_key, event_name=self.__ifttt_webhook_event_name)
        except IftttException as ifttte:
            # Erase any saved data if we fail to connect to the api
            self.__ifttt_webhook_api_key = self.__ifttt_webhook_event_name = ""
            self.save([PARAM_IFTTT_WEBHOOK_API_KEY,
                      PARAM_IFTTT_WEBHOOK_EVENT_NAME])
            raise ValueError(
                "Please try a different IFTTT configuration: " + str(ifttte))

    @property
    def ifttt_webhook_event_name(self):
        return self.__ifttt_webhook_event_name

    @ifttt_webhook_event_name.setter
    def ifttt_webhook_event_name(self, new_event_name):
        if self.__ifttt_webhook_event_name == new_event_name:
            return

        self.__ifttt_webhook_event_name = new_event_name
        if self.__ifttt_webhook_api_key:
            self.__test_ifttt_api()

    @property
    def ifttt_webhook_api_key(self):
        return self.__ifttt_webhook_api_key

    @ifttt_webhook_api_key.setter
    def ifttt_webhook_api_key(self, new_api_key):
        if self.__ifttt_webhook_api_key == new_api_key:
            return

        self.__ifttt_webhook_api_key = new_api_key
        if self.__ifttt_webhook_event_name:
            self.__test_ifttt_api()

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

    def __delete_cmd2_builtins(self):
        delattr(Cmd, "do_alias")
        delattr(Cmd, "do_macro")

        self.__app_ctx.remove_settable("allow_style")
        self.__app_ctx.remove_settable("debug")
        self.__app_ctx.remove_settable("always_show_hint")
        self.__app_ctx.remove_settable("echo")
        self.__app_ctx.remove_settable("max_completion_items")
        self.__app_ctx.remove_settable("feedback_to_output")
        self.__app_ctx.remove_settable("quiet")
