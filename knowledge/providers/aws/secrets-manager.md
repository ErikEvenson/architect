# AWS Secrets Manager

## Checklist

- [ ] **[Critical]** Are all database credentials, API keys, and sensitive configuration values stored in Secrets Manager rather than environment variables, code, or config files?
- [ ] **[Critical]** Is automatic rotation enabled for database credentials using the appropriate Lambda rotation function?
- [ ] **[Recommended]** Is the rotation schedule appropriate? (30 days for database passwords, shorter for API keys in high-security environments)
- [ ] **[Recommended]** Is multi-region replication configured for secrets required by applications in multiple regions?
- [ ] **[Critical]** Are resource-based policies on secrets scoped to specific IAM roles and accounts, not using wildcard principals?
- [ ] **[Recommended]** Is the secret encrypted with a customer-managed KMS key (not the default aws/secretsmanager key) for cross-account access and key rotation control?
- [ ] **[Recommended]** Are secret versions managed correctly, with applications using AWSCURRENT staging label and rotation using AWSPENDING?
- [ ] **[Recommended]** Is Secrets Manager chosen over Parameter Store for the right reasons? (rotation, cross-region replication, binary secrets, RDS/Redshift integration; note: Parameter Store Standard tier is free for up to 10,000 parameters)
- [ ] **[Recommended]** Are applications using the Secrets Manager SDK with caching (AWS Secrets Manager Caching Client) to reduce API calls and latency?
- [ ] **[Recommended]** Use BatchGetSecretValue API to retrieve multiple secrets in a single call, reducing API overhead and latency for applications that need several secrets at startup; supports up to 20 secrets per request filtered by name or tag
- [ ] **[Recommended]** Is CloudTrail logging monitored for GetSecretValue calls to detect unauthorized access attempts?
- [ ] **[Optional]** Are secrets tagged with ownership, environment, and rotation-status tags for governance and cost tracking?
- [ ] **[Recommended]** Is there a process to revoke and rotate secrets immediately in case of a suspected compromise?
- [ ] **[Recommended]** Are VPC endpoints configured for Secrets Manager to avoid secrets traversing the internet via NAT Gateway?

## Why This Matters

Hardcoded secrets in code repositories are the leading cause of credential leaks. Unrotated credentials accumulate risk over time. Missing rotation causes outages when manual rotation is performed without testing. Cross-region applications fail during regional outages if secrets are not replicated. Excessive Secrets Manager API calls without caching add latency and cost.

## Common Decisions (ADR Triggers)

- **Secrets Manager vs Parameter Store** -- rotation and replication vs lower cost (Standard parameters are free, up to 10,000 per account; Advanced parameters $0.05/param/month for >10,000 or >4 KB values; Secrets Manager $0.40/secret/month), tier selection
- **Secrets Manager vs HashiCorp Vault** -- managed service simplicity vs multi-cloud and advanced features (dynamic secrets, leases)
- **KMS key strategy** -- per-secret keys vs shared keys, key rotation policy
- **Rotation architecture** -- managed rotation (RDS, Redshift, DocumentDB) vs custom Lambda rotation for other secret types
- **Cross-account secret sharing** -- resource-based policies vs cross-account KMS key grants vs replication
- **Secret structure** -- one secret per credential vs JSON blob with multiple key-value pairs
- **Application integration** -- SDK with caching vs CSI Secrets Store driver (EKS) vs init container injection

## Reference Architectures

- [AWS Architecture Center: Security, Identity, & Compliance](https://aws.amazon.com/architecture/security-identity-compliance/) -- reference architectures for secrets management in multi-account environments
- [AWS Prescriptive Guidance: Secret management for applications](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/rotate-database-credentials-without-restarting-containers.html) -- patterns for rotating secrets without application downtime
- [AWS Well-Architected Labs: Security - Data Protection](https://www.wellarchitectedlabs.com/security/) -- hands-on labs for secrets management and encryption best practices
- [AWS Secrets Manager rotation architecture](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html) -- reference design for Lambda-based automatic credential rotation
- [AWS EKS Secrets Store CSI Driver integration](https://docs.aws.amazon.com/secretsmanager/latest/userguide/integrating_csi_driver.html) -- reference architecture for mounting secrets as volumes in Kubernetes pods
