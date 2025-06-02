from src.logging_config import setup_logging

setup_logging()
import logging
from .base import BaseNotifier
from typing import Any


class LokiNotifier(BaseNotifier):
    def __init__(self, url: str):
        """
        Args:
            url: Loki push API endpoint.
        """
        self.url = url

    def send(self, title: str, message: str, **kwargs: Any) -> None:
        # TODO: Implement actual Loki push logic here
        logging.info(
            f"[LokiNotifier] Would send to Loki at {self.url}: {title} - {message}"
        )
        # Example: requests.post(self.url, json=payload)
        pass
