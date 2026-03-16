# HashiCorp Packer

## Checklist

- [ ] **[Recommended]** Migrate from JSON templates to HCL2 format (JSON is legacy; HCL2 supports variables, locals, dynamic blocks, and functions)
- [ ] **[Recommended]** Select appropriate builders for target platforms: amazon-ebs, azure-arm, googlecompute, vmware-iso, qemu, docker, vsphere-iso, proxmox
- [ ] **[Optional]** Design multi-cloud image pipeline: single HCL2 template with multiple source blocks producing AMIs, Azure images, and GCP images from one build
- [ ] **[Recommended]** Plan provisioner strategy: prefer cloud-init/user-data for boot-time config; use shell/ansible/chef provisioners for bake-time hardening
- [ ] **[Recommended]** Configure post-processors: manifest (outputs artifact IDs), docker-tag/docker-push, vagrant, compress, checksum, artifice
- [ ] **[Recommended]** Integrate Packer builds into CI/CD pipeline (GitHub Actions, GitLab CI, Jenkins): trigger on base image updates, security patches, or application releases
- [ ] **[Recommended]** Implement image testing: use Packer's post-processor to launch the built image, run InSpec/Goss/Serverspec tests, then promote or discard
- [ ] **[Recommended]** Design variable management: use .pkrvars.hcl files per environment, HCP Packer for variable sets, or CI/CD secret injection for credentials
- [ ] **[Recommended]** Plan image naming and tagging conventions: include build timestamp, git SHA, base OS version, and security patch date in image metadata
- [ ] **[Optional]** Evaluate HCP Packer registry for image lifecycle tracking: channel assignments (dev, staging, production), ancestry tracking, revocation of vulnerable images
- [ ] **[Optional]** Configure builder-specific optimizations: spot/preemptible instances for builds, VPC/subnet selection, instance type sizing for build speed vs cost
- [ ] **[Recommended]** Plan golden image hierarchy: base OS image -> hardened OS image -> application-specific image (layered pipeline with parent tracking)

## Why This Matters

Packer automates the creation of machine images, ensuring that every deployment target (VM, container base image, cloud instance) starts from an identical, tested, and hardened baseline. Without Packer, teams rely on snowflake images built manually or through ad-hoc scripts, leading to configuration drift, unreproducible builds, and security gaps. In multi-cloud environments, Packer's ability to produce images for multiple platforms from a single template eliminates the divergence that occurs when each cloud team maintains separate image-building processes. HCP Packer adds a registry layer that tracks which images are deployed where, enables coordinated revocation of compromised images, and provides a promotion workflow (dev -> staging -> prod) that brings software release discipline to infrastructure images.

## License

HashiCorp transitioned all products from MPL 2.0 to BSL 1.1 in August 2023. The BSL restricts competitive use of the software — you cannot use it to build a product that competes with HashiCorp's commercial offerings. For internal infrastructure use, the BSL is functionally equivalent to open source. Community forks under MPL 2.0 exist: OpenTofu (Terraform fork) and OpenBao (Vault fork). Evaluate license terms for your specific use case before adoption.

## Common Decisions (ADR Triggers)

- **Baked images (Packer) vs configured-at-boot (cloud-init/Ansible)**: Baked images provide faster boot times, reduced runtime dependencies, and immutable infrastructure semantics. Configured-at-boot offers flexibility and smaller image counts but increases boot time and adds runtime failure modes. Best practice: bake security hardening and base packages with Packer; configure environment-specific settings (hostnames, credentials) at boot via cloud-init.
- **Packer + Terraform vs cloud-native image builders (EC2 Image Builder, Azure Image Builder)**: Packer is cloud-agnostic and integrates with existing provisioning tools (Ansible, Chef, shell). Cloud-native builders integrate with provider-specific features (AWS SSM inventory, Azure Shared Image Gallery replication) but lock you into one cloud. Use Packer for multi-cloud; consider cloud-native builders for single-cloud shops that want deeper integration.
- **Shell provisioner vs Ansible provisioner**: Shell provisioners are simple and have no dependencies but become unwieldy for complex configurations. Ansible provisioners provide idempotency, role reuse, and better structure but require Ansible installation on the build instance. Use Ansible for anything beyond basic package installation.
- **HCP Packer registry vs custom metadata tracking**: HCP Packer provides out-of-the-box image lineage, channel management, and Terraform integration (data sources that resolve channels to image IDs). Custom solutions (tagging AMIs, storing in a database) are cheaper but require engineering effort. Use HCP Packer when using Terraform Cloud/Enterprise for seamless integration.
- **Single multi-platform template vs per-platform templates**: Single template with multiple source blocks ensures parity across clouds but can become complex with platform-specific provisioning differences. Per-platform templates allow specialization but risk drift. Prefer single templates with conditional provisioner blocks using `only` filters.

