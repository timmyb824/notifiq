FROM docker.io/library/python:3.12.10-alpine3.21 AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

ENV UV_PYTHON_DOWNLOADS=0

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app
RUN chmod -R a+r /app

# OLD BUILD STEPS LEFT FOR REFERENCE
# RUN --mount=type=cache,target=/root/.cache/uv \
#     uv sync --frozen --no-install-project --no-dev
# RUN --mount=type=cache,target=/root/.cache/uv \
#     uv sync --frozen --no-dev

WORKDIR /app

# Will fail if lockfile is out of date
RUN uv sync --locked

####################################################################################################

FROM docker.io/library/python:3.12.10-alpine3.21 AS runtime

RUN apk update --no-cache && apk upgrade --no-cache
RUN apk upgrade busybox libcrypto3 libssl3

# Create app user and group
RUN addgroup -S app && adduser -S app -G app

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

USER app

CMD ["python", "-m", "src.main"]
