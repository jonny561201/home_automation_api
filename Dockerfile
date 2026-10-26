FROM python:3.13-slim AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


FROM python:3.13-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --no-create-home app

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

WORKDIR /app
COPY svc ./svc
COPY app.py sse_app.py settings.production.json ./
COPY deployment/container ./deployment/container

ENV PYTHON_ENVIRONMENT=production
USER app
EXPOSE 8000 8001

CMD ["uwsgi", "--ini", "deployment/container/api.ini"]
