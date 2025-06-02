import json
from src.logging_config import setup_logging

setup_logging()
import logging
import pika
from src.config import Config
from src.routing import get_target_notifiers
from src.notifiers.apprise_notifier import AppriseNotifier
from src.notifiers.loki_notifier import LokiNotifier
from src.health import start_health_server

# Initialize config
config = Config()

# Initialize notifiers
notifiers = {}
# Apprise-based notifiers (ntfy, discord, email, etc)
if any(config.apprise_urls.values()):
    notifiers["apprise"] = AppriseNotifier(config.apprise_urls)
# Loki notifier
if config.loki_url:
    notifiers["loki"] = LokiNotifier(config.loki_url)


def dispatch_notification(title, message, channels):
    # Route to correct notifier(s)
    apprise_channels = []
    loki_needed = False
    for channel in channels:
        if channel == "loki":
            loki_needed = True
        elif config.apprise_urls.get(channel):
            apprise_channels.append(channel)
        else:
            logging.warning(f"No notifier configured for channel: {channel}")
    # Send via Apprise if needed
    if apprise_channels and "apprise" in notifiers:
        notifiers["apprise"].send(title, message, channels=apprise_channels)
    # Send via Loki if needed
    if loki_needed and "loki" in notifiers:
        notifiers["loki"].send(title, message)


def callback(ch, method, properties, body):
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
    # RabbitMQ connection
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
