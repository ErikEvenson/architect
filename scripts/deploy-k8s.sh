#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

NAMESPACE="${1:?Usage: deploy-k8s.sh <namespace> (e.g., architect-dev, architect-staging)}"

# Map namespace to overlay directory
case "$NAMESPACE" in
    architect-dev)
        OVERLAY_DIR="$PROJECT_DIR/k8s/overlays/local-dev"
        ;;
    architect-staging)
        OVERLAY_DIR="$PROJECT_DIR/k8s/overlays/staging"
        ;;
    *)
        echo "Error: Unknown namespace '$NAMESPACE'"
        echo "Valid namespaces: architect-dev, architect-staging"
        exit 1
        ;;
esac

echo "Deploying Architect to namespace: $NAMESPACE"
echo "Using overlay: $OVERLAY_DIR"

# Create namespace (idempotent)
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Check TLS secret exists
if ! kubectl get secret architect-tls -n "$NAMESPACE" &>/dev/null; then
    echo "Error: TLS secret 'architect-tls' not found in namespace '$NAMESPACE'."
    echo "Run: scripts/setup-tls.sh $NAMESPACE"
    exit 1
fi

# Check app secrets exist
if ! kubectl get secret architect-secrets -n "$NAMESPACE" &>/dev/null; then
    echo "Error: Secret 'architect-secrets' not found in namespace '$NAMESPACE'."
    echo "Run: scripts/create-secrets.sh $NAMESPACE"
    exit 1
fi

# Apply kustomize overlay
echo ""
echo "Applying kustomize overlay..."
kubectl apply -k "$OVERLAY_DIR"

# Wait for postgres
echo ""
echo "Waiting for postgres to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n "$NAMESPACE" --timeout=120s

# Print access info
echo ""
echo "Deployment complete!"
case "$NAMESPACE" in
    architect-dev)
        echo "  Backend:  https://localhost:30010"
        echo "  Frontend: https://localhost:30011"
        ;;
    architect-staging)
        echo "  Backend:  https://localhost:30010"
        echo "  Frontend: https://localhost:30011"
        ;;
esac
echo ""
echo "Next steps:"
echo "  1. Run migrations: kubectl delete job architect-migration -n $NAMESPACE --ignore-not-found && kubectl apply -f k8s/base/migration-job.yaml -n $NAMESPACE"
echo "  2. Check pods: kubectl get pods -n $NAMESPACE"
