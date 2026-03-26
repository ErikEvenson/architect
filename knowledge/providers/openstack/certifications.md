# OpenStack Certifications and Training

## Scope

OpenStack certification paths, training resources, and skill validation for teams operating OpenStack private clouds. Covers Certified OpenStack Administrator (COA), OpenInfra Foundation training programs, vendor-specific OpenStack certifications (Red Hat, Mirantis, Canonical/Ubuntu), and relevance to OpenStack deployment, operations, and migration engagements. Does not cover general Linux certifications — see `providers/openshift/certifications.md` for RHCSA/RHCE which are also relevant.

## Checklist

- [ ] **[Critical]** Is the Certified OpenStack Administrator (COA) identified as the baseline vendor-neutral certification for OpenStack operations teams — covers identity management (Keystone), compute (Nova), networking (Neutron), block storage (Cinder), object storage (Swift), image management (Glance), and basic orchestration?
- [ ] **[Critical]** Is the COA exam format understood — performance-based (live OpenStack environment), 2.5 hours, tasks performed on a real cluster, proctored online or at test centers, passing score approximately 70%?
- [ ] **[Critical]** Are deployment-tool-specific skills validated in addition to COA — teams using Kolla-Ansible, TripleO/Director, Canonical MaaS/Juju, or Mirantis MCP require tool-specific expertise that COA does not cover?
- [ ] **[Recommended]** Is Red Hat Certified System Administrator in Red Hat OpenStack (EX210) evaluated for teams running Red Hat OpenStack Platform (RHOSP) — covers RHOSP-specific deployment with Director (TripleO), Ceph integration, and Red Hat-specific operational procedures?
- [ ] **[Recommended]** Is the COA validity period tracked — the COA certification does not expire, but the exam content is updated for major OpenStack releases and recertification demonstrates currency with the platform?
- [ ] **[Recommended]** Are OpenInfra Foundation training resources evaluated — instructor-led courses (OpenStack Administration, OpenStack Operations) and self-paced content available through the OpenInfra Foundation and partner training providers?
- [ ] **[Recommended]** Is Mirantis training evaluated for teams using Mirantis-distributed OpenStack — Mirantis offers OpenStack operations training aligned to their distribution and support model?
- [ ] **[Recommended]** Are Canonical/Ubuntu OpenStack training paths evaluated for teams using Charmed OpenStack — Ubuntu Pro and Canonical training cover Juju-based deployment and operations specific to the Canonical distribution?
- [ ] **[Recommended]** Is the Linux foundation strong enough across the team — OpenStack operations require deep Linux system administration skills (networking, storage, systemd, troubleshooting), making RHCSA or equivalent a practical prerequisite even if not formally required?
- [ ] **[Optional]** Are OpenStack upstream contribution skills developed for teams running highly customized deployments — understanding the release cycle, Launchpad bug tracking, Gerrit code review, and patch backporting is valuable for teams maintaining custom patches?
- [ ] **[Optional]** Is OpenStack Summit / OpenInfra Summit attendance evaluated for team development — the annual summit provides hands-on workshops, operator sessions, and networking with the OpenStack community?
- [ ] **[Optional]** Are vendor-neutral cloud certifications (CKA, AWS/Azure) evaluated for teams migrating workloads from OpenStack to public cloud or Kubernetes — dual-stack skills accelerate migration projects?

## Why This Matters

OpenStack is operationally complex — it comprises 30+ interrelated services, and misconfigurations in Keystone, Neutron, or Cinder can cascade across the entire platform. The COA certification validates hands-on competency in a live environment, making it a meaningful signal of operational readiness. However, COA alone is insufficient for teams responsible for deployment and lifecycle management, which requires tool-specific expertise (TripleO, Kolla-Ansible, Juju) that varies by distribution. The OpenStack ecosystem is fragmented across vendors (Red Hat, Mirantis, Canonical, SUSE) with significantly different deployment and management tooling, making vendor-specific training as important as the vendor-neutral COA.

The OpenStack talent pool is shrinking as organizations migrate to public cloud or Kubernetes. Certification and training investment must be weighed against the platform's longevity in the organization's roadmap. For teams operating OpenStack long-term, COA plus distribution-specific training is essential. For teams migrating away from OpenStack, investing in target platform certifications (CKA, AZ-305, NCP-MCI) may be higher priority.

## Common Decisions (ADR Triggers)

- **COA vs vendor-specific certification** — COA for vendor-neutral validation vs Red Hat EX210 or Mirantis training for distribution-specific operations; COA demonstrates breadth, vendor certs demonstrate depth with specific tooling
- **OpenStack certification investment vs migration target certs** — for organizations planning OpenStack exit within 2-3 years, redirecting training budget to target platform certifications may be more strategic
- **Linux foundation training priority** — RHCSA/RHCE as prerequisite foundation vs direct OpenStack training; teams weak on Linux fundamentals will struggle with OpenStack regardless of OpenStack-specific training
- **Instructor-led vs self-paced training** — OpenStack operational complexity makes hands-on instructor-led training more effective, but self-paced is more cost-effective for distributed teams
- **Upstream contribution skills** — invest in upstream development skills for teams maintaining custom deployments vs consume vendor-supported distributions without customization

## Training Resources

### Official Training Platform

- **OpenInfra Foundation Training** — instructor-led courses through authorized training providers, self-paced content available, OpenStack Administration and Operations courses

### Vendor-Specific Training

- **Red Hat:** CL210 (OpenStack Administration), CL310 (Advanced Administration), included in RHLS
- **Mirantis:** Mirantis OpenStack training programs aligned to their distribution
- **Canonical:** Ubuntu OpenStack training covering Charmed OpenStack (Juju-based) deployment and operations

### Hands-On Labs

- DevStack (single-node test deployment, free)
- Packstack (multi-node lab, free)
- Vendor trial environments
- Red Hat Developer Sandbox

### Learning Paths by Role

- **Operator:** Linux fundamentals (RHCSA) → COA → vendor-specific training (CL210 or equivalent)
- **Architect:** RHCSA → COA → vendor-specific advanced → CKA (if migrating to K8s)

### Training Cost and Time Estimates

- ~80-120 hours for COA
- COA exam fee $300
- Vendor courses $2,500-4,000 each
- RHLS $7,000/yr includes all Red Hat OpenStack courses

## Reference Links

- [Certified OpenStack Administrator (COA) exam](https://www.openstack.org/coa) -- COA exam objectives, registration, and preparation resources
- [OpenStack training marketplace](https://www.openstack.org/marketplace/training/) -- authorized training providers and courses for OpenStack certification

## See Also

- `general/certification-training.md` -- cross-vendor certification strategy
- `providers/openstack/infrastructure.md` -- OpenStack infrastructure overview
- `providers/openstack/deployment-tools.md` -- OpenStack deployment tooling
- `providers/openshift/certifications.md` -- Red Hat certifications (RHCSA/RHCE relevant for OpenStack)
- `providers/kubernetes/certifications.md` -- CKA/CKAD for teams migrating from OpenStack to Kubernetes
