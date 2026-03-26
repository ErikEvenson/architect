# Supply Chain Security

## Scope

This file covers **software supply chain security** — ensuring the integrity, provenance, and trustworthiness of all software artifacts from source code through production deployment. Topics include Software Bill of Materials (SBOM) generation and consumption, SLSA framework compliance, container image signing, dependency scanning (SCA), artifact provenance, secure build pipelines, base image management, vulnerability disclosure processes, and regulatory requirements (EO 14028, NIST SSDF). For general security controls (IAM, encryption, network security), see `general/security.md`. For CI/CD pipeline design, see `general/ci-cd.md`.

## Checklist

- [ ] **[Critical]** Generate Software Bill of Materials (SBOM) for every deployable artifact — produce SBOMs in both SPDX and CycloneDX formats at build time using tools like Syft, Trivy, or Microsoft sbom-tool, store them alongside artifacts in the registry, and establish a process for consuming SBOMs from third-party vendors to validate their dependency chains
- [ ] **[Critical]** Implement container image signing using Sigstore cosign or Notary v2 — sign all images produced by CI/CD pipelines with keyless signing (Fulcio + Rekor) or bring-your-own-key, enforce signature verification in Kubernetes admission controllers (Kyverno, OPA Gatekeeper, or Connaisseur) to prevent unsigned images from running in any environment
- [ ] **[Critical]** Establish a dependency scanning (SCA) pipeline that runs on every commit and PR — use tools like Snyk, Grype, OWASP Dependency-Check, or GitHub Dependabot to identify known CVEs in direct and transitive dependencies, define a policy for blocking builds on critical/high vulnerabilities, and set a maximum remediation SLA (critical: 48 hours, high: 7 days, medium: 30 days)
- [ ] **[Critical]** Design secure build pipelines that meet at least SLSA Build Level 2 (scripted build, authenticated provenance) with a roadmap to Level 3 (hardened build platform) — use hosted CI/CD runners with ephemeral build environments, ensure build definitions are stored in version control, prevent developers from executing arbitrary commands on build workers, and generate SLSA provenance attestations for every artifact
- [ ] **[Critical]** Define a base image management strategy — select minimal base images (distroless, Alpine, or UBI-minimal), maintain an internal golden image catalog rebuilt on a weekly cadence or when new CVEs are published, pin base image digests (not tags) in Dockerfiles, and scan base images independently of application layers
- [ ] **[Critical]** Implement artifact provenance tracking end-to-end — record which source commit, build system, builder identity, and build parameters produced each artifact, store provenance attestations in an immutable transparency log (Rekor, Grafeas), and verify provenance before promotion to staging and production environments
- [ ] **[Critical]** Assess compliance with Executive Order 14028 requirements if selling to US federal agencies — this includes SBOM generation, secure development practices (NIST SSDF SP 800-218), vulnerability disclosure programs, and self-attestation of conformity with secure software development practices
- [ ] **[Recommended]** Implement the NIST Secure Software Development Framework (SSDF SP 800-218) by mapping its four practice groups (Prepare the Organization, Protect the Software, Produce Well-Secured Software, Respond to Vulnerabilities) to concrete controls in your SDLC — document the mapping and identify gaps for remediation
- [ ] **[Recommended]** Deploy a private artifact registry (Harbor, JFrog Artifactory, AWS ECR, Azure ACR, or GCP Artifact Registry) with vulnerability scanning enabled on push, retention policies for image cleanup, replication for multi-region availability, and role-based access control limiting who can push images to production repositories
- [ ] **[Recommended]** Establish a vulnerability disclosure and response process — publish a security.txt and/or SECURITY.md with contact information, define an internal triage process with SLA-based severity classification, coordinate disclosure timelines with reporters, and maintain a vulnerability database that tracks remediation status across all affected versions
- [ ] **[Recommended]** Pin all dependency versions (lock files, hash verification) and use a dependency proxy or mirror (Artifactory, Nexus, Verdaccio) to insulate builds from upstream registry outages, dependency confusion attacks, and package hijacking — verify package integrity using checksums or signatures where available
- [ ] **[Recommended]** Implement a dependency update strategy that balances security with stability — use automated tools (Renovate, Dependabot) to create PRs for dependency updates, group minor/patch updates by ecosystem, require CI to pass before merge, and schedule a weekly triage cadence for reviewing proposed updates
- [ ] **[Recommended]** Enforce build reproducibility where feasible — deterministic builds allow independent verification that a given source commit produces an identical binary, reducing the risk of compromised build infrastructure injecting malicious code (cf. SolarWinds attack), and are required for SLSA Build Level 4
- [ ] **[Recommended]** Protect CI/CD pipeline credentials and secrets — use short-lived OIDC tokens for cloud authentication (GitHub Actions OIDC, GitLab CI OIDC) instead of long-lived service account keys, store pipeline secrets in a secrets manager (not CI/CD variable stores), restrict secret access to specific branches and environments, and rotate all pipeline credentials on a 90-day cycle
- [ ] **[Optional]** Deploy a software composition analysis (SCA) governance dashboard that aggregates license compliance (GPL, AGPL, SSPL contamination risk), vulnerability counts, SBOM freshness, and mean-time-to-remediate metrics across all repositories — use this to report supply chain risk posture to leadership
- [ ] **[Optional]** Implement VEX (Vulnerability Exploitability eXchange) documents to communicate whether vulnerabilities in SBOMs are actually exploitable in your deployment context — this reduces false-positive noise and helps downstream consumers prioritize remediation
- [ ] **[Optional]** Evaluate Trusted Computing and hardware-rooted attestation (TPM, Intel TXT, AMD SEV) for build workers to establish a hardware root of trust for the build environment — this is relevant for SLSA Build Level 4 and high-assurance government workloads

