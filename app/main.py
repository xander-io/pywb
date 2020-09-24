from argparse import ArgumentParser
from pywatch.browser.chrome import Chrome
from pywatch.watcher import Watcher
from pywatch import VERSION
from pywatch.logger import logger
from pywatch.sites import site_parser
from pywatch.notifier import Notifier
import signal

g_watcher = None


def _display_ascii():
    ascii = r"""
         _    _        _         _             _                 _             _             _       _  
        /\ \ /\ \     /\_\      / /\      _   / /\              /\ \         /\ \           / /\    / /\
       /  \ \\ \ \   / / /     / / /    / /\ / /  \             \_\ \       /  \ \         / / /   / / /
      / /\ \ \\ \ \_/ / /     / / /    / / // / /\ \            /\__ \     / /\ \ \       / /_/   / / / 
     / / /\ \_\\ \___/ /     / / /_   / / // / /\ \ \          / /_ \ \   / / /\ \ \     / /\ \__/ / /  
    / / /_/ / / \ \ \_/     / /_//_/\/ / // / /  \ \ \        / / /\ \ \ / / /  \ \_\   / /\ \___\/ /   
   / / /__\/ /   \ \ \     / _______/\/ // / /___/ /\ \      / / /  \/_// / /    \/_/  / / /\/___/ /    
  / / /_____/     \ \ \   / /  \____\  // / /_____/ /\ \    / / /      / / /          / / /   / / /     
 / / /             \ \ \ /_/ /\ \ /\ \// /_________/\ \ \  / / /      / / /________  / / /   / / /      
/ / /               \ \_\\_\//_/ /_/ // / /_       __\ \_\/_/ /      / / /_________\/ / /   / / /       
\/_/                 \/_/    \_\/\_\/ \_\___\     /____/_/\_\/       \/____________/\/_/    \/_/
                                
                                        (Version: {})                                                                   
""".format(VERSION)
    logger.info(ascii)


def _parse_args():
    parser = ArgumentParser()
    parser.add_argument("-i", "--interval", type=int,
                        help="Interval in seconds to refresh website data", default=15)
    parser.add_argument("-s", "--sites", type=str,
                        help="Yaml file to sites", required=True)
    parser.add_argument("-r", "--remote-notifications", action="store_true",
                        help="Enables remote access for push notifications")
    parser.add_argument("-f", "--foreground", action="store_true",
                        help="Disables running in headless mode")
    return parser.parse_args()


def _shut_down(s, f):
    global g_watcher
    if g_watcher:
        logger.info("Shutting down Pywatch...")
        g_watcher.shut_down()


def _wait_on_watcher():
    global g_watcher
    while g_watcher.is_alive():
        g_watcher.join(timeout=1)


def main():
    global g_watcher
    args = _parse_args()
    _display_ascii()
    signal.signal(signal.SIGINT, _shut_down)
    try:
        g_watcher = Watcher(Chrome(site_parser.parse(args.sites), headless=(not args.foreground)),
                            args.interval,
                            Notifier(remote_notifications=args.remote_notifications))
        g_watcher.start()
    except Exception as e:
        logger.error(str(e))
    finally:
        if g_watcher:
            _wait_on_watcher()


if __name__ == "__main__":
    main()
