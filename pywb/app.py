"""
The main entry point for the pyww application.

Functions
---------
    run()
"""

from argparse import ArgumentParser
from os import environ
from signal import SIGINT, signal
from sys import exit
from threading import ThreadError

from pywb.ascii.ascii import generate_ascii_art
from pywb.core.action import parse_actions
from pywb.core.logger import logger
from pywb.core.notifier import Notifier
from pywb.core.plugin import load_plugins
from pywb.core.run_manager import RunManager
from pywb.core.runner import RunConfig
from pywb.web.browser import BrowserType


class _App():
    """
    A class representing the pywb application

    Methods
    -------
    start():
        Starts the pyww application
    """

    def __init__(self, args):
        """
        Constructs all the necessary attributes for the app object.

        Parameters
        ----------
        args : object
            the args from argparse
        """

        self._notifier = Notifier(
            remote_notifications=args.remote_notifications)
        self._run_manager = RunManager(RunConfig(interval=args.interval,
                                                 notifier=self._notifier, browser_type=BrowserType.CHROME))
        self._actions_path = args.actions
        self._plugins_path = args.plugins

    def start(self):
        """
        Starts the pywb application.

        Returns
        -------
        None
        """

        signal(SIGINT, self._shut_down)
        logger.info(generate_ascii_art())
        logger.info(self._notifier.notify_info())
        plugins = load_plugins(self._plugins_path)
        actions = parse_actions(self._actions_path)
        if plugins and actions:
            self._run_manager.delegate_and_wait(actions, plugins)

    def _shut_down(self, *_):
        logger.info("Shutdown signaled for pywb...")
        self._run_manager.shut_down()


def _parse_args():
    parser = ArgumentParser("pywb")
    parser.add_argument("-i", "--interval", type=int,
                        help="Interval in seconds to refresh website data", default=30)
    parser.add_argument("-r", "--remote-notifications", action="store_true",
                        help="Enables remote access for push notifications")
    parser.add_argument("-a", "--actions", type=str,
                        help="Yaml file to actions", required=True)
    parser.add_argument("-p", "--plugins", type=str,
                        help="File or folder for python plugins", required=True)
    return parser.parse_args()


def run():
    """
    Runs the pyww application

    Returns
    -------
    None
    """

    try:
        app = _App(_parse_args())
        app.start()
    except ThreadError as te:
        logger.error(te)
        # Calling exit in case we have any rogue external plugins that aren't cleaning up properly
        exit()
    except Exception as err:
        logger.error(err)
