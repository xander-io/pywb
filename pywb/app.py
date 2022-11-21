"""
The main entry point for the pyww application.

Functions
---------
    run()
"""

from argparse import Namespace
from atexit import register
from sys import exit, stdout
from time import sleep

from cmd2 import Cmd, Cmd2ArgumentParser, ansi, with_argparser

from pywb.ascii.ascii import generate_ascii_art
from pywb.core.action import parse_actions
from pywb.core.notifier import Notifier
from pywb.core.plugin_manager import PluginManager
from pywb.core.run_manager import RunManager, RunManagerStatus
from pywb.core.runner import RunConfig
from pywb.core.settings import Settings
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
        # Set defaults
        self.prompt = "(pywb) > "
        self.__plugin_manager = PluginManager()
        self.__run_manager = RunManager()
        self.__settings = Settings(self)

    def cmdloop(self, intro=None):
        register(self.__shutdown_bot)
        self.poutput(intro)
        self.__plugin_manager.load_builtin_plugins()
        self.__write_ansi_table(
            self.__plugin_manager.generate_loaded_plugins_table)

        # Custom cmdloop that catches multiple keyboard interrupts
        while True:
            try:
                super().cmdloop(intro="")
                break
            except KeyboardInterrupt:
                self.poutput("^C")

    def __shutdown_bot(self):
        self.__stop_bot_service(blocking=True)
        self.poutput("Goodbye :)")

    # Parser for example command
    bot_cmd_parser = Cmd2ArgumentParser(description="Command web bot service")
    service = bot_cmd_parser.add_subparsers(
        title="service controls", help="controls the bot's state")
    start = service.add_parser("start", help="starts the pywb service")
    start.add_argument("--actions", "-a", completer=Cmd.path_complete,
                       help="actions yaml file for the web bot to run")
    restart = service.add_parser("restart", help="restarts the pywb service")
    stop = service.add_parser("stop", help="stops the pywb service")
    status = service.add_parser(
        "status", help="gets a status on the state of the pywb service")

    @with_argparser(bot_cmd_parser)
    def do_bot(self, ns: Namespace) -> None:
        statement_args = ns.cmd2_statement.get().args.split()
        if len(statement_args) == 0:
            self.__write_ansi_table(self.__run_manager.generate_status_table,
                                    extended=(self.__run_manager.status == RunManagerStatus.RUNNING))
            return

        service_cmd = statement_args[0]
        if service_cmd == "start":
            if not ns.actions:
                self.perror(
                    "Unable to start pywb service - Missing actions .yaml file")
                return
            self.__start_bot_service(ns.actions)
        elif service_cmd == "restart":
            actions_path = self.__run_manager.run_cfg.actions_path
            # Stop the service
            self.__stop_bot_service(blocking=True)
            # Start the copied run manager
            self.__start_bot_service(actions_path)
        elif service_cmd == "status":
            self.__write_ansi_table(self.__run_manager.generate_status_table,
                                    extended=(self.__run_manager.status == RunManagerStatus.RUNNING))
        elif service_cmd == "stop":
            # Stop the service
            self.__stop_bot_service()

    def __start_bot_service(self, actions_path):
        # Only can have one run manager
        if self.__run_manager.status >= RunManagerStatus.SHUTTING_DOWN:
            self.perror("The pywb service is already running!")
            return

        # Parse the actions from the yaml file
        actions = parse_actions(actions_path)
        # Get a local copy of the plugins loaded right now
        plugins = self.__plugin_manager.loaded_plugins
        run_cfg = RunConfig(actions_path=actions_path,
                            refresh_rate=self.__settings.refresh_rate,
                            geolocation=self.__settings.geolocation,
                            notifier=Notifier(
                                remote_notifications=self.__settings.remote_notifications))
        # Not started only is set when the thread is new
        self.__run_manager = RunManager(
            actions=actions, plugins=plugins, browser=BrowserType[self.__settings.browser.upper()].value, run_cfg=run_cfg)

        # Detaching run manager execution from cmd2 to respond to ctrl+d properly - using atexit.register to cleanup properly
        self.__run_manager.daemon = True
        self.__run_manager.start()
        while self.__run_manager.status != RunManagerStatus.RUNNING:
            sleep(1)
        self.__write_ansi_table(self.__run_manager.generate_status_table)

    def __stop_bot_service(self, blocking=False):
        if self.__run_manager.status >= RunManagerStatus.STARTED:
            self.__run_manager.shut_down()
            self.poutput("Shutdown signaled for pywb service...")
            if blocking:
                self.__run_manager.join()
            self.__write_ansi_table(
                self.__run_manager.generate_status_table, extended=False)

    def do_plugins(self, _: Namespace) -> None:
        self.__write_ansi_table(
            self.__plugin_manager.generate_loaded_plugins_table)

    def __write_ansi_table(self, table_func, **kwargs) -> None:
        ansi.style_aware_write(
            stdout, table_func(**kwargs))

    # Callback for Cmd settables
    def change_setting(self, param, _, new_v):
        setattr(self.__settings, param, new_v)

        if self.__run_manager.status == RunManagerStatus.RUNNING and param in Settings.PARAMS_RESTART_REQUIRED:
            self.pwarning(
                "WARNING: Run 'bot restart' to apply %s changes" % param)


def run():
    """
    Runs the pywb application

    Returns
    -------
    None
    """

    app = _App()
    exit(app.cmdloop(intro=generate_ascii_art()))
