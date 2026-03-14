# AWS Secrets Manager

## Checklist

- [ ] Are all database credentials, API keys, and sensitive configuration values stored in Secrets Manager rather than environment variables, code, or config files?
- [ ] Is automatic rotation enabled for database credentials using the appropriate Lambda rotation function?
- [ ] Is the rotation schedule appropriate? (30 days for database passwords, shorter for API keys in high-security environments)
- [ ] Is multi-region replication configured for secrets required by applications in multiple regions?
- [ ] Are resource-based policies on secrets scoped to specific IAM roles and accounts, not using wildcard principals?
- [ ] Is the secret encrypted with a customer-managed KMS key (not the default aws/secretsmanager key) for cross-account access and key rotation control?
- [ ] Are secret versions managed correctly, with applications using AWSCURRENT staging label and rotation using AWSPENDING?
- [ ] Is Secrets Manager chosen over Parameter Store for the right reasons? (rotation, cross-region replication, binary secrets, RDS/Redshift integration)
- [ ] Are applications using the Secrets Manager SDK with caching (AWS Secrets Manager Caching Client) to reduce API calls and latency?
- [ ] Is CloudTrail logging monitored for GetSecretValue calls to detect unauthorized access attempts?
- [ ] Are secrets tagged with ownership, environment, and rotation-status tags for governance and cost tracking?
- [ ] Is there a process to revoke and rotate secrets immediately in case of a suspected compromise?
- [ ] Are VPC endpoints configured for Secrets Manager to avoid secrets traversing the internet via NAT Gateway?

## Why This Matters

Hardcoded secrets in code repositories are the leading cause of credential leaks. Unrotated credentials accumulate risk over time. Missing rotation causes outages when manual rotation is performed without testing. Cross-region applications fail during regional outages if secrets are not replicated. Excessive Secrets Manager API calls without caching add latency and cost.

## Common Decisions (ADR Triggers)

- **Secrets Manager vs Parameter Store** -- rotation and replication vs lower cost ($0.05/param vs $0.40/secret/month), tier selection
- **Secrets Manager vs HashiCorp Vault** -- managed service simplicity vs multi-cloud and advanced features (dynamic secrets, leases)
- **KMS key strategy** -- per-secret keys vs shared keys, key rotation policy
- **Rotation architecture** -- managed rotation (RDS, Redshift, DocumentDB) vs custom Lambda rotation for other secret types
- **Cross-account secret sharing** -- resource-based policies vs cross-account KMS key grants vs replication
- **Secret structure** -- one secret per credential vs JSON blob with multiple key-value pairs
- **Application integration** -- SDK with caching vs CSI Secrets Store driver (EKS) vs init container injection
