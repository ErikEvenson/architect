# Knowledge Library

The knowledge library is a curated collection of cloud architecture checklists that Claude Code uses during architecture sessions. Each file contains structured questions and considerations that ensure no critical design decisions are overlooked.

## Purpose

When Claude acts as a cloud architect in Architect sessions, it draws on these knowledge files to ask the right questions, surface tradeoffs, and identify decisions that warrant an Architecture Decision Record (ADR). The library encodes hard-won lessons from real-world cloud deployments so they are applied consistently across every engagement.

## Directory Structure

```
knowledge/
  general/          Cloud-agnostic topics (security, networking, compute, data,
                    observability, disaster recovery, cost, deployment)
  providers/        Provider-specific guidance organized by cloud platform
    aws/            Amazon Web Services (VPC, IAM, RDS, EC2, etc.)
    azure/          Microsoft Azure (compute, networking, data, security)
    gcp/            Google Cloud Platform (compute, networking, data, security)
    nutanix/        Nutanix private cloud
    vmware/         VMware private cloud
    openstack/      OpenStack private cloud
  patterns/         Architecture patterns (microservices, three-tier web,
                    data pipeline, hybrid cloud, static site)
  compliance/       Compliance frameworks and regulatory checklists
  failures/         Failure mode analysis and resilience checklists
```

### general/

Cloud-agnostic checklists that apply regardless of provider. These cover foundational concerns like security posture, networking topology, compute sizing, data management, observability, disaster recovery, cost optimization, and deployment strategy. These files are referenced in nearly every architecture session.

### providers/

Provider-specific checklists that layer on top of the general guidance. For example, `general/security.md` covers universal security questions, while `providers/aws/iam.md` covers AWS-specific IAM configuration. During a session targeting AWS, both files are relevant.

### patterns/

Architecture pattern checklists for common system designs. These are selected based on the type of system being designed (e.g., a microservices backend, a three-tier web application, a data pipeline). Each pattern file includes an overview, a checklist, common mistakes, and key sub-patterns.

### compliance/

Checklists for specific compliance frameworks (PCI DSS, HIPAA, SOC 2, FedRAMP, GDPR). These are pulled in when a project has regulatory requirements.

### failures/

Failure mode checklists covering resilience concerns: blast radius analysis, dependency failure scenarios, data loss prevention, and recovery procedures. These help ensure systems are designed to fail gracefully.

## How Claude Code Uses the Library

During an architecture session, Claude selects the relevant knowledge files based on:

1. **Target cloud provider(s)** -- loads the appropriate `providers/` files
2. **System pattern** -- loads the matching `patterns/` file
3. **General concerns** -- loads relevant `general/` files (security, networking, etc.)
4. **Compliance requirements** -- loads `compliance/` files if regulatory standards apply
5. **Resilience requirements** -- loads `failures/` files for high-availability designs

Claude walks through the checklist items as questions during the session. Each unchecked item represents a decision that needs to be made. When a decision is significant or has long-term implications, Claude flags it as an ADR trigger.

## Browsing in the Web UI

The Architect web interface provides a way to browse the knowledge library:

- Navigate to the knowledge section to see all available checklists organized by category
- Each file displays its checklist items, context, and ADR triggers
- During an active architecture session, the relevant knowledge files are highlighted
- Completed checklist items track which questions have been addressed for a given project

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding or updating knowledge files.

