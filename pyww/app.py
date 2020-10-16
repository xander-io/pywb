from argparse import ArgumentParser
from pyww.browser.chrome import Chrome
from pyww.core.watcher import Watcher
from pyww import VERSION
from pyww.core.logger import logger
from pyww.sites import site_parser
from pyww.core.notifier import Notifier
from os import environ
import signal

g_watcher = None


def _display_ascii():
    ascii = r"""
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
    logger.info(ascii)


def _parse_args():
    parser = ArgumentParser("pyww")
    parser.add_argument("-i", "--interval", type=int,
                        help="Interval in seconds to refresh website data", default=30)
    parser.add_argument("-s", "--sites", type=str,
                        help="Yaml file to sites", required=True)
    parser.add_argument("-r", "--remote-notifications", action="store_true",
                        help="Enables remote access for push notifications")
    return parser.parse_args()


def _shut_down(s, f):
    global g_watcher
    if g_watcher:
        logger.info("Shutdown signaled for pyww...")
        g_watcher.shut_down()


def _wait_on_watcher():
    global g_watcher
    while g_watcher.is_alive():
        g_watcher.join(timeout=1)


def run():
    global g_watcher
    args = _parse_args()
    _display_ascii()
    signal.signal(signal.SIGINT, _shut_down)

    try:
        g_watcher = Watcher(Chrome(site_parser.parse(args.sites), headless=("PYWW_DEBUG" not in environ)),
                            args.interval,
                            Notifier(remote_notifications=args.remote_notifications))
        g_watcher.start()
    except Exception as e:
        logger.error(str(e))
    finally:
        if g_watcher:
            _wait_on_watcher()
