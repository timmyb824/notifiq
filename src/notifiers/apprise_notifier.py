from typing import Any

import apprise

from src.logging_config import setup_logging
from src.notifiers.base import BaseNotifier

setup_logging()


class AppriseNotifier(BaseNotifier):
    """
    Apprise notifier.
    """

    def __init__(self, urls: dict):
        """
        Args:
            urls: Dict mapping channel names to Apprise URLs.
        """
        self.urls = urls

    def send(
        self, title: str, message: str, channels: list[str], **kwargs: Any
    ) -> None:
        """
        Send a notification using Apprise.
        Args:
            title: The notification title.
            message: The notification body.
            channels: List of channel names (e.g., ["ntfy", "loki"])
            kwargs: Extra arguments for the notifier.
        """
        aps = apprise.Apprise()
        for channel in channels:
            if url := self.urls.get(channel):
                aps.add(url)
            else:
                # Optionally, log missing channel
                pass
        aps.notify(title=title, body=message)