## Why This Matters

Software supply chain attacks have moved from theoretical risk to routine occurrence. The SolarWinds Sunburst attack (2020) demonstrated that compromising a single build pipeline can grant access to 18,000 organizations including US government agencies. The Codecov breach (2021) showed that a tampered CI/CD tool can exfiltrate secrets from thousands of downstream repositories. The Log4Shell vulnerability (2021) revealed that a single transitive dependency buried deep in the dependency tree can create a critical vulnerability across millions of applications — and that most organizations could not even answer the basic question "do we use Log4j?" because they lacked SBOMs.

These incidents triggered regulatory action. US Executive Order 14028 (May 2021) now requires federal software suppliers to produce SBOMs, attest to secure development practices, and implement vulnerability disclosure programs. The EU Cyber Resilience Act imposes similar requirements on products sold in European markets. Organizations that cannot demonstrate supply chain security practices will be locked out of government contracts and face increasing scrutiny from enterprise customers.

The SLSA framework provides a graduated maturity model — from Level 1 (documented build process) through Level 4 (hermetic, reproducible, hardware-attested builds) — that gives organizations a concrete roadmap rather than a binary pass/fail. Starting at Level 2 (scripted build with authenticated provenance) provides significant protection against the most common attack vectors: compromised source, tampered build process, and modified artifacts.

Beyond compliance, supply chain security directly affects operational resilience. Without an SBOM, responding to the next Log4Shell-class vulnerability requires manually auditing every application. Without image signing, a compromised registry or man-in-the-middle attack can inject malicious containers. Without dependency pinning, a malicious upstream package update (the ua-parser-js and event-stream incidents) can compromise every downstream build automatically.

## Common Decisions (ADR Triggers)

### ADR: SBOM Format and Generation Strategy

**Context:** The organization needs to produce SBOMs for all deployable artifacts to meet regulatory requirements and enable vulnerability response.

**Options:**

| Approach | Format | Generation Tool | Strengths | Limitations |
|---|---|---|---|---|
| Build-time generation (preferred) | CycloneDX or SPDX | Syft, Trivy, Microsoft sbom-tool | Captures exact build-time dependencies; integrates into CI/CD; most accurate | Requires CI/CD pipeline changes per project |
| Registry-based scanning | CycloneDX | Harbor, JFrog Xray, ACR | Automatic for all pushed images; no pipeline changes | Post-build only; may miss build-time-only dependencies |
| Source-based generation | SPDX | SPDX tools, FOSSology | Captures license metadata; suitable for source distribution | Does not reflect runtime dependencies; misses container OS packages |

**Decision drivers:** Regulatory requirements (EO 14028 prefers build-time SBOMs), whether the primary use case is vulnerability response (CycloneDX preferred) or license compliance (SPDX preferred), CI/CD maturity, number of repositories to onboard, and whether SBOMs must be delivered to customers.

### ADR: Container Image Signing and Verification

**Context:** Container images must be signed to ensure only trusted, unmodified images run in production.

**Options:**
- **Sigstore cosign (keyless):** Uses OIDC identity (GitHub Actions, Google, Microsoft) via Fulcio for ephemeral certificates; signatures and attestations stored in Rekor transparency log. No key management overhead. Requires internet access to Rekor for verification (or deploy private Rekor instance). Rapidly becoming the industry standard.
- **Sigstore cosign (key-pair):** Traditional asymmetric key signing via cosign. Organization manages the signing key in a KMS (AWS KMS, GCP KMS, Azure Key Vault, HashiCorp Vault). Offline verification possible. Key rotation and distribution must be managed.
- **Notary v2 (notation):** OCI-native signing standard backed by CNCF. Signatures stored as OCI artifacts alongside images in the registry. Uses X.509 certificates. Better integration with existing PKI infrastructure. Smaller ecosystem than Sigstore.

**Decision drivers:** Whether the organization has existing PKI infrastructure (favors Notary v2), whether air-gapped deployment is required (favors key-pair cosign), CI/CD provider OIDC support (favors keyless cosign), Kubernetes admission controller compatibility, and team familiarity.

### ADR: SLSA Target Level and Implementation Roadmap

**Context:** The organization must decide what SLSA Build Level to target initially and over what timeline to progress.

