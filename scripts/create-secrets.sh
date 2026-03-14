#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${1:?Usage: create-secrets.sh <namespace>}"

echo "Creating secrets for namespace: $NAMESPACE"

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" &>/dev/null; then
    echo "Error: Namespace '$NAMESPACE' does not exist."
    echo "Run: kubectl create namespace $NAMESPACE"
    exit 1
fi

# Check if secrets already exist
if kubectl get secret architect-secrets -n "$NAMESPACE" &>/dev/null; then
    echo "Warning: Secret 'architect-secrets' already exists in namespace '$NAMESPACE'."
    read -r -p "Overwrite? [y/N] " response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# Generate passwords
POSTGRES_PASSWORD=$(openssl rand -hex 12)

# Create secret
kubectl create secret generic architect-secrets \
    --from-literal=postgres-password="$POSTGRES_PASSWORD" \
    --namespace="$NAMESPACE" \
    --dry-run=client -o yaml | kubectl apply -f -

echo ""
echo "Secrets created in namespace '$NAMESPACE'."
echo ""
echo "Generated values (save these!):"
echo "  postgres-password: $POSTGRES_PASSWORD"
