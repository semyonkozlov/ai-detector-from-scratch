FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /usr/local/bin/uv

WORKDIR /app
ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    HF_HUB_DISABLE_TELEMETRY=1

COPY requirements-service.txt ./
RUN uv pip install --system --no-cache --index-strategy unsafe-best-match \
    -r requirements-service.txt

COPY src/ai_detector src/ai_detector
COPY scripts/15_classifier-api/download-models.py scripts/15_classifier-api/
RUN python scripts/15_classifier-api/download-models.py --fetch --model modernbert

ENV AI_DETECTOR_MODEL=modernbert \
    AI_DETECTOR_DEVICE=cpu \
    AI_DETECTOR_MAX_TOKENS=2048 \
    HF_HUB_OFFLINE=1

EXPOSE 8080
CMD ["sh", "-c", "exec uvicorn ai_detector.service:app --host 0.0.0.0 --port ${PORT:-8080}"]
