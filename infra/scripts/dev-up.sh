#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "Starting local infrastructure..."
docker compose up -d postgres redis

echo "Waiting for containers to report healthy..."
for service in mwc_postgres mwc_redis; do
  until [ "$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}unknown{{end}}' "$service")" = "healthy" ]; do
    echo "Waiting for $service..."
    sleep 2
  done
done

echo "Local infrastructure is up and healthy."
docker compose ps