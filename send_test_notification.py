import argparse
import json
import os

import pika


def main():
    parser = argparse.ArgumentParser(
        description="Send a test notification to RabbitMQ."
    )
    parser.add_argument(
        "--title", default="Test Notification", help="Notification title"
    )
    parser.add_argument(
        "--message",
        default="Hello from the producer script!",
        help="Notification message",
    )
    parser.add_argument(
        "--channels",
        default="ntfy",
        help="Comma-separated list of channels (e.g. ntfy,discord,loki)",
    )
    args = parser.parse_args()

    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "localhost")
    rabbitmq_port = int(os.environ.get("RABBITMQ_PORT", 5672))
    rabbitmq_user = os.environ.get("RABBITMQ_USER", "guest")
    rabbitmq_pass = os.environ.get("RABBITMQ_PASS", "guest")
    rabbitmq_queue = os.environ.get("RABBITMQ_QUEUE", "alerts")

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)

    msg = {
        "title": args.title,
        "message": args.message,
        "channels": [c.strip() for c in args.channels.split(",") if c.strip()],
    }

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitmq_host, port=rabbitmq_port, credentials=credentials
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=rabbitmq_queue, durable=True)
    channel.basic_publish(
        exchange="",
        routing_key=rabbitmq_queue,
        body=json.dumps(msg),
        properties=pika.BasicProperties(delivery_mode=2),  # make message persistent
    )
    print(f"Sent: {msg}")
    connection.close()


if __name__ == "__main__":
    main()
