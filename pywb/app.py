"""
The main entry point for the pyww application.

Functions
---------
    run()
"""

from argparse import Namespace
from sys import exit, stdout

from cmd2 import Cmd, Cmd2ArgumentParser, Settable, ansi, with_argparser

from pywb.ascii.ascii import generate_ascii_art
from pywb.core.action import parse_actions
from pywb.core.logger import DEFAULT_LOG_PATH, logger, set_logger_output_path
from pywb.core.notifier import Notifier
from pywb.core.plugin_manager import PluginManager
from pywb.core.run_manager import RunManager
from pywb.core.runner import RunConfig
from pywb.web.browser import BrowserType


class _App(Cmd):
    """
    A class representing the pywb application

    Methods
    -------
    TODO
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the app object.

        Parameters
        ----------
        None
        """
        super().__init__()
        self.__delete_cmd2_builtins()
        self.__init_settings()
        self.__init_managers()

    def __init_managers(self):
        self._plugin_manager = PluginManager()
        self._run_manager = None

    def __init_settings(self):
        # Set defaults
        self.prompt = "(pywb) > "
        self.browser = "Chrome"
        self.interval = 30
        self.log_path = DEFAULT_LOG_PATH
        self.remote_notifications = False

        # Add custom settings
        self.add_settable(
            Settable("browser", str, "Browser used by pywb (Supported: %s)"
                     % str([i.name.capitalize() for i in BrowserType]),
                     self, onchange_cb=self.__on_browser_change))
        self.add_settable(
            Settable("interval", int, "Interval in seconds to poll actions", self))
        self.add_settable(Settable("log_path", str, "Path to log file for web bot output",
                          self, onchange_cb=lambda _p, _o, new_path: set_logger_output_path(new_path)))
        self.add_settable(
            Settable("remote_notifications", bool, "Receive remote notifcations from pywb", self))

    def __delete_cmd2_builtins(self):
        delattr(Cmd, "do_alias")
        delattr(Cmd, "do_macro")
        self.remove_settable("debug")

    def __on_browser_change(self, _p, _o, new_browser):
        try:
            # Attempt to set new browser type
            tmp = BrowserType[new_browser.upper()]
        except:
            raise ValueError("Browser '%s' is unsupported" % new_browser)
        # Format string
        self.browser = new_browser.capitalize()

    def cmdloop(self, intro=None):
        self.poutput(intro)
        self._plugin_manager.load_builtin_plugins()
        self.__display_plugins()

        # Custom cmdloop that catches multiple keyboard interrupts
        while True:
            try:
                super().cmdloop(intro="")
                break
            except KeyboardInterrupt:
                self.poutput("^C")

    # Parser for example command
    bot_cmd_parser = Cmd2ArgumentParser(
        description="Command to start or stop the web bot service"
    )
    # Tab complete using a completer

    service_parser = bot_cmd_parser.add_subparsers(title="service control states", help="help")
    start = service_parser.add_parser("start", help="start")
    stop = service_parser.add_parser("stop", help="stop")
    start.add_argument("--actions", completer=Cmd.path_complete,
                            help="actions yaml file for the web bot to run")

    @with_argparser(bot_cmd_parser)
    def do_bot(self, ns: Namespace) -> None:
        statement = ns.cmd2_statement.get()
        if statement.args.split()[0] == "start":
            # Only can have one run manager
            if self._run_manager:
                self.perror("The pywb service is already running!")
            elif not ns.actions:
                self.perror("Unable to start pywb service - Missing actions .yaml file")
            else:
                actions = parse_actions(ns.actions)
                default_run_cfg = RunConfig(interval=self.interval,
                                            notifier=Notifier(
                                                remote_notifications=self.remote_notifications),
                                            browser_type=BrowserType[self.browser.upper()])
                self._run_manager = RunManager(actions, default_run_cfg)
                self._run_manager.start()
        else:
            if self._run_manager:
                self._run_manager.shut_down()
                self.poutput("Shutdown signaled for pywb service...")
                self._run_manager.join()
            self._run_manager = None
            self.poutput("Successfully stopped the pywb service!")

    def do_plugins(self, _: Namespace) -> None:
        self.__display_plugins()

    def __display_plugins(self) -> None:
        ansi.style_aware_write(
            stdout, self._plugin_manager.generate_loaded_plugins_table())

def run():
    """
    Runs the pywb application

    Returns
    -------
    None
    """

    app = _App()
    exit(app.cmdloop(intro=generate_ascii_art()))
