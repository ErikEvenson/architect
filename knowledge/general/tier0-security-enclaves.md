# Tier 0 and Security Enclave Handling During Platform Transformation

## Scope

This file covers **handling highest-security enclaves (Tier 0) during infrastructure platform changes** -- the decision framework for migrating, retaining, or relocating identity infrastructure, PKI, privileged access systems, and security tooling when the underlying platform is changing. For general security architecture, see `general/security.md`. For identity architecture, see `general/identity.md`. For hypervisor migration, see `patterns/hypervisor-migration.md`. For Azure Stack HCI migration specifically, see `patterns/azure-stack-hci-migration.md`.

## Checklist

### Tier 0 Identification

- [ ] **[Critical]** Are all Tier 0 workloads identified and inventoried? Tier 0 typically includes: Active Directory Domain Controllers, Active Directory Certificate Services (ADCS/PKI), Active Directory Federation Services (ADFS), Privileged Access Workstations (PAW), security tooling (SIEM collectors, vulnerability scanners, EDR management servers), and DNS servers authoritative for internal zones.
- [ ] **[Critical]** Is the Tier 0 boundary explicitly defined? Which VMs are inside the security enclave vs. which consume Tier 0 services from outside? The boundary determines the migration unit -- everything inside moves together or stays together.
- [ ] **[Critical]** Are Tier 0 dependencies mapped? Which workloads outside Tier 0 depend on Tier 0 services (AD authentication, certificate issuance, DNS resolution, security policy enforcement)? If Tier 0 moves, these dependencies must continue to function during and after the move.
- [ ] **[Critical]** Is the current Tier 0 platform documented? (Dedicated physical hosts, specific hypervisor, dedicated network segments, hardware security modules, specific compliance certifications tied to the platform)
- [ ] **[Recommended]** Is the Tier 0 change control process documented? Tier 0 environments typically require the strictest change approval (security CAB, extended maintenance windows, mandatory rollback plans, multi-person authorization).
- [ ] **[Recommended]** Are Tier 0 backup and recovery procedures documented separately from standard workloads? AD forest recovery, PKI key recovery, and security tooling rebuild have unique procedures.

### Disposition Decision

- [ ] **[Critical]** Is a disposition decision documented for Tier 0 workloads? Options: (A) Keep on current platform at new facility, (B) Migrate to the target platform, (C) Move to cloud, (D) Rebuild from scratch on target platform.
- [ ] **[Critical]** Is the disposition decision made by the security architecture team, not the infrastructure team? Tier 0 decisions are security decisions that happen to involve infrastructure. The security team must own the risk acceptance.
- [ ] **[Critical]** If keeping Tier 0 on a different platform than the rest (Option A), is the dual-platform operational cost documented? (Separate management plane, separate patching cadence, separate skills requirement, separate licensing, separate backup infrastructure)
- [ ] **[Recommended]** Is the disposition decision independent of the migration timeline? Tier 0 should not be rushed to meet a migration deadline. If the deadline requires Tier 0 to move before the security team is ready, the answer is "Tier 0 stays, everything else moves."

### Migration Sequencing

- [ ] **[Critical]** Is Tier 0 sequenced LAST in the migration plan, not first? Tier 0 provides foundational services (authentication, DNS, certificates) that all other workloads depend on. Moving Tier 0 first risks disrupting every other workload. Moving it last means all dependent workloads are already stable on the target platform.
- [ ] **[Critical]** Is a Tier 0 connectivity plan in place for the migration period? During migration, some workloads will be at the source and some at the target. Both must be able to reach Tier 0 services. Options: Tier 0 stays at source until last, cross-site AD replication with DCs at both locations, or read-only DCs at the target during migration.
- [ ] **[Critical]** Are AD domain controllers deployed at the target facility BEFORE any workloads move there? Authentication must be available locally -- workloads should not authenticate across WAN to source-site DCs during normal operations.
- [ ] **[Recommended]** Is a phased Tier 0 approach planned? Phase 1: deploy read-only DCs and secondary DNS at target (parallel with standard migration). Phase 2: promote target DCs to writable, transfer FSMO roles. Phase 3: decommission source DCs after validation period.
- [ ] **[Recommended]** Are certificate services migration and PKI hierarchy changes planned separately from the infrastructure migration? PKI migration (moving or rebuilding CA hierarchy) is a multi-week effort with its own validation and rollback procedures.

### Platform Migration (if Option B -- migrate Tier 0 to target platform)

