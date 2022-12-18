from platform import system

try:
    # Windows?
    from win11toast import notify
except ImportError:
    # Maybe Mac OSX?
    try:
        from mac_notifications import client
    except ImportError:
        # Definitely Linux
        pass

from webbrowser import open

from pywb.core.notify.notifier import Notifier


class LocalNotifier(Notifier):
    def __init__(self) -> None:
        super().__init__()

    def notify(self, title: str, msg: str, url: str = None) -> None:
        os_name = system()
        if os_name == "Windows":
            self.__notify_windows_os(title, msg, url=url)
        elif os_name == "Darwin":
            self.__notify_mac_os(title, msg, url=url)

    def __notify_mac_os(self, title: str, msg: str, url: str = None) -> None:
        client.create_notification(
            title=title,
            subtitle=msg,
            action_button_str="Open URL",
            action_callback=lambda: open(url, new=2)
        )

    def __notify_windows_os(self, title: str, msg: str, url: str = None) -> None:
        button = None if not url else {
            'activationType': 'protocol', 'arguments': url, 'content': "Open URL"}
        notify(title, msg, button=button, on_click=url)
