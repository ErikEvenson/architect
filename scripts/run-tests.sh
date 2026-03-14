#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Running Backend Tests ==="
cd "$PROJECT_DIR/services/backend"
python -m pytest tests/ -v --cov=src --cov-report=term-missing

echo ""
echo "=== Running Frontend Tests ==="
cd "$PROJECT_DIR/services/frontend"
npm test

echo ""
echo "All tests complete."
