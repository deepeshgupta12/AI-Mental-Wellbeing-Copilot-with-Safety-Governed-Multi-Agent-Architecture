#!/usr/bin/env bash
set -euo pipefail

echo "Starting local infrastructure..."
docker compose up -d postgres redis

echo "Local infrastructure is up."
docker compose ps