import signal
from argparse import ArgumentParser
from os import environ

from pyww import ENVIRON_DEBUG_KEY, VERSION
from pyww.browser.chrome import Chrome
from pyww.core.logger import logger
from pyww.core.notifier import Notifier
from pyww.core.watcher import Watcher
from pyww.sites import site_parser


class _App():
    def __init__(self, args):
        self._watcher = None
        self._interval = args.interval
        self._sites = args.sites
        self._remote_notifications = args.remote_notifications

    def start(self):
        signal.signal(signal.SIGINT, self._shut_down)
        logger.info(_App.get_ascii_art())
        try:
            self._watcher = Watcher(Chrome(site_parser.parse(self._sites),
                                           headless=(ENVIRON_DEBUG_KEY not in environ)),
                                    self._interval,
                                    Notifier(remote_notifications=self._remote_notifications))
            self._watcher.start()
        except ValueError as err:
            logger.error(str(err))
        finally:
            if self._watcher:
                self._wait_on_watcher()

    def _shut_down(self, *_):
        logger.info("Shutdown signaled for pyww...")
        self._watcher.shut_down()

    def _wait_on_watcher(self):
        while self._watcher.is_alive():
            self._watcher.join(timeout=1)

    @staticmethod
    def get_ascii_art():
        ascii_art = r"""
 ________  ___    ___ ___       __   ___       __      
|\   __  \|\  \  /  /|\  \     |\  \|\  \     |\  \    
\ \  \|\  \ \  \/  / | \  \    \ \  \ \  \    \ \  \   
 \ \   ____\ \    / / \ \  \  __\ \  \ \  \  __\ \  \  
  \ \  \___|\/  /  /   \ \  \|\__\_\  \ \  \|\__\_\  \ 
   \ \__\ __/  / /      \ \____________\ \____________\
    \|__||\___/ /        \|____________|\|____________|
         \|___|/                                                   
               (Version: {version})                                                                   
        """.format(version=VERSION)
        return ascii_art


def _parse_args():
    parser = ArgumentParser("pyww")
    parser.add_argument("-i", "--interval", type=int,
                        help="Interval in seconds to refresh website data", default=30)
    parser.add_argument("-s", "--sites", type=str,
                        help="Yaml file to sites", required=True)
    parser.add_argument("-r", "--remote-notifications", action="store_true",
                        help="Enables remote access for push notifications")
    return parser.parse_args()


def run():
    app = _App(_parse_args())
    app.start()
