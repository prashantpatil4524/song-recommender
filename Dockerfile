# ── Stage 1: build & train ──────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy source
COPY . .

# train model (produces backend/models/*.pkl)
RUN python backend/train_model.py


# ── Stage 2: runtime ────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app + pre-trained models from builder
COPY --from=builder /app /app

EXPOSE 5000
ENV FLASK_ENV=production
ENV PYTHONPATH=/app/backend

CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 "backend.app:create_app()"


