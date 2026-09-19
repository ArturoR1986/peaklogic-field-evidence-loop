FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    MAX_UPLOAD_BYTES=10485760 \
    TRACE_PATH=/tmp/peaklogic-evidence-trace.jsonl

RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

EXPOSE 8080

CMD ["python", "-m", "peaklogic_field_evidence.service"]
