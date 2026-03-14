# TLS Certificate Management

## Checklist

- [ ] **[Critical]** Never deploy production services with self-signed certificates — clients will reject them unless every consumer's trust store is manually configured
- [ ] **[Critical]** Automate certificate renewal — expired certificates cause outages, and manual renewal is the #1 cause of TLS-related downtime
- [ ] **[Critical]** Include all required Subject Alternative Names (SANs) — hostname, FQDN, IP addresses, wildcard if needed; missing SANs cause TLS handshake failures
- [ ] **[Critical]** Disable TLS 1.0 and 1.1 — they have known vulnerabilities (BEAST, POODLE); enforce TLS 1.2 minimum, prefer TLS 1.3
- [ ] **[Critical]** Store private keys securely — never commit to version control, use Kubernetes Secrets (encrypted at rest with KMS), HashiCorp Vault, or cloud KMS
- [ ] **[Recommended]** Set up certificate expiry monitoring and alerting — alert at 30, 14, and 7 days before expiration (Prometheus blackbox exporter, Nagios check_ssl_cert, or cloud-native tools)
- [ ] **[Recommended]** Use cert-manager for Kubernetes environments — it automates issuance and renewal via Let's Encrypt, Vault, or internal CA with zero downtime
- [ ] **[Recommended]** Establish a certificate inventory — track all certificates, their expiry dates, issuing CA, and owning team; tools: cert-manager dashboard, Venafi, Keyfactor, or a simple spreadsheet
- [ ] **[Recommended]** Use separate certificates per service rather than sharing a single wildcard — limits blast radius if a key is compromised
- [ ] **[Recommended]** Configure HSTS headers (Strict-Transport-Security) on public-facing services to prevent TLS stripping attacks
- [ ] **[Optional]** Implement certificate pinning for mobile apps or high-security API clients — but plan for rotation (backup pins, max-age)
- [ ] **[Optional]** Set up OCSP stapling on your web servers to improve TLS handshake performance and privacy
- [ ] **[Optional]** Use Certificate Transparency (CT) log monitoring to detect unauthorized certificate issuance for your domains (crt.sh, Facebook CT monitor, SSLMate CertSpotter)
- [ ] **[Optional]** Implement mutual TLS (mTLS) for service-to-service communication — each service presents a client certificate; service meshes (Istio, Linkerd) automate this
- [ ] **[Optional]** Document your certificate chain hierarchy and publish CA certificates in an internal repository for easy trust store configuration

## Why This Matters

TLS certificates are the foundation of encrypted communication and identity verification across every modern system. A certificate failure is not a graceful degradation — it is a hard failure. Browsers show scary warnings, API clients throw exceptions, Docker daemons refuse to pull images, and Kubernetes pods crash-loop. The most common production outages caused by certificates are entirely preventable: expired certificates, missing SANs, and untrusted CAs.

Certificate management complexity scales with your infrastructure. A single web server needs one certificate. A Kubernetes cluster with 50 services, a container registry, a database, and internal APIs may need dozens. Without automation, each is a ticking time bomb. Let's Encrypt democratized free certificates but introduced operational requirements (90-day expiry, automated renewal). Internal CAs add enterprise control but require PKI expertise. The decision framework below helps you pick the right approach for each scenario.

## Common Decisions (ADR Triggers)

### ADR: Certificate Authority Selection

**Self-signed / mkcert (development only)**

Generate a local CA and server certificates with no external dependencies. `mkcert` automatically installs the CA into the local OS and browser trust stores, eliminating the "Your connection is not private" warning during development.

```
# mkcert (recommended for dev)
mkcert -install                          # install local CA
mkcert myapp.local "*.myapp.local" localhost 127.0.0.1

# openssl (manual, any environment)
openssl req -x509 -newkey rsa:4096 -sha256 -days 365 \
  -nodes -keyout ca.key -out ca.crt \
  -subj "/CN=My Internal CA"
openssl req -newkey rsa:4096 -nodes -keyout server.key -out server.csr \
  -subj "/CN=myapp.example.com" \
  -addext "subjectAltName=DNS:myapp.example.com,DNS:*.myapp.example.com,IP:10.0.0.5"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out server.crt -days 365 -sha256 \
  -extfile <(printf "subjectAltName=DNS:myapp.example.com,DNS:*.myapp.example.com,IP:10.0.0.5")
```

