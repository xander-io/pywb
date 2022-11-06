import os

from notify_run import Notify as RemoteNotify
from notifypy import Notify as LocalNotify
from pywb.core.logger import logger


class Notifier(object):
    def __init__(self, remote_notifications=False):
        self._local_notifier = LocalNotify()
        self._remote_notify_info = None
        if remote_notifications:
            self._register_remote_endpoint()
        else:
            self._remote_notifier = None

    def _register_remote_endpoint(self):
        if not self._remote_notify_info:
            self._remote_notifier = RemoteNotify()

            logger.info(
                "Registering a new Remote Push Notification (RPN) endpoint")
            self._remote_notify_info = str(self._remote_notifier.register())
            if os.name == 'nt':
                # Windows cmd/powershell does not display QR code properly - stripping it off
                self._remote_notify_info = self._remote_notify_info[:self._remote_notify_info.index(
                    "Or scan this QR code")]

    def notify_info(self) -> str:
        notify_info = "\n\n************************** NOTIFICATIONS ****************************\n"
        notify_info += "Local Notifications: ON\n"
        notify_info += ("Remote Notifications: %s" %
                        ("ON" if self._remote_notifier else "OFF"))

        if self._remote_notifier:
            notify_info += "\n\nRemote " + self._remote_notify_info + \
                "\nNOTE: Remote notifications NOT supported for iOS and Safari"

        notify_info += "\n*********************************************************************\n"
        return notify_info

    def notify(self, title, message, link):
        if self._remote_notifier:
            self._send_remote_notification(title, message, link)
        self._send_local_notification(title, message)

    def _send_local_notification(self, title, message):
        self._local_notifier.title = title
        self._local_notifier.message = message
        self._local_notifier.send()

    def _send_remote_notification(self, title, message, link):
        self._remote_notifier.send(
            "{title} - {message}".format(title=title, message=message), link)
