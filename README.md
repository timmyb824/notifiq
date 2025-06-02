# notifiq

A modular, extensible notification routing hub for Kubernetes and cloud-native environments. notifiq consumes messages from RabbitMQ and dispatches notifications to multiple channels (Ntfy, Discord, Email, Mattermost, Loki, etc.) with structured JSON logging and health endpoints for observability.

## Features

- Modular notification routing (add new notifiers easily)
- RabbitMQ consumer with credential/env support
- Apprise integration for multi-channel notifications
- Structured JSON logging (Loki-friendly)
- Health (`/healthz`) and readiness (`/readyz`) endpoints for Kubernetes
- Dockerfile and Compose for easy deployment
- Graceful shutdown handling
- Example pytest smoke test

## Quick Start

1. **Clone the repo:**

   ```sh
   git clone https://github.com/timmyb824/notifiq.git
   cd notifiq
   ```

2. **Configure environment:**

   - Copy `.env.example` to `.envrc` or set environment variables directly.
   - Set your RabbitMQ and Apprise notification URLs.

3. **Run with Docker Compose:**

   ```sh
   docker-compose up --build
   ```

   Or run locally:

   ```sh
   uv sync
   uv run python -m src.main
   ```

4. **Send a test message:**
   Publish a JSON message to the configured RabbitMQ queue.

## Configuration

Set these environment variables:

- `RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USER`, `RABBITMQ_PASS`, `RABBITMQ_QUEUE`
- Apprise URLs: `APPRISE_NTFY_URL`, `APPRISE_DISCORD_URL`, `APPRISE_EMAIL_URL`, `APPRISE_MATTERMOST_URL`, etc.
- `LOKI_PUSH_URL` for Loki notifications
- `VERBOSE=1` for debug logging

See `.env.example` for details.

## Health & Readiness

- `GET /healthz` — always returns 200
- `GET /readyz` — returns 200 only if RabbitMQ is reachable

## Testing

Run the smoke test:

```sh
pytest tests/
```

## License

MIT License — see [LICENSE](LICENSE)