Acceptable for: POC, development, air-gapped environments, internal tools with controlled clients. Never for public-facing services.

**Let's Encrypt (public-facing services)**

Free, automated, 90-day certificates via ACME protocol. The 90-day expiry is intentional — it forces automation. Rate limits: 50 certificates per registered domain per week, 5 duplicate certificates per week, 300 new orders per account per 3 hours.

- **HTTP-01 challenge**: Prove domain ownership by serving a file at `http://yourdomain/.well-known/acme-challenge/TOKEN`. Requires port 80 open. Cannot issue wildcard certificates. Works with certbot, Traefik, Caddy, nginx.
- **DNS-01 challenge**: Prove ownership by creating a `_acme-challenge.yourdomain` TXT record. Required for wildcard certificates. Works with any DNS provider that has an API (Cloudflare, Route53, Google Cloud DNS). No port 80 needed — works for internal services with public DNS.

**Decision trigger:** Use HTTP-01 for simple public web servers. Use DNS-01 for wildcard certs, internal services, or when port 80 is blocked.

**Internal CA (enterprise, compliance, air-gapped)**

Run your own Certificate Authority for internal services. Required when: public CA cannot issue certificates for internal hostnames (e.g., `myapp.corp.internal`), compliance mandates organizational CA control, or the environment is air-gapped.

