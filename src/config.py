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
        for key, value in os.environ.items():
            if key.startswith("APPRISE_") and key.endswith("_URL") and value:
                provider = key[len("APPRISE_") : -len("_URL")].lower()
                self.apprise_urls[provider] = value

        # Loki notifier URL
        self.loki_url = os.environ.get("LOKI_PUSH_URL")
