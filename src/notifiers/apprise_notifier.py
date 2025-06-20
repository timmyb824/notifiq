import re
import urllib.parse
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
            url = self.urls.get(channel)
            if not url:
                # Optionally, log missing channel
                continue

            # Dynamic ntfy topic override
            if channel == "ntfy" and "ntfy_topic" in kwargs:

                parsed = urllib.parse.urlparse(url)
                # Remove trailing slash, split path, replace last segment
                path_parts = parsed.path.rstrip("/").split("/")
                path_parts[-1] = kwargs["ntfy_topic"]
                new_path = "/".join(path_parts)
                url = urllib.parse.urlunparse(parsed._replace(path=new_path))

            # Dynamic gotify app token override
            if channel == "gotify" and "gotify_app" in kwargs:
                parsed = urllib.parse.urlparse(url)
                path_parts = parsed.path.rstrip("/").split("/")
                # Replace the last segment (token) with gotify_app
                if len(path_parts) > 0:
                    path_parts[-1] = kwargs["gotify_app"]
                    new_path = "/".join(path_parts)
                    url = urllib.parse.urlunparse(parsed._replace(path=new_path))

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
