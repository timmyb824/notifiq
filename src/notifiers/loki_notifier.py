import logging
from typing import Any

from src.logging_config import setup_logging
from src.notifiers.base import BaseNotifier

setup_logging()


# TODO: Implement actual Loki push logic here
# For now, this is just an example of how a custom notifier should be implemented
class LokiNotifier(BaseNotifier):
    """
    Loki notifier.
    """

    def __init__(self, url: str):
        """
        Args:
            url: Loki push API endpoint.
        """
        self.url = url

    def send(self, title: str, message: str, **kwargs: Any) -> None:
        """
        Send a notification to Loki.
        Args:
            title: Notification title.
            message: Notification message.
            kwargs: Extra arguments for the notifier.
        """
        # TODO: Implement actual Loki push logic here
        logging.info(
            f"[LokiNotifier] Would send to Loki at {self.url}: {title} - {message}"
        )
        # Example: requests.post(self.url, json=payload)
        pass
