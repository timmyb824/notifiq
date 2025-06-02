from typing import Any

import apprise

from src.logging_config import setup_logging
from src.notifiers.base import BaseNotifier

setup_logging()


class MattermostNotifier(BaseNotifier):
    """
    Notifier for Mattermost via Apprise, combining title and message into a single text field.
    """

    def __init__(self, url: str):
        self.url = url

    def send(
        self, title: str, message: str, channels: list[str], **kwargs: Any
    ) -> None:
        combined = f"{title}: {message}" if title else message
        aps = apprise.Apprise()
        aps.add(self.url)
        aps.notify(body=combined)
