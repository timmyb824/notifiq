import apprise
from typing import List, Any
from .base import BaseNotifier


class AppriseNotifier(BaseNotifier):
    def __init__(self, urls: dict):
        """
        Args:
            urls: Dict mapping channel names to Apprise URLs.
        """
        self.urls = urls

    def send(
        self, title: str, message: str, channels: List[str], **kwargs: Any
    ) -> None:
        aps = apprise.Apprise()
        for channel in channels:
            if url := self.urls.get(channel):
                aps.add(url)
            else:
                # Optionally, log missing channel
                pass
        aps.notify(title=title, body=message)
