# Multi-stage build for Ollama-powered LLM Chatbot
# Stage 1: Builder
FROM python:3.11-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Development with Ollama
FROM ollama/ollama:latest AS development

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Copy startup script
COPY docker/start_services.sh /start_services.sh
RUN chmod +x /start_services.sh

# Create necessary directories
RUN mkdir -p data models logs config

# Copy model configuration
COPY config/models.yml /app/config/models.yml

# Expose ports
EXPOSE 8000 11434

# Default command for development
CMD ["/start_services.sh"]

# Stage 3: Production
FROM ollama/ollama:latest AS production

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory and copy application
WORKDIR /app
COPY --chown=appuser:appuser . .

# Copy startup script
COPY --chown=appuser:appuser docker/start_services.sh /start_services.sh
RUN chmod +x /start_services.sh

# Create directories and set permissions
RUN mkdir -p data models logs config && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8000 11434

# Production command
CMD ["/start_services.sh"]
