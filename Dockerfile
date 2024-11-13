# Stage 1: Builder Stage
FROM python:3.11-alpine AS builder

ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.8.3

# Install build dependencies
RUN apk update && \
  apk add --no-cache \
  build-base \
  libffi-dev \
  postgresql-dev \
  musl-dev \
  gcc \
  make \
  curl \
  bash

# Install Poetry
RUN pip install poetry==${POETRY_VERSION} \
  && pip install --upgrade pip \
  && poetry config virtualenvs.in-project true

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app


# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install all dependencies
RUN poetry install --no-root --only main

# Copy application code
COPY . .

# Stage 2: Final Image
FROM python:3.11-alpine

ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:/usr/local/bin:$PATH"

# Install runtime dependencies
RUN apk add --no-cache \
  libstdc++ \
  libffi \
  postgresql-client \
  bash

WORKDIR /app

# Copy dependencies and application code from the builder stage
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

# Expose port (optional)
EXPOSE 8000
