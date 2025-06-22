import re
import urllib.parse
from typing import Any

import apprise

from src.logging_config import setup_logging
from src.notifiers.base import BaseNotifier

setup_logging()

# Priority mappings for Gotify
GOTIFY_PRIORITY_MAP = {
    0: "low",
    3: "moderate",
    5: "normal",
    8: "high",
    10: "emergency",
}


def map_gotify_priority(priority: int) -> str:
    return GOTIFY_PRIORITY_MAP.get(priority, "normal")


# Priority mappings for ntfy
NTFY_PRIORITY_MAP = {
    1: "min",
    2: "low",
    3: "default",
    4: "high",
    5: "max",
}


def map_ntfy_priority(priority: int) -> str:
    return NTFY_PRIORITY_MAP.get(priority, "default")


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
            kwargs: Extra arguments for the notifier. Supports 'priority' for Gotify notifications.
        """

        aps = apprise.Apprise()
        for channel in channels:
            url = self.urls.get(channel)
            if not url:
                # Optionally, log missing channel
                continue

            # Dynamic ntfy topic override
            if channel == "ntfy" and "ntfy_topic" in kwargs:
                parsed = urllib.parse.urlparse(url)
                # Remove trailing slash, split path, replace last segment
                path_parts = str(parsed.path).rstrip("/").split("/")
                path_parts[-1] = str(kwargs["ntfy_topic"])
                new_path = "/".join(path_parts)
                url = urllib.parse.urlunparse(parsed._replace(path=new_path))

            # ntfy priority mapping
            if channel == "ntfy" and "priority" in kwargs:
                ntfy_priority = map_ntfy_priority(kwargs["priority"])
                if "?" in str(url):
                    url = f"{url}&priority={ntfy_priority}"
                else:
                    url = f"{url}?priority={ntfy_priority}"

            # Dynamic gotify app token override
            if channel == "gotify" and "gotify_app" in kwargs:
                parsed = urllib.parse.urlparse(url)
                if path_parts := str(parsed.path).rstrip("/").split("/"):
                    path_parts[-1] = str(kwargs["gotify_app"])
                    new_path = "/".join(path_parts)
                    url = urllib.parse.urlunparse(parsed._replace(path=new_path))

            # gotify priority mapping
            if channel == "gotify" and "priority" in kwargs:
                gotify_priority = map_gotify_priority(kwargs["priority"])
                if "?" in str(url):
                    url = f"{url}&priority={gotify_priority}"
                else:
                    url = f"{url}?priority={gotify_priority}"

            # Dynamic mattermost channel override
            if channel == "mattermost" and "mattermost_channel" in kwargs:
                if "?" in str(url):
                    # Replace or add channel param
                    if re.search(r"[?&]channel=", str(url)):
                        url = re.sub(
                            r"([?&])channel=[^&]*",
                            f"\\1channel={kwargs['mattermost_channel']}",
                            str(url),
                        )
                    else:
                        url = f"{str(url)}&channel={kwargs['mattermost_channel']}"
                else:
                    url = f"{str(url)}?channel={kwargs['mattermost_channel']}"

            aps.add(url)

        aps.notify(title=title, body=message)
