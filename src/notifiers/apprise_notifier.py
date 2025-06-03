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
        import re

        aps = apprise.Apprise()
        for channel in channels:
            url = self.urls.get(channel)
            if not url:
                # Optionally, log missing channel
                continue

            # Dynamic ntfy topic override
            if channel == "ntfy" and "ntfy_topic" in kwargs:
                # Replace the topic at the end of the URL
                url = re.sub(r"/[^/]+$", f"/{kwargs['ntfy_topic']}", url)

            # Dynamic mattermost channel override
            if channel == "mattermost" and "mattermost_channel" in kwargs:
                if "?" in url:
                    # Replace or add channel param
                    if re.search(r"[?&]channel=", url):
                        url = re.sub(
                            r"([?&])channel=[^&]*",
                            f"\\1channel={kwargs['mattermost_channel']}",
                            url,
                        )
                    else:
                        url += f"&channel={kwargs['mattermost_channel']}"
                else:
                    url += f"?channel={kwargs['mattermost_channel']}"

            aps.add(url)
        aps.notify(title=title, body=message)
