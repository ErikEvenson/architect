#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Read versions from each service
BACKEND_VERSION=$(grep '^version' "$PROJECT_DIR/services/backend/pyproject.toml" | head -1 | sed 's/.*"\(.*\)".*/\1/')
FRONTEND_VERSION=$(grep '"version"' "$PROJECT_DIR/services/frontend/package.json" | head -1 | sed 's/.*"\([0-9][^"]*\)".*/\1/')

echo "Building Architect images..."
echo "  Backend version:  $BACKEND_VERSION"
echo "  Frontend version: $FRONTEND_VERSION"

# Temp dir for build contexts
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT INT TERM

# --- Backend ---
echo ""
echo "=== Building architect-backend:$BACKEND_VERSION ==="
BACKEND_CTX="$TMPDIR/backend"
mkdir -p "$BACKEND_CTX"
cp "$PROJECT_DIR/services/backend/Dockerfile" "$BACKEND_CTX/"
cp "$PROJECT_DIR/services/backend/requirements.txt" "$BACKEND_CTX/"
cp -r "$PROJECT_DIR/services/backend/src" "$BACKEND_CTX/src"
cp -r "$PROJECT_DIR/knowledge" "$BACKEND_CTX/knowledge"

sudo docker build -t "architect-backend:$BACKEND_VERSION" -t "architect-backend:latest" "$BACKEND_CTX"

# --- Frontend ---
echo ""
echo "=== Building architect-frontend:$FRONTEND_VERSION ==="
FRONTEND_CTX="$TMPDIR/frontend"
mkdir -p "$FRONTEND_CTX"
cp -r "$PROJECT_DIR/services/frontend/." "$FRONTEND_CTX/"
# Remove node_modules if present (shouldn't be, but safety)
rm -rf "$FRONTEND_CTX/node_modules"

sudo docker build -t "architect-frontend:$FRONTEND_VERSION" -t "architect-frontend:latest" "$FRONTEND_CTX"

# --- DB Migrations ---
echo ""
echo "=== Building architect-db-migrations:$BACKEND_VERSION ==="
DB_CTX="$TMPDIR/db"
mkdir -p "$DB_CTX/db"
cp "$PROJECT_DIR/db/Dockerfile" "$DB_CTX/"
cp "$PROJECT_DIR/db/requirements.txt" "$DB_CTX/db/"
cp "$PROJECT_DIR/db/alembic.ini" "$DB_CTX/db/"
cp -r "$PROJECT_DIR/db/alembic" "$DB_CTX/db/alembic"

sudo docker build -t "architect-db-migrations:$BACKEND_VERSION" -t "architect-db-migrations:latest" "$DB_CTX"

echo ""
echo "All images built successfully."
echo "  architect-backend:$BACKEND_VERSION"
echo "  architect-frontend:$FRONTEND_VERSION"
echo "  architect-db-migrations:$BACKEND_VERSION"
