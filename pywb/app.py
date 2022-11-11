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
from pywb.core.logger import DEFAULT_LOG_PATH, set_logger_output_path
from pywb.core.notifier import Notifier
from pywb.core.plugin_manager import PluginManager
from pywb.core.run_manager import RunManager
from pywb.core.runner import RunConfig
from pywb.web import BrowserType


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
        self.__plugin_manager = PluginManager()
        self.__run_manager = None

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
        self.__plugin_manager.load_builtin_plugins()
        self.__display_plugins()

        # Custom cmdloop that catches multiple keyboard interrupts
        while True:
            try:
                super().cmdloop(intro="")
                break
            except KeyboardInterrupt:
                self.poutput("^C")

    # Parser for example command
    bot_cmd_parser = Cmd2ArgumentParser(description="Command web bot service")
    service = bot_cmd_parser.add_subparsers(title="service controls", help="controls the bot's state")
    start = service.add_parser("start", help="start")
    start.add_argument("--actions", "-a", completer=Cmd.path_complete,
                            help="actions yaml file for the web bot to run")
    stop = service.add_parser("stop", help="stop")
    status = service.add_parser("status", help="status")

    @with_argparser(bot_cmd_parser)
    def do_bot(self, ns: Namespace) -> None:
        statement = ns.cmd2_statement.get()
        service_cmd = statement.args.split()[0]
        if service_cmd == "start":
            self.__start_bot_service(ns)
        elif service_cmd == "status":
            self.poutput("No status at this time :)")
        else:
            self.__stop_bot_service()


    def __start_bot_service(self, ns): 
        # Only can have one run manager
        if self.__run_manager and self.__run_manager.is_alive():
            self.perror("The pywb service is already running!")
        elif not ns.actions:
            self.perror("Unable to start pywb service - Missing actions .yaml file")
        else:
            # Parse the actions from the yaml file
            actions = parse_actions(ns.actions)
            # Get a local copy of the plugins loaded right now
            plugins = self.__plugin_manager.loaded_plugins
            default_run_cfg = RunConfig(interval=self.interval,
                                        notifier=Notifier(
                                            remote_notifications=self.remote_notifications))

            self.__run_manager = RunManager(actions, plugins, BrowserType[self.browser.upper()].value, default_run_cfg)
            self.__run_manager.start()
    
    def __stop_bot_service(self):
        if not self.__run_manager:
            return

        self.__run_manager.shut_down()
        self.poutput("Shutdown signaled for pywb service...")
        self.__run_manager.join()
        self.poutput("Successfully stopped the pywb service!")
        self.__run_manager = None


    def do_plugins(self, _: Namespace) -> None:
        self.__display_plugins()

    def __display_plugins(self) -> None:
        ansi.style_aware_write(
            stdout, self.__plugin_manager.generate_loaded_plugins_table())

def run():
    """
    Runs the pywb application

    Returns
    -------
    None
    """

    app = _App()
    exit(app.cmdloop(intro=generate_ascii_art()))
