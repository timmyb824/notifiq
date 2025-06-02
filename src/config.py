import os
from typing import Dict, Optional


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

        # Apprise notifier URLs (channels)
        self.apprise_urls: Dict[str, Optional[str]] = {
            "ntfy": os.environ.get("APPRISE_NTFY_URL"),
            "discord": os.environ.get("APPRISE_DISCORD_URL"),
            "email": os.environ.get("APPRISE_EMAIL_URL"),
            "mattermost": os.environ.get("APPRISE_MATTERMOST_URL"),
        }

        # Loki notifier URL
        self.loki_url = os.environ.get("LOKI_PUSH_URL")
