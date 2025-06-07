import os
import threading
from typing import Literal

import pika
from flask import Flask, Response, jsonify

from src.logging_config import setup_logging

setup_logging()

from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

app = Flask(__name__)


@app.route("/metrics")
def metrics():
    """
    Prometheus metrics endpoint.
    """
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/healthz")
def healthz() -> tuple[Response, Literal[200]]:
    """
    Health check endpoint.
    """
    return jsonify(status="ok"), 200


# @app.route("/readyz")
# def readyz() -> tuple[Response, Literal[200]]:
#     """
#     Readiness check endpoint.
#     """
#     return jsonify(status="ready"), 200


@app.route("/readyz")
def readyz() -> tuple[Response, int]:
    """
    Readiness check endpoint: only ready if RabbitMQ is reachable.
    """
    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "localhost")
    rabbitmq_port = int(os.environ.get("RABBITMQ_PORT", 5672))
    rabbitmq_user = os.environ.get("RABBITMQ_USER", "guest")
    rabbitmq_pass = os.environ.get("RABBITMQ_PASS", "guest")
    rabbitmq_vhost = os.environ.get("RABBITMQ_VHOST", "/")

    try:
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
        params = pika.ConnectionParameters(
            host=rabbitmq_host,
            port=rabbitmq_port,
            virtual_host=rabbitmq_vhost,
            credentials=credentials,
            connection_attempts=1,
            socket_timeout=2,
        )
        conn = pika.BlockingConnection(params)
        conn.close()
        return jsonify(status="ready"), 200
    except Exception as e:
        return jsonify(status="not ready", reason=str(e)), 503


def start_health_server(port: int = 8080) -> threading.Thread:
    """
    Start the health server.
    Args:
        port: Port to run the health server on.
    Returns:
        Thread: Thread running the health server.
    """
    thread = threading.Thread(
        target=app.run, kwargs={"host": "0.0.0.0", "port": port}, daemon=True
    )
    thread.start()
    return thread
