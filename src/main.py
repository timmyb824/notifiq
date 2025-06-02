import json
import logging

import pika
from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from src.config import Config
from src.health import start_health_server
from src.logging_config import setup_logging
from src.notifiers.apprise_notifier import AppriseNotifier
from src.notifiers.loki_notifier import LokiNotifier
from src.notifiers.mattermost_notifier import MattermostNotifier
from src.routing import get_target_notifiers

setup_logging()

# Start health/readiness endpoint
start_health_server()

# Initialize config
config = Config()

# Initialize notifiers
notifiers = {}
notifiers["apprise"] = AppriseNotifier(config.apprise_urls)
if config.apprise_urls.get("mattermost"):
    notifiers["mattermost"] = MattermostNotifier(config.apprise_urls["mattermost"])
# Loki notifier
if config.loki_url:
    notifiers["loki"] = LokiNotifier(config.loki_url)


def dispatch_notification(title: str, message: str, channels: list[str]):
    """
    Dispatch a notification to the appropriate notifier(s).
    Args:
        title: Notification title
        message: Notification message
        channels: List of channels to notify
    """
    apprise_channels = []
    loki_needed = False
    mattermost_needed = False
    for channel in channels:
        if channel == "loki":
            loki_needed = True
        elif channel == "mattermost":
            mattermost_needed = True
        else:
            apprise_channels.append(channel)
    if apprise_channels:
        notifiers["apprise"].send(title, message, apprise_channels)
    if mattermost_needed and "mattermost" in notifiers:
        notifiers["mattermost"].send(title, message, ["mattermost"])
    if loki_needed and "loki" in notifiers:
        notifiers["loki"].send(title, message)


# It is standard practice to include the unused arguments in the callback even if they are not used
def callback(
    ch: Channel,
    method: Basic.Deliver,
    properties: BasicProperties,
    body: bytes,
):
    """
    Callback function for RabbitMQ message processing.
    Args:
        ch: RabbitMQ channel
        method: RabbitMQ method
        properties: RabbitMQ properties
        body: Message body
    """
    try:
        msg = json.loads(body)
        title = msg.get("title", "Notification")
        message = msg.get("message", str(msg))
        channels = get_target_notifiers(msg)
        logging.info(f"Dispatching '{title}' to {channels}: {message}")
        dispatch_notification(title, message, channels)
    except Exception:
        logging.exception("Failed to process message")


def main():
    """
    Main entry point for the application.
    """
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
    channel.start_consuming()


if __name__ == "__main__":
    main()