**Options:**
- **SLSA Build Level 1:** Build process is documented and automated. Provenance is available but not authenticated. Minimal effort — most organizations with CI/CD already meet this. Does not protect against compromised build systems.
- **SLSA Build Level 2:** Build service generates authenticated provenance (signed attestations). Protects against artifact tampering after build. Requires CI/CD integration with SLSA provenance generators (GitHub Actions SLSA generator, Tekton Chains).
- **SLSA Build Level 3:** Build platform is hardened — runs on an isolated, tamper-resistant service. Build definitions cannot be modified by build users. Protects against compromised CI/CD configuration. Requires hosted build service with strong tenant isolation (GitHub-hosted runners, Google Cloud Build).
- **SLSA Build Level 4:** Hermetic, reproducible builds with hardware-attested build environments. Highest assurance. Significant engineering investment. Currently achievable only for specific ecosystems (Go, Bazel).

**Decision drivers:** Regulatory requirements (EO 14028 effectively requires Level 2+), customer contract requirements, current CI/CD maturity, engineering capacity to invest in build infrastructure, and threat model (nation-state adversaries warrant Level 3+).

### ADR: Dependency Management and Pinning Strategy

**Context:** The organization must balance dependency freshness (getting security patches quickly) with stability (preventing supply chain attacks via malicious updates).

**Options:**
- **Strict pinning with automated updates:** Pin all dependencies by exact version and hash in lock files. Use Renovate or Dependabot to propose updates via PR. All updates require CI pass and human review. Highest security and stability. Higher maintenance burden.
- **Range pinning with auto-merge for patches:** Allow patch-version ranges (e.g., ~1.2.3) in manifests, auto-merge patch updates that pass CI. Manual review for minor/major updates. Balances security updates with review burden. Risk of malicious patch releases.
- **Dependency proxy with quarantine:** Route all package installs through an internal proxy (Artifactory, Nexus). New package versions are quarantined for a configurable period (24-72 hours) before becoming available. Protects against rapid-fire supply chain attacks but delays security patches.

**Decision drivers:** Team size and capacity for dependency review, security risk tolerance, compliance requirements, build reproducibility goals, and whether the organization has experienced dependency-related incidents.

### ADR: Base Image Strategy

**Context:** Container base images are the foundation of every deployed workload and represent a large portion of the vulnerability surface area.

**Options:**
- **Distroless images (Google distroless):** Contain only the application runtime — no shell, no package manager, no OS utilities. Smallest attack surface. Difficult to debug in production (no shell access). Best for compiled languages (Go, Java, Rust).
- **Alpine-based images:** Minimal Linux distribution (~5 MB). Uses musl libc instead of glibc, which can cause compatibility issues with some libraries. Small attack surface. Has a package manager for adding build dependencies.
- **UBI-minimal (Red Hat):** Minimal Red Hat Enterprise Linux base. Uses glibc, broadest compatibility. Supported by Red Hat with predictable CVE patching cadence. Required for OpenShift and some regulated environments. Larger than Alpine (~100 MB).
- **Internal golden images:** Organization-maintained base images built from a chosen upstream (Ubuntu, RHEL, Debian) with hardening applied (CIS benchmarks, removed unnecessary packages). Rebuilt weekly or on CVE trigger. Consistent security baseline across all applications. Requires dedicated team to maintain.

**Decision drivers:** Language runtime requirements (musl vs. glibc), regulatory requirements (RHEL/UBI for FedRAMP), debugging needs in production, team familiarity, image size constraints, and whether a dedicated platform team can maintain golden images.

## Reference Links

- [SLSA Framework](https://slsa.dev/)
- [Sigstore](https://www.sigstore.dev/)
- [cosign](https://docs.sigstore.dev/cosign/overview/)
- [NIST SSDF SP 800-218](https://csrc.nist.gov/publications/detail/sp/800-218/final)
- [Executive Order 14028](https://www.whitehouse.gov/briefing-room/presidential-actions/2021/05/12/executive-order-on-improving-the-nations-cybersecurity/)
- [CycloneDX SBOM Standard](https://cyclonedx.org/)
- [SPDX Specification](https://spdx.dev/)
- [Syft (SBOM Generator)](https://github.com/anchore/syft)
- [Grype (Vulnerability Scanner)](https://github.com/anchore/grype)
- [Notary v2 (notation)](https://notaryproject.dev/)
- [Kyverno (Policy Engine)](https://kyverno.io/)
- [CISA SBOM Resources](https://www.cisa.gov/sbom)
- [OpenVEX](https://openvex.dev/)
- [Tekton Chains](https://tekton.dev/docs/chains/)
- [SLSA GitHub Actions Generator](https://github.com/slsa-framework/slsa-github-generator)

## See Also

- `general/security.md` — General security controls including secrets management, encryption, and IAM
- `general/ci-cd.md` — CI/CD pipeline design including build, test, and deployment automation
- `general/container-orchestration.md` — Container runtime security, admission controllers, and Kubernetes security policies
- `general/deployment.md` — Deployment strategies and artifact promotion workflows
- `general/compliance-automation.md` — Automated compliance scanning and policy-as-code
- `general/cloud-workload-hardening.md` — CIS Benchmarks, golden image pipelines, and runtime hardening
- `general/observability.md` — Audit logging for supply chain events and build pipeline monitoring
