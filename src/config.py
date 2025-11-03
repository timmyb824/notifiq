import os
from typing import Optional


class Config:
    """
    Central configuration loader for the notification hub.
    """

    def __init__(self):
        # RabbitMQ
        self.rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
        self.rabbitmq_port = int(os.environ.get("RABBITMQ_PORT", 5672))
        self.rabbitmq_user = os.environ.get("RABBITMQ_USER", "guest")
        self.rabbitmq_pass = os.environ.get("RABBITMQ_PASS", "guest")
        self.rabbitmq_queue = os.environ.get("RABBITMQ_QUEUE", "alerts")
        self.rabbitmq_vhost = os.environ.get("RABBITMQ_VHOST", "/")

        # Dynamically build Apprise notifier URLs (channels)
        self.apprise_urls: dict[str, Optional[str]] = {}
        # Support multiple Pushover applications with identifiers
        self.pushover_apps: dict[str, str] = {}

        for key, value in os.environ.items():
            if key.startswith("APPRISE_") and key.endswith("_URL") and value:
                # Extract provider name from key
                middle_part = key[len("APPRISE_") : -len("_URL")]

                # Check if this is a Pushover app with identifier (e.g., APPRISE_PUSHOVER_INFRA_URL)
                if middle_part.startswith("PUSHOVER_"):
                    app_identifier = middle_part[len("PUSHOVER_") :].lower()
                    self.pushover_apps[app_identifier] = value
                else:
                    # Regular provider (ntfy, mattermost, etc.)
                    provider = middle_part.lower()
                    self.apprise_urls[provider] = value

        # For backward compatibility: if APPRISE_PUSHOVER_URL exists (no app identifier),
        # add it as "default" app
        if "APPRISE_PUSHOVER_URL" in os.environ and os.environ["APPRISE_PUSHOVER_URL"]:
            self.pushover_apps["default"] = os.environ["APPRISE_PUSHOVER_URL"]
