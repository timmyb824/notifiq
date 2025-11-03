import argparse
import json
import logging
import signal
import sys
import time
from typing import Any

import pika
from pika.channel import Channel
from pika.spec import Basic, BasicProperties
from prometheus_client import Counter, Histogram

from src.config import Config
from src.health import start_health_server
from src.logging_config import setup_logging
from src.notifiers.apprise_notifier import AppriseNotifier
from src.notifiers.mattermost_notifier import MattermostNotifier
from src.notifiers.ntfy_direct_notifier import NtfyDirectNotifier
from src.notifiers.pushover_direct_notifier import PushoverDirectNotifier
from src.routing import get_target_notifiers

setup_logging()

# Prometheus metrics
MESSAGES_PICKED_UP = Counter(
    "notifiq_messages_picked_total",
    "Total number of messages picked up from RabbitMQ.",
    labelnames=["channel"],
)
MESSAGES_DELIVERED = Counter(
    "notifiq_messages_delivered_total",
    "Total number of messages successfully delivered.",
    labelnames=["channel"],
)
MESSAGES_ERRORS = Counter(
    "notifiq_message_errors_total",
    "Total number of message processing or delivery errors.",
    labelnames=["channel"],
)
MESSAGE_PROCESSING_TIME = Histogram(
    "notifiq_message_processing_seconds",
    "Time spent processing and delivering a message (seconds).",
    labelnames=["channel"],
)

start_health_server()

config = Config()

shutdown_requested = False

notifiers = {}
notifiers["apprise"] = AppriseNotifier(config.apprise_urls)
if ntfy_url := config.apprise_urls.get("ntfy"):
    notifiers["ntfy-direct"] = NtfyDirectNotifier(ntfy_url)  # type: ignore
if mattermost_url := config.apprise_urls.get("mattermost"):
    notifiers["mattermost"] = MattermostNotifier(mattermost_url)  # type: ignore

# Initialize multiple Pushover notifiers (one per application)
pushover_notifiers = {}
logging.info(
    f"Found {len(config.pushover_apps)} Pushover app(s) in config: {list(config.pushover_apps.keys())}"
)
for app_id, pushover_url in config.pushover_apps.items():
    pushover_notifiers[app_id] = PushoverDirectNotifier(pushover_url)
    logging.info(f"Initialized Pushover notifier for app: {app_id}")

# For backward compatibility: if only one Pushover app exists, register it as "pushover-direct"
if len(pushover_notifiers) == 1:
    notifiers["pushover-direct"] = list(pushover_notifiers.values())[0]
    logging.info(
        "Single Pushover app detected, registered as 'pushover-direct' for backward compatibility"
    )


def dispatch_notification(title: str, message: str, channels: list[str], **kwargs):
    """
    Dispatch a notification to the appropriate notifier(s).
    Args:
        title: Notification title
        message: Notification message
        channels: List of channels to notify
        kwargs: Extra arguments for dynamic routing (e.g., ntfy_topic, mattermost_channel, priority, pushover_app)
    """
    # For Prometheus timing
    prom_start_time = kwargs.pop("_prom_start_time", None)
    apprise_channels = []
    ntfy_direct_needed = False
    mattermost_needed = False
    pushover_direct_needed = False
    try:
        for channel in channels:
            if channel == "mattermost":
                mattermost_needed = True
            elif channel == "ntfy-direct":
                ntfy_direct_needed = True
            elif channel == "pushover-direct":
                pushover_direct_needed = True
            else:
                apprise_channels.append(channel)
        if apprise_channels:
            notifiers["apprise"].send(title, message, apprise_channels, **kwargs)
        if mattermost_needed and "mattermost" in notifiers:
            notifiers["mattermost"].send(title, message, ["mattermost"], **kwargs)
        if ntfy_direct_needed and "ntfy-direct" in notifiers:
            notifiers["ntfy-direct"].send(title, message, ["ntfy-direct"], **kwargs)
        if pushover_direct_needed:
            # Route to specific Pushover app if pushover_app is specified
            pushover_app = kwargs.get("pushover_app")
            logging.info(
                f"Pushover routing: pushover_app={pushover_app}, available_apps={list(pushover_notifiers.keys())}, has_default={'pushover-direct' in notifiers}"
            )
            if pushover_app and pushover_app in pushover_notifiers:
                # Use the specified Pushover app
                pushover_notifiers[pushover_app].send(
                    title, message, ["pushover-direct"], **kwargs
                )
                logging.info(f"Sent to Pushover app: {pushover_app}")
            elif "pushover-direct" in notifiers:
                # Fall back to single/default notifier for backward compatibility
                logging.info("Using backward-compatible 'pushover-direct' notifier")
                notifiers["pushover-direct"].send(
                    title, message, ["pushover-direct"], **kwargs
                )
            elif pushover_notifiers:
                # If multiple apps exist but no app specified, prefer "default" (from APPRISE_PUSHOVER_URL)
                if "default" in pushover_notifiers:
                    logging.warning(
                        "No pushover_app specified, using 'default' app from APPRISE_PUSHOVER_URL"
                    )
                    pushover_notifiers["default"].send(
                        title, message, ["pushover-direct"], **kwargs
                    )
                else:
                    # Fall back to first app if no default exists
                    default_app = next(iter(pushover_notifiers))
                    pushover_notifiers[default_app].send(
                        title, message, ["pushover-direct"], **kwargs
                    )
                    logging.warning(
                        f"No pushover_app specified and no 'default' app found, using: {default_app}"
                    )
            else:
                logging.error("Pushover requested but no Pushover notifiers configured")
        for channel in channels:
            MESSAGES_DELIVERED.labels(channel=channel).inc()
        if prom_start_time is not None:
            for channel in channels:
                MESSAGE_PROCESSING_TIME.labels(channel=channel).observe(
                    time.time() - prom_start_time
                )
    except Exception:
        for channel in channels if "channels" in locals() else ["unknown"]:
            MESSAGES_ERRORS.labels(channel=channel).inc()
        logging.exception("Error delivering notification")


