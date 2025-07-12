import contextlib

GOTIFY_PRIORITY_MAP = {
    "min": "low",
    "low": "low",
    "moderate": "moderate",
    "normal": "normal",
    "default": "normal",
    "high": "high",
    "critical": "emergency",
    "emergency": "emergency",
    "max": "emergency",
}


def map_gotify_priority(priority: str) -> str:
    """
    Map a string-based priority to a Gotify priority.
    Args:
        priority: The priority to map.
    Returns:
        The mapped priority.
    """
    p = priority.strip().lower()
    return GOTIFY_PRIORITY_MAP.get(p, "normal")


NTFY_PRIORITY_MAP = {
    "min": "min",
    "low": "low",
    "moderate": "low",
    "normal": "default",
    "default": "default",
    "high": "high",
    "critical": "max",
    "emergency": "max",
    "max": "max",
}


def map_ntfy_priority(priority: str) -> str:
    """
    Map a string-based priority to a ntfy priority.
    Args:
        priority: The priority to map.
    Returns:
        The mapped priority.
    """
    p = priority.strip().lower()
    return NTFY_PRIORITY_MAP.get(p, "default")


PUSHOVER_PRIORITY_MAP = {
    "min": -2,
    "lowest": -2,
    "low": -1,
    "moderate": -1,
    "normal": 0,
    "default": 0,
    "medium": 0,
    "high": 1,
    "critical": 1,
    "emergency": 2,
    "max": 2,
}


def map_pushover_priority(priority: str) -> int:
    """
    Map a string-based priority to a Pushover integer priority.
    Args:
        priority: The priority to map (string or int-like string).
    Returns:
        The mapped integer priority.
    """
    if priority is None:
        return 0
    with contextlib.suppress(Exception):
        # If already an int or int-like string
        return int(priority)
    p = priority.strip().lower()
    return PUSHOVER_PRIORITY_MAP.get(p, 0)
