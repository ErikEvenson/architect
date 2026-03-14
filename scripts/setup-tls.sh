#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${1:?Usage: setup-tls.sh <namespace>}"

echo "Setting up TLS for namespace: $NAMESPACE"

# Check mkcert is installed
if ! command -v mkcert &>/dev/null; then
    echo "Error: mkcert is not installed."
    echo "Install: https://github.com/FiloSottile/mkcert#installation"
    exit 1
fi

# Generate certificates
echo "Generating TLS certificate for localhost..."
mkcert -install 2>/dev/null || true
mkcert localhost 127.0.0.1 ::1

# Create K8s TLS secret (idempotent)
kubectl create secret tls architect-tls \
    --cert=localhost+2.pem \
    --key=localhost+2-key.pem \
    --namespace="$NAMESPACE" \
    --dry-run=client -o yaml | kubectl apply -f -

# Clean up PEM files
rm -f localhost+2.pem localhost+2-key.pem

echo "TLS secret 'architect-tls' created in namespace '$NAMESPACE'."
