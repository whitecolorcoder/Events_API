# FROM python:3.12-slim

# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1

# WORKDIR /app

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#  && rm -rf /var/lib/apt/lists/*

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# EXPOSE 8000

# CMD ["bash", "./run.sh"]


# ---------- Stage 1: Builder ----------
# ---------- Stage 1: Builder ----------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install curl (required for uv installer)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv
ADD https://astral.sh/uv/install.sh /install.sh
RUN sh /install.sh

# Copy metadata
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies into .venv
RUN /root/.local/bin/uv sync --frozen


# ---------- Stage 2: Final image ----------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Create non-root user
RUN useradd -m appuser

# Copy only necessary files
COPY --from=builder /app /app
COPY src ./src
COPY run.sh .

# Permissions
RUN chmod +x run.sh && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["./run.sh"]