- [ ] **[Critical]** Is security architecture revalidation planned? Changing the hypervisor or platform under Tier 0 workloads may invalidate existing security assessments, compliance certifications, or audit findings. The security team must revalidate.
- [ ] **[Critical]** Are hypervisor-specific security features mapped between source and target? (vTPM, Secure Boot, memory encryption, VM isolation) If the source platform provides security features that the target does not, Tier 0 migration may introduce security regression.
- [ ] **[Critical]** Is the Tier 0 migration tested in a non-production environment first? Never perform Tier 0 platform migration directly in production. Build a parallel Tier 0 on the target platform, validate all security functions, then cut over.
- [ ] **[Recommended]** Is a rollback plan documented that can restore Tier 0 to the source platform within the maintenance window? AD and PKI rollback is complex -- snapshot-based rollback may cause USN rollback issues in AD. Plan for authoritative restore procedures.
- [ ] **[Recommended]** Is the maintenance window sized for Tier 0 migration larger than standard workload windows? Tier 0 cutover requires validation of every dependent service (authentication, group policy, certificate issuance, DNS, security tools).

### Compliance and Audit

- [ ] **[Critical]** Are compliance requirements documented for the Tier 0 platform? (SOX controls for financial systems, regulatory requirements for identity infrastructure, audit trail requirements for privileged access)
- [ ] **[Critical]** Is an audit trail maintained for every change to Tier 0 during the transformation? (Who approved, what changed, when, rollback available) This is not standard change management -- it is security-auditable change management.
- [ ] **[Recommended]** Are compliance certifications reviewed for impact? Changing the platform under Tier 0 may require re-certification (SOC 2, ISO 27001, PCI DSS, etc.) if the certification scope includes the infrastructure platform.
- [ ] **[Optional]** Is the security team's sign-off documented as a gate before Tier 0 migration proceeds? This is a hold point -- the migration cannot proceed past this gate without explicit security approval.

## Why This Matters

Tier 0 is the foundation of enterprise security. Every user authentication, every group policy enforcement, every certificate issuance, and every privileged access decision flows through Tier 0. When it breaks, everything breaks -- and it breaks in ways that are difficult to diagnose because the symptoms appear in the dependent applications, not in Tier 0 itself.

The most common failures during infrastructure transformation:

1. **Migrating Tier 0 first "to get it out of the way."** This puts the highest-risk, most-dependent workloads on an unproven platform before any other workloads validate it. When AD breaks on the new platform, there are no other workloads to test against, and the failure cascades to everything at the source that depends on AD replication.

2. **Treating Tier 0 as "just more VMs."** The infrastructure team includes domain controllers in a standard migration wave alongside application servers. AD domain controllers have unique migration requirements (replication topology, FSMO roles, SYSVOL replication, DNS integration) that standard VM migration tools don't understand.

3. **Forcing Tier 0 onto a timeline.** The lease expires in 90 days and Tier 0 hasn't moved. Under pressure, the team rushes the migration and skips security validation. Post-migration, certificate issuance breaks because the CA was moved without updating the AIA/CDP extensions. This takes days to diagnose and fix.

4. **Not planning for the dual-site period.** During migration, workloads exist at both source and target. Without AD replication and DNS at the target, migrated workloads can't authenticate. The first wave fails because no one planned for Tier 0 connectivity during the migration period.

The correct approach: Tier 0 is the LAST thing to fully migrate, but the FIRST thing to extend to the target (via read-only DCs, secondary DNS, replicated ADCS). This ensures dependent workloads can authenticate at both locations throughout the migration.

## Common Decisions (ADR Triggers)

- **Tier 0 platform disposition** -- keep on current platform (dual-platform ops), migrate to target platform (security revalidation), move to cloud (network dependency), or rebuild (clean start, most effort). This is a security decision, not an infrastructure decision.
- **Dual-platform operational model** -- if Tier 0 stays on a different platform, define the operational scope: separate patching, separate monitoring, separate skills, separate licensing. Document the ongoing cost.
- **AD topology during migration** -- deploy read-only DCs at target vs. writable DCs vs. rely on WAN replication to source. Affects authentication latency and fault tolerance during migration.
- **PKI migration approach** -- migrate existing CA hierarchy vs. rebuild on target. Migration preserves certificate chain; rebuild provides a clean start but requires re-issuance of all certificates.
- **Tier 0 migration timing** -- migrate as the final wave (safest), migrate in parallel with late waves (faster), or defer to a separate Phase 3 project (cleanest separation of risk). The decision should be owned by the security team.

## See Also

- `general/security.md` -- Security architecture and controls
- `general/identity.md` -- Identity and access management architecture
- `patterns/hypervisor-migration.md` -- Hypervisor-to-hypervisor migration pattern
- `patterns/azure-stack-hci-migration.md` -- Azure Stack HCI migration (common Tier 0 platform)
- `patterns/datacenter-relocation.md` -- Full datacenter relocation pattern
- `general/governance.md` -- Change management and governance processes
