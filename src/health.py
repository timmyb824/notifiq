from src.logging_config import setup_logging

setup_logging()
from flask import Flask
from threading import Thread
from flask import jsonify

app = Flask(__name__)


@app.route("/healthz")
def healthz():
    return jsonify(status="ok"), 200


@app.route("/readyz")
def readyz():
    # Extend this to check RabbitMQ connection if desired
    return jsonify(status="ready"), 200


def start_health_server(port=8080):
    thread = threading.Thread(
        target=app.run, kwargs={"host": "0.0.0.0", "port": port}, daemon=True
    )
    thread.start()
    return thread