- **step-ca (Smallstep)**: Modern, lightweight, supports ACME protocol (your internal services can use the same tooling as Let's Encrypt). Supports SSH certificates too. Best choice for cloud-native environments.
- **HashiCorp Vault PKI**: Dynamic short-lived certificates (minutes to hours). Tight integration with Vault's auth methods. Best for service-to-service mTLS where certificates rotate frequently.
- **CFSSL (Cloudflare)**: Simple JSON-based CA. Good for scripted certificate generation. Less feature-rich than step-ca.
- **Active Directory Certificate Services (ADCS)**: Windows-native, integrates with Group Policy for auto-enrollment. Use when AD is the backbone of your organization.

**Decision trigger:** Any service using non-public hostnames, compliance requirements for CA control, or air-gapped environments.

### ADR: Kubernetes Certificate Management Strategy

**cert-manager** is the de facto standard for certificate management in Kubernetes. It watches Certificate CRDs and automatically provisions and renews certificates, storing them as Kubernetes Secrets.

Key concepts:
- **Issuer** (namespace-scoped) vs **ClusterIssuer** (cluster-wide): ClusterIssuer is preferred for shared CAs like Let's Encrypt.
- **Certificate CRD**: Declares the desired certificate (DNS names, duration, renewal window). cert-manager creates a Secret with `tls.crt`, `tls.key`, and `ca.crt`.
- **Ingress annotations**: `cert-manager.io/cluster-issuer: letsencrypt-prod` on an Ingress resource triggers automatic certificate provisioning.

Issuer types:
- `ACME` (Let's Encrypt or any ACME server including step-ca)
- `CA` (provide a CA key pair, cert-manager signs certificates locally)
- `SelfSigned` (for bootstrapping, not production)
- `Vault` (HashiCorp Vault PKI backend)
- `Venafi` (enterprise certificate management platform)

**Decision trigger:** Any Kubernetes cluster running TLS-enabled services should use cert-manager. The only question is which Issuer type.

### ADR: Wildcard vs Per-Service Certificates

**Wildcard (`*.example.com`)**: Single certificate covers all subdomains at one level. Simpler management, fewer certificates to track. Risk: if the private key leaks, all subdomains are compromised. Requires DNS-01 challenge with Let's Encrypt. Does not cover sub-subdomains (`*.*.example.com` is not valid).

**Per-service certificates**: Each service gets its own certificate. Better security isolation — compromised key affects only one service. More certificates to manage (automate with cert-manager). Can use HTTP-01 challenge.

**Decision trigger:** Use wildcard for ingress/load balancer termination where a single component handles TLS for many services. Use per-service for mTLS, high-security services, or when different services have different certificate requirements (expiry, key size).

### ADR: Certificate Distribution Method

- **Kubernetes Secrets**: Standard for K8s workloads. Encrypt at rest with KMS (AWS KMS, GCP KMS, Azure Key Vault, or `EncryptionConfiguration`). cert-manager creates and rotates these automatically.
- **HashiCorp Vault**: Centralized secret management. Applications fetch certificates via Vault Agent sidecar, CSI driver, or API. Best for dynamic, short-lived certificates.
- **Configuration management (Ansible, Puppet, Chef)**: Push certificates to VMs. Use for non-Kubernetes workloads. Ensure private keys are encrypted in transit (Ansible Vault, encrypted data bags).
- **Cloud-native (AWS ACM, GCP Managed Certificates, Azure Key Vault)**: Fully managed, integrated with cloud load balancers. Zero operational overhead but limited to cloud services.

## Reference Architectures

### Development Environment

```
[Developer Workstation]
  mkcert -install          # one-time: install local CA
  mkcert myapp.local       # generate cert trusted by OS + browsers

[Docker Compose]
  nginx:
    volumes:
      - ./myapp.local.pem:/etc/nginx/tls/cert.pem
      - ./myapp.local-key.pem:/etc/nginx/tls/key.pem

  # /etc/hosts: 127.0.0.1 myapp.local

No certificate warnings, HTTPS works identically to production.
```

### Public-Facing Kubernetes with Let's Encrypt

```
[Internet]
    |
[Cloud Load Balancer]
    |
[nginx-ingress-controller]     <-- TLS termination
    |                                  |
    |                          [cert-manager]
    |                            |          |
    |                    [ClusterIssuer]   [Certificate CRDs]
    |                    (Let's Encrypt     (auto-created from
    |                     prod, DNS-01)     Ingress annotations)
    |
[K8s Services - HTTP internally]

cert-manager flow:
  1. Ingress created with annotation cert-manager.io/cluster-issuer
  2. cert-manager creates Certificate resource
  3. cert-manager creates Order → Challenge (DNS-01 TXT record)
  4. Let's Encrypt validates → issues certificate
  5. cert-manager stores in K8s Secret, mounts to Ingress
  6. 30 days before expiry → automatic renewal
```

### Enterprise Internal PKI

```
[Root CA - Offline]
  |
  +-- Root certificate (20-year expiry)
  |   Stored: HSM or air-gapped machine, used only to sign intermediates
  |
[Intermediate CA - step-ca or Vault PKI]
  |
  +-- Intermediate certificate (5-year expiry)
  |   Runs as a service, issues leaf certificates
  |
  +-- [cert-manager Issuer]         [Vault Agent Sidecars]
  |     |                              |
  |   K8s workloads                 VM workloads
  |   (auto-issued, auto-renewed)   (dynamic, short-lived)
  |
[Trust Distribution]
  +-- K8s: ConfigMap with CA bundle, mounted to pods
  +-- Linux VMs: /usr/local/share/ca-certificates/ + update-ca-certificates
  +-- Docker: /etc/docker/certs.d/<registry>/ca.crt
  +-- Java: keytool -importcert -keystore $JAVA_HOME/lib/security/cacerts
  +-- Windows: certutil -addstore "Root" ca.crt (or Group Policy)
```

### Hybrid: Internal Services + Public Endpoints

```
[Public Internet]                    [Internal Network]
       |                                    |
[Let's Encrypt certs]              [Internal CA (step-ca)]
       |                                    |
[Public Ingress]                   [Internal Ingress]
  api.example.com                    harbor.corp.internal
  app.example.com                    vault.corp.internal
  docs.example.com                   grafana.corp.internal
       |                                    |
[cert-manager]                     [cert-manager]
  ClusterIssuer:                     ClusterIssuer:
    letsencrypt-prod                   internal-ca
    solver: dns01                      ca:
    (Cloudflare API)                     secretName: internal-ca-keypair

Two ClusterIssuers, same cert-manager instance.
Ingress annotations determine which CA signs each certificate.
```
