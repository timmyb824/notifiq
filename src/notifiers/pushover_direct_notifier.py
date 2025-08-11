import logging
from typing import Any, Optional
from urllib.parse import unquote, urlparse

import httpx

from src.logging_config import setup_logging
from src.notifiers.base import BaseNotifier
from src.notifiers.priority_mappings import map_pushover_priority

setup_logging()


class PushoverDirectNotifier(BaseNotifier):
    """
    Notifier for sending messages directly to Pushover using HTTP requests, with support for all Pushover parameters (including html=1) and Apprise-style URL parsing.
    """

    def __init__(self, apprise_url: str):
        """
        Args:
            apprise_url: Apprise-style pushover URL (e.g., pover://token@user)
        """
        self.api_url = "https://api.pushover.net/1/messages.json"
        self.token, self.user = self.parse_apprise_pushover_url(apprise_url)
        if not self.token or not self.user:
            raise ValueError(
                "PushoverDirectNotifier: Both token and user key must be provided in the apprise_url."
            )

    @staticmethod
    def parse_apprise_pushover_url(
        apprise_url: str,
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Parse Apprise-style pushover URL and return (token, user) tuple.
        Example: pover://USER_KEY@TOKEN
        """
        if not apprise_url:
            return None, None
        parsed = urlparse(apprise_url)
        user = unquote(parsed.username) if parsed.username else None
        token = unquote(parsed.hostname) if parsed.hostname else None
        # If user is actually in the path (e.g., pover://TOKEN/USER)
        if not user and parsed.path:
            user = parsed.path.strip("/")
        return token, user

    def send(
        self,
        title: str,
        message: str,
        channels: list[str],
        **kwargs: Any,
    ) -> None:  # sourcery skip: extract-method
        """
        Send a notification directly to Pushover using HTTP POST.
        Args:
            title: The notification title (can include emojis).
            message: The notification body.
            channels: List of channel names (should include "pushover-direct" if using this notifier).
            kwargs: Extra Pushover params (html, priority, sound, attachment, pushover_device, etc.)
                   pushover_device: List of device names or single device name string.
                                  If a list is provided, it will be joined with commas.
        """
        print("[PUSHOVER SEND CALLED]")
        logging.info("[pushover-direct] send() called with title='%s'", title)

        if "pushover-direct" not in channels:
            return

        data = {
            "token": self.token,
            "user": self.user,
            "message": message,
        }
        if title:
            data["title"] = title

        # Always set html=1 unless explicitly overridden
        data["html"] = kwargs.get("html", 1)

        # Handle priority mapping (string or int)
        if "priority" in kwargs:
            data["priority"] = map_pushover_priority(kwargs["priority"])

        # Handle pushover_device parameter (list -> comma-separated string)
        if "pushover_device" in kwargs:
            device_list = kwargs["pushover_device"]
            if isinstance(device_list, list):
                data["device"] = ",".join(device_list)
            else:
                # If it's already a string, use it directly
                data["device"] = device_list

        # Pass through other supported Pushover params if provided
        for pushover_param in [
            "device",
            "sound",
            "timestamp",
            "url",
            "url_title",
            "ttl",
        ]:
            if pushover_param in kwargs:
                data[pushover_param] = kwargs[pushover_param]

        files = None
        # Attachment support (either via file or base64)
        if "attachment" in kwargs:
            files = {"attachment": kwargs["attachment"]}
        elif "attachment_base64" in kwargs:
            files = {
                "attachment_base64": kwargs["attachment_base64"],
            }
            if "attachment_type" in kwargs:
                data["attachment_type"] = kwargs["attachment_type"]

        try:
            logging.info("[pushover-direct] Sending to URL: %s", self.api_url)
            logging.info("[pushover-direct] Payload: %s", data)
            if files:
                logging.info("[pushover-direct] Files: %s", list(files.keys()))
            resp = httpx.post(
                url=self.api_url,
                data=data,
                files=files,
                timeout=5.0,
            )
            logging.info("[pushover-direct] Response status: %s", resp.status_code)
            logging.info("[pushover-direct] Response text: %s", resp.text)
            if resp.status_code >= 400:
                logging.error(
                    "pushover-direct failed: status=%s response=%s",
                    resp.status_code,
                    resp.text,
                )
            else:
                logging.info(
                    "[pushover-direct] Notification posted successfully: status=%s",
                    resp.status_code,
                )
        except Exception as e:
            logging.error("pushover-direct exception: error=%s", e)
