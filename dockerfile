FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /install.sh
RUN sh /install.sh

COPY pyproject.toml .
COPY uv.lock .

RUN /root/.local/bin/uv sync --frozen


FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd -m appuser

COPY --from=builder /app /app
COPY src ./src
COPY run.sh .

RUN chmod +x run.sh && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["./run.sh"]