## Reference Architectures

### Golden Image Pipeline
```
[Base OS Image (Ubuntu/RHEL)]
        |
  [Packer Build: Hardened Base]
  - CIS benchmark hardening (Ansible role)
  - Security agent installation
  - SSH configuration
  - Monitoring agent
        |
  [Image Test (Goss/InSpec)]
        |
  [HCP Packer Registry: "hardened-base" channel]
        |
  +-----+------+------+
  |            |            |
[App Image A]  [App Image B]  [App Image C]
(Packer build  (Packer build  (Packer build
 uses base)     uses base)     uses base)
  |            |            |
[Test]        [Test]        [Test]
  |            |            |
[HCP Packer: "app-a"]  [HCP Packer: "app-b"]  [HCP Packer: "app-c"]
```
Layered pipeline where hardened base image is the parent for all application images. When a base image is revoked (CVE), HCP Packer identifies all downstream images that need rebuilding. Each layer triggers automated testing before promotion.

### Multi-Cloud Build (Single Template)
```hcl
source "amazon-ebs" "base" {
  ami_name      = "myapp-{{timestamp}}"
  instance_type = "t3.medium"
  source_ami_filter {
    filters = { "name" = "ubuntu/images/hvm-ssd/ubuntu-jammy-*" }
    owners  = ["099720109477"]
  }
  ssh_username = "ubuntu"
  spot_price   = "auto"
}

source "azure-arm" "base" {
  image_publisher = "Canonical"
  image_offer     = "0001-com-ubuntu-server-jammy"
  image_sku       = "22_04-lts"
  os_type         = "Linux"
  vm_size         = "Standard_B2s"
}

source "googlecompute" "base" {
  project_id   = var.gcp_project
  source_image = "ubuntu-2204-jammy-v20240101"
  zone         = "us-central1-a"
  machine_type = "e2-medium"
  ssh_username = "packer"
  use_internal_ip = true
}

build {
  sources = ["amazon-ebs.base", "azure-arm.base", "googlecompute.base"]

  provisioner "ansible" {
    playbook_file = "playbooks/harden.yml"
  }

  post-processor "manifest" {
    output = "build-manifest.json"
  }
}
```
Single build block targets all three clouds. Ansible playbook applies identical hardening. Manifest post-processor outputs artifact IDs for downstream consumption by Terraform. Spot/preemptible instances reduce build costs.

### CI/CD Integration
```
[Git Push (base image repo)] --> [CI Pipeline]
        |
  [packer init]     -- download plugins
  [packer validate] -- syntax/config check
  [packer build]    -- parallel multi-cloud builds
        |
  [Post-build Tests]
  - Launch instance from image
  - Run Goss/InSpec test suite
  - Terminate test instance
        |
  [Promote to HCP Packer Channel]
  - "dev" channel (automatic)
  - "staging" channel (after integration tests)
  - "production" channel (after approval gate)
        |
  [Terraform Plan Detects New Image]
  - data.hcp_packer_artifact resolves new image ID
  - Rolling update of ASG/VMSS/MIG
```
CI triggers on changes to Packer templates or provisioning scripts. Parallel builds produce images for each cloud. Automated tests validate images before channel promotion. Terraform data sources reference HCP Packer channels, automatically picking up promoted images during the next apply.
