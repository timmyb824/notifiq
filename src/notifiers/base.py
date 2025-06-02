from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseNotifier(ABC):
    """
    Abstract base class for all notifiers.
    """
    @abstractmethod
    def send(self, title: str, message: str, **kwargs: Any) -> None:
        """
        Send a notification.
        Args:
            title: The notification title.
            message: The notification body.
            kwargs: Extra arguments for the notifier.
        """
        pass
