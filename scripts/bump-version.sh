#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

SERVICE="${1:?Usage: bump-version.sh <service> <version> (service: backend, frontend, db-migrations)}"
VERSION="${2:?Usage: bump-version.sh <service> <version>}"

# Validate semver format
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version must be in semver format (e.g., 1.2.3)"
    exit 1
fi

case "$SERVICE" in
    backend)
        echo "Bumping backend to $VERSION..."
        sed -i "s/^version = \".*\"/version = \"$VERSION\"/" "$PROJECT_DIR/services/backend/pyproject.toml"
        echo "  Updated services/backend/pyproject.toml"
        ;;
    frontend)
        echo "Bumping frontend to $VERSION..."
        sed -i "s/\"version\": \".*\"/\"version\": \"$VERSION\"/" "$PROJECT_DIR/services/frontend/package.json"
        echo "  Updated services/frontend/package.json"
        ;;
    db-migrations)
        echo "db-migrations shares the backend version."
        echo "Use: bump-version.sh backend $VERSION"
        exit 1
        ;;
    *)
        echo "Error: Unknown service '$SERVICE'"
        echo "Valid services: backend, frontend"
        exit 1
        ;;
esac

# Update kustomize overlays with the image tag for this service
IMAGE_NAME="architect-$SERVICE"
for overlay in local-dev staging; do
    KUSTOMIZATION="$PROJECT_DIR/k8s/overlays/$overlay/kustomization.yaml"
    if [ -f "$KUSTOMIZATION" ]; then
        # Update the tag for this service's image
        sed -i "/name: $IMAGE_NAME$/{n;s/newTag: \".*\"/newTag: \"$VERSION\"/}" "$KUSTOMIZATION"
        echo "  Updated k8s/overlays/$overlay/kustomization.yaml"
    fi
done

# Also update db-migrations tag if bumping backend
if [ "$SERVICE" = "backend" ]; then
    IMAGE_NAME="architect-db-migrations"
    for overlay in local-dev staging; do
        KUSTOMIZATION="$PROJECT_DIR/k8s/overlays/$overlay/kustomization.yaml"
        if [ -f "$KUSTOMIZATION" ]; then
            sed -i "/name: $IMAGE_NAME$/{n;s/newTag: \".*\"/newTag: \"$VERSION\"/}" "$KUSTOMIZATION"
        fi
    done
    # Update migration job image tag
    sed -i "s/architect-db-migrations:.*/architect-db-migrations:$VERSION/" "$PROJECT_DIR/k8s/base/migration-job.yaml"
    echo "  Updated k8s/base/migration-job.yaml"
fi

echo "Done."
