from typing import Any, Optional
from urllib.parse import unquote, urlparse

import logging
import httpx

from src.logging_config import setup_logging
from src.notifiers.base import BaseNotifier

setup_logging()


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
        scheme = "https" if parsed.scheme == "ntfys" else "http"
        netloc = parsed.hostname
        port = f":{parsed.port}" if parsed.port else ""
        path = parsed.path or ""
        username = unquote(parsed.username) if parsed.username else None
        password = unquote(parsed.password) if parsed.password else None
        auth = (username, password) if username and password else None
        direct_url = f"{scheme}://{netloc}{port}{path}"
        return direct_url, auth

    def send(
        self, title: str, message: str, channels: list[str], **kwargs: Any
    ) -> None:
        """
        Send a notification directly to ntfy using HTTP POST with markdown support.
        Args:
            title: The notification title (can include emojis).
            message: The notification body.
            channels: List of channel names (should include "ntfy-direct" if using this notifier).
            kwargs: Extra headers like priority, tags, etc.
        """
        logging.info("[ntfy-direct] send() called with title='%s'", title)

        if "ntfy-direct" not in channels or not self.url:
            return

        parsed = urlparse(self.url)
        base_url = f"{parsed.scheme}://{parsed.hostname}{f':{parsed.port}' if parsed.port else ''}"
        topic = kwargs.get("ntfy_topic") or parsed.path.strip("/").split("/")[-1]
        url_to_use = f"{base_url}/{topic}"

        # Construct headers (as bytes to allow UTF-8 in title)
        headers: dict[bytes, bytes] = {
            b"Title": title.encode("utf-8"),
            b"X-Markdown": b"true",
        }

        for k, v in kwargs.items():
            if k.startswith("X-"):
                headers[k.encode("utf-8")] = str(v).encode("utf-8")

        try:
            resp = httpx.post(
                url=url_to_use,
                content=message.encode("utf-8"),
                headers=headers,
                timeout=5.0,
                auth=self.auth,
            )
            if resp.status_code >= 400:
                logging.error(
                    "ntfy-direct failed: status=%s url=%s response=%s",
                    resp.status_code,
                    url_to_use,
                    resp.text,
                )
            else:
                logging.info(
                    "[ntfy-direct] Notification posted successfully: status=%s url=%s",
                    resp.status_code,
                    url_to_use,
                )
        except Exception as e:
            logging.error("ntfy-direct exception: url=%s error=%s", url_to_use, e)


### REQUESTS VERSION ###

# from typing import Any, Optional
# from urllib.parse import unquote, urlparse

# import logging
# import requests

# from src.logging_config import setup_logging
# from src.notifiers.base import BaseNotifier

# setup_logging()


# class NtfyDirectNotifier(BaseNotifier):
#     """
#     Notifier for sending messages directly to ntfy using HTTP requests, with support for markdown and Apprise-style URL parsing.
#     """

#     def __init__(self, apprise_url: str):
#         """
#         Args:
#             apprise_url: Apprise-style ntfy URL (e.g., ntfys://user:pass@host/topic)
#         """
#         self.url, self.auth = self.parse_apprise_ntfy_url(apprise_url)

#     @staticmethod
#     def parse_apprise_ntfy_url(
#         apprise_url: str,
#     ) -> tuple[Optional[str], Optional[tuple[str, str]]]:
#         """
#         Parse an Apprise-style ntfy URL and return (direct_url, (user, pass)) tuple if credentials exist.
#         """
#         if not apprise_url:
#             return None, None
#         parsed = urlparse(apprise_url)
#         # Scheme: ntfy/ntfys -> http/https
#         scheme = "https" if parsed.scheme == "ntfys" else "http"
#         netloc = parsed.hostname
#         port = f":{parsed.port}" if parsed.port else ""
#         path = parsed.path or ""
#         # Credentials
#         username = unquote(parsed.username) if parsed.username else None
#         password = unquote(parsed.password) if parsed.password else None
#         auth = (username, password) if username and password else None
#         # Compose URL
#         direct_url = f"{scheme}://{netloc}{port}{path}"
#         return direct_url, auth

#     def send(
#         self, title: str, message: str, channels: list[str], **kwargs: Any
#     ) -> None:
#         """
#         Send a notification directly to ntfy using HTTP POST with markdown support.
#         Args:
#             title: The notification title.
#             message: The notification body.
#             channels: List of channel names (should include "ntfy-direct" if using this notifier)
#             kwargs: Extra arguments for the notifier (e.g., markdown, tags, priority, etc.)
#         """
#         logging.info("[ntfy-direct] send() called with title='%s'", title)

#         if "ntfy-direct" not in channels or not self.url:
#             return

#         parsed = urlparse(self.url)
#         base_url = f"{parsed.scheme}://{parsed.hostname}{f':{parsed.port}' if parsed.port else ''}"
#         topic = kwargs.get("ntfy_topic") or parsed.path.strip("/").split("/")[-1]
#         url_to_use = f"{base_url}/{topic}"

#         headers = {
#             "Title": title,
#             "X-Markdown": "true",
#         }

#         for k, v in kwargs.items():
#             if k.startswith("X-"):
#                 headers[k] = v

#         try:
#             resp = requests.post(
#                 url_to_use,
#                 data=message.encode("utf-8"),
#                 headers=headers,
#                 timeout=5,
#                 auth=self.auth,
#             )
#             if not resp.ok:
#                 logging.error(
#                     "ntfy-direct failed: status=%s url=%s response=%s",
#                     resp.status_code,
#                     url_to_use,
#                     resp.text,
#                 )
#             else:
#                 logging.info(
#                     "[ntfy-direct] Notification posted successfully: status=%s url=%s",
#                     resp.status_code,
#                     url_to_use,
#                 )
#         except Exception as e:
#             logging.error("ntfy-direct exception: url=%s error=%s", url_to_use, e)
