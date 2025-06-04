# notifiq

A modular, extensible notification routing hub for Kubernetes and cloud-native environments. notifiq consumes messages from RabbitMQ and dispatches notifications to multiple channels (Ntfy, Discord, Email, Mattermost, Loki, etc.) with structured JSON logging and health endpoints for observability.

## Features

- Modular notification routing (add new notifiers easily)
- RabbitMQ consumer with credential/env support
- Apprise integration for multi-channel notifications
- **Direct ntfy integration with markdown support (ntfy-direct channel)**
- Structured JSON logging (Loki-friendly)
- Health (`/healthz`) and readiness (`/readyz`) endpoints for Kubernetes
- Dockerfile and Compose for easy deployment
- Graceful shutdown handling
- Example pytest smoke test

---

## ntfy-direct Channel & Markdown Support

notifiq supports sending notifications directly to [ntfy](https://ntfy.sh) using the `ntfy-direct` channel. This allows you to:

- Use the `X-Markdown: true` header for beautiful, styled messages (Apprise does not support this).
- Use the same `APPRISE_NTFY_URL` environment variable for both Apprise and direct ntfy notifications—no need for duplicate configuration.

**How to Use:**

1. **Set your Apprise ntfy URL (with optional credentials):**

   ```sh
   export APPRISE_NTFY_URL="ntfys://user:password@ntfy.example.com/mytopic"
   # or without auth:
   export APPRISE_NTFY_URL="ntfys://ntfy.example.com/mytopic"
   ```

   - `ntfy` = http, `ntfys` = https
   - Credentials are optional but supported for secured topics.

2. **Specify the `ntfy-direct` channel in your message:**
   - Example: `{ "channels": ["ntfy-direct"] }`
3. **Markdown formatting:**
   - By default, messages sent via `ntfy-direct` will include the `X-Markdown: true` header, enabling markdown rendering in ntfy clients.
   - You can add custom headers by passing them in the `headers` argument (as a dict) to the notification payload.

> **Note:** Markdown rendering support may vary by ntfy client. The official web and Android clients support markdown, but the iOS/iPad app may not (or may have limited support), which could result in raw markdown (e.g., `**bold**`) being displayed instead of formatted text.

**Example Python usage:**

```python
# Dispatch a markdown notification
send_args = {
    "title": "*Server Down*",
    "message": "**Alert:** _The server is unreachable!_",
    "channels": ["ntfy-direct"],
    # Optionally add more ntfy headers
    "headers": {"X-Priority": "urgent"}
}
dispatch_notification(**send_args)
```

**Benefits:**

- Rich message formatting with markdown
- No extra environment variables needed—just set `APPRISE_NTFY_URL`
- Supports authentication for private ntfy topics

---

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

## Dynamic Channel/Topic Routing

You can override the default Mattermost channel or Ntfy topic for each message by including `mattermost_channel` or `ntfy_topic` in your message payload. This allows you to send notifications to different destinations dynamically.

**Example message JSON:**

```json
{
  "title": "Alert",
  "message": "Something happened",
  "channels": ["ntfy", "mattermost"],
  "ntfy_topic": "devops-updates",
  "mattermost_channel": "devops"
}
```

- For Ntfy: `ntfy_topic` will replace the topic in the Apprise URL for this message only.
- For Mattermost: `mattermost_channel` will add or replace the `channel` query parameter in the Apprise URL for this message only.
- If not specified, the default from your environment is used.

## Health & Readiness

- `GET /healthz` — always returns 200
- `GET /readyz` — returns 200 only if RabbitMQ is reachable

## Testing

Run the smoke test:

```sh
pytest tests/
```

## Future Features

- Add prometheus metrics
- Add slack notifications
- Add support for multiple notifiers (e.g., ntfy topics, mattermost channels, etc.)
- Add support for multiple RabbitMQ queues

## License

MIT License — see [LICENSE](LICENSE)
