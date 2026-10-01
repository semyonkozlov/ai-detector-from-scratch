#!/usr/bin/env sh
# Regenerate openapi.yaml and the Python client in client/ from the service app.
set -eu

cd "$(dirname "$0")/.."
PYTHONPATH=src uv run --no-project --with fastapi --with pyyaml \
    python scripts/export_service_openapi.py
uvx openapi-python-client@0.28.2 generate \
    --path openapi.yaml \
    --config client-config.yaml \
    --output-path client \
    --overwrite
rm -rf client/.ruff_cache
