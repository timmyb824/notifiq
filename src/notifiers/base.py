from abc import ABC, abstractmethod
from typing import Any


class BaseNotifier(ABC):
    """
    Abstract base class for all notifiers.
    """

    @abstractmethod
    def send(
        self, title: str, message: str, channels: list[str], **kwargs: Any
    ) -> None:
        """
        Send a notification.
        Args:
            title: The notification title.
            message: The notification body.
            channels: List of channel names (e.g., ["ntfy", "loki"])
            kwargs: Extra arguments for the notifier.
        """
        pass
