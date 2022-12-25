from platform import system
from webbrowser import open

from pywb.core.notify.notifier import Notifier

_OS_NAME = system()
if _OS_NAME == "Windows":
    from win11toast import notify as win_notify
elif _OS_NAME == "Darwin":
    from pync import notify as mac_notify


class LocalNotifier(Notifier):
    def __init__(self) -> None:
        super().__init__()

    def notify(self, title: str, msg: str, url: str = "") -> None:
        global _OS_NAME
        if _OS_NAME == "Windows":
            self.__notify_windows_os(title, msg, url=url)
        elif _OS_NAME == "Darwin":
            self.__notify_mac_os(title, msg, url=url)

    def __notify_mac_os(self, title: str, msg: str, url: str = "") -> None:
        mac_notify(msg, title=title, open=url)

    def __notify_windows_os(self, title: str, msg: str, url: str = "") -> None:
        button = None if not url else {
            'activationType': 'protocol', 'arguments': url, 'content': "Open URL"}
        win_notify(title, msg, button=button, on_click=url)
