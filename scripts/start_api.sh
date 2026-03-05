#!/bin/bash
# Inicializa banco + seed admin + inicia API
cd "$(dirname "$0")/.."
source .venv/bin/activate
python -m api.seed
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
