from typing import Any

from src.logging_config import setup_logging

setup_logging()


def get_target_notifiers(message: dict[str, Any]) -> list[str]:
    """
    Determine which notifiers to use for a given message.
    Args:
        message: The notification message dict (from RabbitMQ)
    Returns:
        List of channel names (e.g., ["ntfy", "loki"])
    """
    channels = message.get("channels")
    if not channels:
        # Default to ntfy (Apprise)
        return ["ntfy"]
    if isinstance(channels, str):
        # Allow comma-separated string
        return [c.strip() for c in channels.split(",") if c.strip()]
    return channels if isinstance(channels, list) else ["ntfy"]