# It is standard practice to include the unused arguments in the callback even if they are not used
def callback(
    ch: Channel,
    method: Basic.Deliver,
    properties: BasicProperties,
    body: bytes,
):  # sourcery skip: extract-method
    """
    Callback function for RabbitMQ message processing.
    Args:
        ch: RabbitMQ channel
        method: RabbitMQ method
        properties: RabbitMQ properties
        body: Message body
    """
    start_time = time.time()
    try:
        msg = json.loads(body)
        title = msg.get("title", "Notification")
        message = msg.get("message", str(msg))
        channels = get_target_notifiers(msg)
        # Pass all extra fields for dynamic routing (e.g., ntfy_topic, mattermost_channel)
        extra = {
            k: v for k, v in msg.items() if k not in {"title", "message", "channels"}
        }
        logging.info(f"Dispatching '{title}' to {channels}: {message}")
        # Increment picked up for each channel
        for channel in channels:
            MESSAGES_PICKED_UP.labels(channel=channel).inc()
        dispatch_notification(
            title, message, channels, **extra, _prom_start_time=start_time
        )
    except Exception:
        for channel in channels if "channels" in locals() else ["unknown"]:
            MESSAGES_ERRORS.labels(channel=channel).inc()
        logging.exception("Failed to process message")


def handle_shutdown(signum: int, frame: Any) -> None:
    global shutdown_requested  # pylint: disable=global-statement
    logging.info(f"Received signal {signum}, shutting down gracefully...")
    shutdown_requested = True


def version():
    """
    Print the version of the application.
    """
    parser = argparse.ArgumentParser(
        description="Print the version of the application."
    )
    parser.add_argument(
        "--version", action="store_true", help="Print the version of the application."
    )
    args = parser.parse_args()
    if args.version:
        try:
            try:
                from importlib.metadata import (  # pylint: disable=redefined-outer-name
                    PackageNotFoundError,
                    version,
                )
            except ImportError:
                from importlib_metadata import (  # pyright: ignore
                    PackageNotFoundError,
                    version,
                )

            try:
                notifiq_version = version("notifiq")
                print(f"notifiq {notifiq_version}")
            except PackageNotFoundError:
                print("[red]Package not found. Did you install it?[/red]")
        except ImportError:
            print("[red]importlib.metadata and importlib_metadata not found[/red]")
        sys.exit(0)


def main():
    """
    Main entry point for the application.
    """
    version()
    credentials = pika.PlainCredentials(config.rabbitmq_user, config.rabbitmq_pass)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=config.rabbitmq_host,
            port=config.rabbitmq_port,
            virtual_host=getattr(config, "rabbitmq_vhost", "/"),
            credentials=credentials,
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=config.rabbitmq_queue, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=config.rabbitmq_queue, on_message_callback=callback, auto_ack=True
    )
    logging.info(f"Listening for messages on queue '{config.rabbitmq_queue}'...")

    # Register signal handlers
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    try:
        while not shutdown_requested:
            connection.process_data_events(time_limit=1)
    except Exception as e:
        logging.error(f"Error in consumer loop: {e}")
    finally:
        try:
            if channel.is_open:
                channel.close()
            if connection.is_open:
                connection.close()
        except Exception as e:
            logging.warning(f"Error closing RabbitMQ connection: {e}")
        logging.info("Shutdown complete.")
        sys.exit(0)


if __name__ == "__main__":
    main()
