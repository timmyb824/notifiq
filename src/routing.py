from typing import List, Dict, Any


def get_target_notifiers(message: Dict[str, Any]) -> List[str]:
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


# For advanced routing, add logic here (e.g., by queue, type, or source)
