# Security

## Scope

This file covers **what** security controls are needed regardless of provider. For provider-specific **how**, see the provider security files.

## Checklist

- [ ] What compliance standards apply? (PCI DSS, HIPAA, SOC2, GDPR, FedRAMP)
- [ ] How is identity and access management handled? (IAM roles, service accounts, least privilege)
- [ ] Where are application secrets stored? (secrets manager, vault, parameter store)
- [ ] Is automatic secret rotation configured?
- [ ] Is encryption at rest enabled for all data stores?
- [ ] Is encryption in transit (TLS) enforced for all connections?
- [ ] What TLS version minimum? (1.2 recommended, 1.3 preferred)
- [ ] How are security groups/firewall rules defined between tiers?
- [ ] Is there a WAF with appropriate rule sets?
- [ ] Is DDoS protection in place?
- [ ] How is vulnerability scanning handled? (container images, OS, dependencies)
- [ ] Is there an intrusion detection/threat detection system?
- [ ] How is SSH/admin access managed? (bastion, SSM, VPN)
- [ ] Are audit logs enabled for all API calls and data access?
- [ ] Is there a security incident response plan?
- [ ] Are security patches applied within a defined SLA?

## Why This Matters

Security breaches are existential risks. Compliance violations carry legal and financial penalties. Missing encryption, weak access controls, or absent audit logging are the most common findings in security audits.

## Common Decisions (ADR Triggers)

- **Compliance framework** — which standards and what controls
- **Secrets management** — which tool, rotation policy
- **Access model** — bastion vs SSM vs VPN
- **Encryption strategy** — key management approach
- **WAF and DDoS protection** — managed rules vs custom
- **Audit logging** — what to log, where to store, retention

## See Also

- `providers/aws/iam.md` — AWS IAM roles, policies, and access management
- `providers/aws/secrets-manager.md` — AWS Secrets Manager configuration
- `providers/azure/security.md` — Azure security controls and identity
- `providers/gcp/security.md` — GCP security controls and IAM
