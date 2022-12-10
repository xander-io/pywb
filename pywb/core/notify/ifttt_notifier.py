from pathlib import Path

from requests import post

from pywb.core.notify.notifier import Notifier

default_url = 'https://maker.ifttt.com/trigger/{event_name}/with/key/{key}'


class IftttNotifier(Notifier):
    """A class to trigger IFTTT webhook events."""

    def __init__(self, event_name, key, url=default_url):
        """A class to trigger IFTTT webhook events.
        Parameters
        ----------
        key : str
            The user's IFTTT Webhook key. This key can be found under
            "Documentation" at https://ifttt.com/maker_webhooks/. The key can
            be passed directly to the key parameter or stored in a text file.
            If the value passed to the key parameter is a valid path to a file,
            then the constructor will look for the key on the first line of
            this file.
        url : str, default: 'https://maker.ifttt.com/trigger/{event_name}/with/key/{key}'
            The string corresponding to the url of the webhook event. The
            '{event_name}' and '{key}' fileds will be automatically filled with
            the proper values upon calling one of the trigger methods.
        """
        super().__init__()
        self.__event_name = event_name
        if Path(key).is_file():
            with open(Path(key), 'r') as f:
                self.__key = f.readlines()[0].strip('\n').strip('\r')
        else:
            self.__key = key
        self.__url = url
        # Trigger a test event to check if key is valid
        self.__trigger('key_test_event')

    def __trigger(self, event_name, value1=None, value2=None, value3=None):
        """Triggers the IFTTT event defined by event_name with the JSON content
        defined by the value1, value2 and value3 parameters.

        Parameters
        ----------
        event_name : str
            The name of the IFTTT webhook event to trigger (set in the
            "Event Name" field of the IFTTT Webhook).
        value1, value2 and value3 : str or number
            The optional values passed to the JSON body of the webhook. These
            will be passed as "ingredients" to the Action of the IFTTT Recipe.
        """
        body = {}
        if value1 is not None:
            body['value1'] = value1
        if value2 is not None:
            body['value2'] = value2
        if value3 is not None:
            body['value3'] = value3
        url = self.__url.format(event_name=event_name, key=self.__key)
        response = post(url, json=body)

        if response.status_code != 200:
            raise IftttException(response.status_code,
                                 response.text.strip('\n'))

    def notify(self, title: str, message: str, url: str = None) -> None:
        """Triggers an IFTTT event named 'notification' that sends a
        notification to the user via the IFTTT mobile application. The value1,
        value2 and value3 "ingredients" are mapped to the Title, Content and
        URL fields of the notification respectively.
        For this method to work, the event must be created in the user's IFTTT
        account.
        """
        self.__trigger(self.__event_name, value1=title,
                       value2=message, value3=url)


class IftttException(Exception):
    def __init__(self, status_code, content):
        self.content = content
        self.status_code = status_code

    def __str__(self):
        return repr(f"Status code: {self.status_code}, message: {self.content}")
