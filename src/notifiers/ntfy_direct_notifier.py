import contextlib
from typing import Any, Optional
from urllib.parse import urlparse, unquote
import requests

from src.notifiers.base import BaseNotifier


class NtfyDirectNotifier(BaseNotifier):
    """
    Notifier for sending messages directly to ntfy using HTTP requests, with support for markdown and Apprise-style URL parsing.
    """

    def __init__(self, apprise_url: str):
        """
        Args:
            apprise_url: Apprise-style ntfy URL (e.g., ntfys://user:pass@host/topic)
        """
        self.url, self.auth = self.parse_apprise_ntfy_url(apprise_url)

    @staticmethod
    def parse_apprise_ntfy_url(
        apprise_url: str,
    ) -> tuple[Optional[str], Optional[tuple[str, str]]]:
        """
        Parse an Apprise-style ntfy URL and return (direct_url, (user, pass)) tuple if credentials exist.
        """
        if not apprise_url:
            return None, None
        parsed = urlparse(apprise_url)
        # Scheme: ntfy/ntfys -> http/https
        scheme = "https" if parsed.scheme == "ntfys" else "http"
        netloc = parsed.hostname
        port = f":{parsed.port}" if parsed.port else ""
        path = parsed.path or ""
        # Credentials
        username = unquote(parsed.username) if parsed.username else None
        password = unquote(parsed.password) if parsed.password else None
        auth = (username, password) if username and password else None
        # Compose URL
        direct_url = f"{scheme}://{netloc}{port}{path}"
        return direct_url, auth

    def send(
        self, title: str, message: str, channels: list[str], **kwargs: Any
    ) -> None:
        """
        Send a notification directly to ntfy using HTTP POST with markdown support.
        Args:
            title: The notification title.
            message: The notification body.
            channels: List of channel names (should include "ntfy-direct" if using this notifier)
            kwargs: Extra arguments for the notifier (e.g., markdown, tags, priority, etc.)
        """
        headers = {"X-Markdown": "true"}
        if "headers" in kwargs:
            headers |= kwargs["headers"]
        req_headers = headers.copy()
        req_headers["Title"] = title
        for k, v in kwargs.items():
            if k.startswith("X-"):
                req_headers[k] = v
        # Only send if 'ntfy-direct' is in channels
        if "ntfy-direct" in channels and self.url:
            url_to_use = self.url
            if ntfy_topic := kwargs.get("ntfy_topic"):
                # Replace the last segment of the path with the new topic
                parsed = urlparse(url_to_use)
                # Remove trailing slash for clean split
                path_parts = parsed.path.rstrip("/").split("/")
                if len(path_parts) > 1:
                    path_parts[-1] = ntfy_topic
                elif len(path_parts) == 1:
                    path_parts[0] = ntfy_topic
                new_path = "/" + "/".join(path_parts)
                url_to_use = f"{parsed.scheme}://{parsed.hostname}{f':{parsed.port}' if parsed.port else ''}{new_path}"
            data = message
            try:
                resp = requests.post(
                    url_to_use,
                    data=data.encode("utf-8"),
                    headers=req_headers,
                    timeout=5,
                    auth=self.auth,
                )
                if not resp.ok:
                    import logging

                    logging.error(
                        "ntfy-direct failed: status=%s url=%s response=%s",
                        resp.status_code,
                        url_to_use,
                        resp.text,
                    )
            except Exception as e:
                import logging

                logging.error("ntfy-direct exception: url=%s error=%s", url_to_use, e)
