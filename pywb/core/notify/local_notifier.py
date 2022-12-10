from pywb.core.notify.notifier import Notifier


class LocalNotifier(Notifier):
    def __init__(self) -> None:
        super().__init__()

    def notify(self, title: str, message: str, url: str = None) -> None:
        pass
