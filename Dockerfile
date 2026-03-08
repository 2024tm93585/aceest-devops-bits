# ── Stage 1: Build ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Runtime ────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Create non-root user for security
RUN addgroup --system aceest && \
    adduser --system --ingroup aceest aceest

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application source
COPY --chown=aceest:aceest app.py requirements.txt ./

# Create data directory for SQLite database
RUN mkdir -p /app/data && chown -R aceest:aceest /app

USER aceest

ENV PATH="/opt/venv/bin:$PATH" \
    DB_NAME="/app/data/aceest_fitness.db" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["sh", "-c", "python -c 'from app import init_db; init_db()' && python app.py"]
