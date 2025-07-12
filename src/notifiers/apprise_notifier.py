import re
import urllib.parse
from typing import Any

import apprise

from src.logging_config import setup_logging
from src.notifiers.base import BaseNotifier
from src.notifiers.priority_mappings import map_gotify_priority, map_ntfy_priority

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
            kwargs: Extra arguments for the notifier. Supports 'priority' for Gotify notifications.
        """
        aps = apprise.Apprise()
        for channel in channels:
            url = self.urls.get(channel)
            if not url:
                continue
            url = self._transform_url(channel, url, kwargs)
            aps.add(url)
        aps.notify(title=title, body=message)

    def _transform_url(self, channel: str, url: str, kwargs: dict) -> str:
        """
        Transform an Apprise URL with dynamic channel override.
        Args:
            channel: The channel name.
            url: The Apprise URL to transform.
            kwargs: Extra arguments for the notifier.
        Returns:
            The transformed URL.
        """
        if channel == "ntfy":
            return self._transform_ntfy_url(url, kwargs)
        if channel == "gotify":
            return self._transform_gotify_url(url, kwargs)
        if channel == "mattermost":
            return self._transform_mattermost_url(url, kwargs)
        return url

    def _transform_ntfy_url(self, url: str, kwargs: dict) -> str:
        # sourcery skip: class-extract-method
        """
        Transform an ntfy URL with dynamic topic override.
        Args:
            url: The ntfy URL to transform.
            kwargs: Extra arguments for the notifier. Supports 'ntfy_topic' for ntfy notifications.
        Returns:
            The transformed URL.
        """
        if "ntfy_topic" in kwargs:
            parsed = urllib.parse.urlparse(url)
            path_parts = str(parsed.path).rstrip("/").split("/")
            path_parts[-1] = str(kwargs["ntfy_topic"])
            new_path = "/".join(path_parts)
            url = urllib.parse.urlunparse(parsed._replace(path=new_path))
        # ntfy priority mapping
        if "priority" in kwargs:
            ntfy_priority = map_ntfy_priority(kwargs["priority"])
            if "?" in str(url):
                url = f"{url}&priority={ntfy_priority}"
            else:
                url = f"{url}?priority={ntfy_priority}"
        return url

    def _transform_gotify_url(self, url: str, kwargs: dict) -> str:
        """
        Transform a Gotify URL with dynamic app token override and always set format=markdown.
        Args:
            url: The Gotify URL to transform.
            kwargs: Extra arguments for the notifier. Supports 'gotify_app' for Gotify notifications.
        Returns:
            The transformed URL.
        """
        if "gotify_app" in kwargs:
            parsed = urllib.parse.urlparse(url)
            if path_parts := str(parsed.path).rstrip("/").split("/"):
                path_parts[-1] = str(kwargs["gotify_app"])
                new_path = "/".join(path_parts)
                url = urllib.parse.urlunparse(parsed._replace(path=new_path))
        # gotify priority mapping
        if "priority" in kwargs:
            gotify_priority = map_gotify_priority(kwargs["priority"])
            if "?" in str(url):
                url = f"{url}&priority={gotify_priority}"
            else:
                url = f"{url}?priority={gotify_priority}"
        # Always set format=markdown
        url = f"{url}&format=markdown" if "?" in str(url) else f"{url}?format=markdown"
        return url

    def _transform_mattermost_url(self, url: str, kwargs: dict) -> str:
        """
        Transform a Mattermost URL with dynamic channel override.
        Args:
            url: The Mattermost URL to transform.
            kwargs: Extra arguments for the notifier. Supports 'mattermost_channel' for Mattermost notifications.
        Returns:
            The transformed URL.
        """
        if "mattermost_channel" in kwargs:
            if "?" in url:
                url = (
                    re.sub(
                        r"([?&])channel=[^&]*",
                        f"\\1channel={kwargs['mattermost_channel']}",
                        url,
                    )
                    if re.search(r"[?&]channel=", url)
                    else f"{url}&channel={kwargs['mattermost_channel']}"
                )
            else:
                url = f"{str(url)}?channel={kwargs['mattermost_channel']}"
        return url
