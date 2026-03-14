# Disaster Recovery

## Scope

This file covers **what** disaster recovery strategy decisions need to be made (RPO/RTO targets, failover models, DR testing). For provider-specific data protection implementation, see the provider files.

## Checklist

- [ ] What is the RPO (Recovery Point Objective)? How much data loss is acceptable?
- [ ] What is the RTO (Recovery Time Objective)? How quickly must the service recover?
- [ ] What failure scenarios must be survived? (instance, AZ, region, provider)
- [ ] What is the failover model? (active-passive, active-active, pilot light, warm standby)
- [ ] Is cross-region replication configured for databases?
- [ ] Is cross-region replication configured for object storage?
- [ ] Are backups stored in a different region from primary?
- [ ] Is there an automated failover mechanism? (DNS failover, database failover)
- [ ] How is failover tested? How often?
- [ ] Is there a documented runbook for DR scenarios?
- [ ] How is data consistency maintained during failover?
- [ ] What is the failback procedure after recovery?
- [ ] Are there dependencies on third-party services? What happens if they fail?

## Why This Matters

Disasters happen — AZ outages, region outages, data corruption. Without a tested DR plan, recovery is improvised and slow. RPO/RTO must be defined by business requirements, not by what the infrastructure happens to provide.

## Common Decisions (ADR Triggers)

- **Failover model** — active-passive vs active-active (cost vs RTO trade-off)
- **Region selection** — primary and standby regions
- **Replication strategy** — synchronous (zero RPO, higher latency) vs asynchronous
- **Failover automation** — manual vs automated (DNS health checks)
- **DR testing cadence** — quarterly, monthly, chaos engineering

## See Also

- `providers/nutanix/data-protection.md` — Nutanix backup and replication
- `providers/vmware/data-protection.md` — VMware backup and replication
- `providers/openstack/data-protection.md` — OpenStack backup and recovery
- `providers/openshift/data-protection.md` — OpenShift data protection
