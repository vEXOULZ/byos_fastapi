# syntax=docker/dockerfile:1

FROM python:3.12-slim

# Same interpreter settings the upstream kata-compose.yaml sets.
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF_8:replace \
    PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# The app resolves its writable tree (db, logs, ssl, generated assets) to
# <repo root>/var. Created here so a named volume mounted at /app/var inherits
# ownership; drop the useradd/USER lines if you would rather run as root.
RUN useradd --uid 1000 --create-home --home-dir /home/trmnl trmnl \
 && mkdir -p /app/var \
 && chown -R trmnl:trmnl /app/var

USER trmnl

EXPOSE 4567

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD ["python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:4567/status', timeout=5)"]

CMD ["python3", "-u", "-m", "trmnl_server"]
