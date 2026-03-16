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

# --- PostgreSQL PV retention: rebind existing retained PV ---
PVC_NAME="postgres-data-postgres-0"
RETAINED_PV=$(kubectl get pv -l architect/namespace="$NAMESPACE",architect/component=postgres-data \
    --no-headers -o custom-columns=":metadata.name" 2>/dev/null | head -1)
REUSING_PV=false

if [[ -n "$RETAINED_PV" ]]; then
    REUSING_PV=true
    echo ""
    echo "Found retained PostgreSQL PV: $RETAINED_PV"

    # Clear the old claimRef so the PV can be rebound
    kubectl patch pv "$RETAINED_PV" --type=json \
        -p='[{"op": "remove", "path": "/spec/claimRef"}]' 2>/dev/null || true

    # Get storage class and capacity from the retained PV
    PV_SC=$(kubectl get pv "$RETAINED_PV" -o jsonpath='{.spec.storageClassName}')
    PV_CAP=$(kubectl get pv "$RETAINED_PV" -o jsonpath='{.spec.capacity.storage}')

    # Pre-create the PVC bound to the retained PV (before StatefulSet tries to create it)
    if ! kubectl get pvc "$PVC_NAME" -n "$NAMESPACE" &>/dev/null; then
        echo "Pre-creating PVC $PVC_NAME bound to $RETAINED_PV..."
        kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: $PVC_NAME
  namespace: $NAMESPACE
  labels:
    app: postgres
    architect/component: postgres-data
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: "$PV_SC"
  volumeName: "$RETAINED_PV"
  resources:
    requests:
      storage: "$PV_CAP"
EOF
        echo "PVC $PVC_NAME created and bound to retained PV."
    else
        echo "PVC $PVC_NAME already exists, skipping pre-creation."
    fi
else
    echo ""
    echo "No retained PostgreSQL PV found — fresh deployment."
fi

# Apply kustomize overlay
echo ""
echo "Applying kustomize overlay..."
kubectl apply -k "$OVERLAY_DIR"

# Wait for postgres
echo ""
echo "Waiting for postgres to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n "$NAMESPACE" --timeout=120s

# --- PostgreSQL PV retention: sync password if reusing existing data ---
if [[ "$REUSING_PV" == "true" ]]; then
    echo ""
    echo "Syncing PostgreSQL password with retained database..."
    NEW_PW=$(kubectl get secret architect-secrets -n "$NAMESPACE" \
        -o jsonpath='{.data.postgres-password}' | base64 -d)
    kubectl exec -n "$NAMESPACE" postgres-0 -- \
        psql -U architect -d architect -c "ALTER USER architect PASSWORD '$NEW_PW'" \
        >/dev/null 2>&1
    echo "PostgreSQL password updated to match current secret."
fi

# --- PostgreSQL PV retention: patch PV reclaim policy and label it ---
POSTGRES_PV=$(kubectl get pvc "$PVC_NAME" -n "$NAMESPACE" -o jsonpath='{.spec.volumeName}' 2>/dev/null)
if [[ -n "$POSTGRES_PV" ]]; then
    echo ""
    echo "Patching PV $POSTGRES_PV: reclaimPolicy=Retain"
    kubectl patch pv "$POSTGRES_PV" -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'
    kubectl label pv "$POSTGRES_PV" \
        architect/namespace="$NAMESPACE" \
        architect/component=postgres-data \
        --overwrite
    echo "PostgreSQL PV labeled and set to Retain."
fi

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
