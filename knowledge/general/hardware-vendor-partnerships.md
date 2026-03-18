# Hardware Vendor Partnerships

## Scope

This file covers **hardware vendor partnerships with hypervisor and platform vendors** — the co-engineering relationships, certification programs, pre-validated configurations, and integrated lifecycle management that affect platform selection and procurement decisions. It does not cover hardware specifications or sizing (see `general/hardware-sizing.md`), hypervisor feature comparison (see `providers/vmware/` and `providers/nutanix/`), or software licensing (see `providers/vmware/licensing.md`).

## Checklist

- [ ] **[Critical]** Hardware vendor selected and verified as certified for the target hypervisor/platform (VMware HCL, Nutanix compatibility matrix, OpenStack vendor ecosystem)
- [ ] **[Critical]** Pre-validated configurations evaluated vs custom builds — vSAN Ready Nodes, Nutanix certified nodes, or HPE DX series reduce risk and accelerate deployment
- [ ] **[Critical]** Hardware Compatibility List (HCL) checks completed before procurement — every server model, NIC, HBA, and GPU validated against the platform vendor's compatibility matrix
- [ ] **[Critical]** Support model and escalation boundaries documented — clear delineation of hardware vendor support vs software vendor support, with joint escalation procedures identified
- [ ] **[Critical]** Firmware and driver lifecycle management strategy selected — vLCM for VMware, LCM for Nutanix, HPE OneView, or manual process with defined cadence
- [ ] **[Recommended]** Custom hypervisor images from the hardware vendor evaluated — Dell custom ESXi images, HPE Vibsdepot images include vendor-specific drivers and firmware agents pre-integrated
- [ ] **[Recommended]** Deal registration completed with both hardware and software vendors to secure partner procurement discounts and priority support
- [ ] **[Recommended]** Reference architectures from the vendor partnership reviewed — Dell+VMware, HPE+Nutanix, and similar joint publications contain validated configurations and best practices
- [ ] **[Recommended]** Hardware reuse feasibility assessed for platform migrations — PowerEdge servers may support multiple hypervisors, but VxRail and NX appliances are single-platform locked
- [ ] **[Recommended]** Hyper-converged appliance vs software-on-standard-hardware decision made — VxRail and Nutanix NX are turnkey but inflexible; software on PowerEdge/ProLiant offers more choice
- [ ] **[Optional]** As-a-service consumption model evaluated — HPE GreenLake for VMware or Nutanix shifts CapEx to OpEx with vendor-managed hardware lifecycle
- [ ] **[Optional]** Multi-vendor hardware strategy assessed — mixing Dell and HPE in the same cluster is technically possible but complicates lifecycle management and support contracts
- [ ] **[Optional]** End-of-life hardware partnership implications reviewed — older server models may lose HCL certification on newer hypervisor versions, forcing hardware refresh

## Why This Matters

Hardware and software vendors invest heavily in joint engineering, certification, and support integration. These partnerships produce tangible benefits: pre-validated configurations eliminate compatibility guesswork, integrated lifecycle management reduces firmware/driver update risk, and joint support agreements prevent finger-pointing during outages. Ignoring these partnerships — for example, deploying VMware on uncertified hardware or skipping custom vendor ESXi images — leads to unsupported configurations, longer troubleshooting cycles, and voided support entitlements.

The partnership also affects procurement economics. Deal registration with both hardware and software vendors can yield 15-30% discounts. Pre-validated configurations (vSAN Ready Nodes, Nutanix certified nodes) come with tested bill-of-materials that procurement teams can order directly, reducing configuration errors and lead times.

Platform migration decisions are constrained by these partnerships. A VxRail environment cannot be converted to Nutanix without replacing the hardware (VxRail is a closed appliance). A Dell PowerEdge environment running VMware may be reusable for Nutanix if the specific model and components appear on the Nutanix compatibility matrix. Understanding these constraints early prevents costly surprises during migration planning.

## Common Decisions (ADR Triggers)

### ADR: Dell + VMware Partnership Model

**Trigger:** Deploying VMware on Dell hardware or evaluating Dell as the hardware vendor for a VMware environment.
**Considerations:**

- **VxRail (hyper-converged appliance):** Fully integrated Dell+VMware HCI appliance. vSAN + VCF pre-installed. Single support call to Dell for hardware and software. Automated full-stack lifecycle management. Best for organizations wanting turnkey HCI with minimal operational overhead. Locked to VMware — cannot be repurposed for another hypervisor.
- **vSAN Ready Nodes (validated configurations):** PowerEdge servers pre-configured, tested, and certified for VMware vSAN. Managed through vLCM for full-stack firmware/driver updates. More flexible than VxRail — standard PowerEdge hardware that can theoretically be repurposed. 300+ PowerEdge configurations certified for vSphere 8.
- **Standard PowerEdge with VMware:** Any PowerEdge model on the VMware HCL. Maximum flexibility in configuration. Use Dell custom ESXi images (include iDRAC agents, OMSA, and Dell-certified drivers). Requires more manual lifecycle management. Best for organizations with existing VMware expertise who want hardware choice.
- Dell custom ESXi images include iDRAC Service Module, OpenManage Server Administrator (OMSA), and certified NIC/HBA/storage drivers. Using vanilla VMware ISO on Dell hardware means losing these integrations and potentially running uncertified driver versions.

### ADR: Dell + Nutanix Partnership Model

**Trigger:** Deploying Nutanix on Dell hardware or migrating from Dell+VMware to Nutanix.
**Considerations:**

- **Nutanix NX (Nutanix-manufactured):** Purpose-built Nutanix hardware. Single vendor for hardware and software support. Nutanix controls the full stack. Simpler support model but limited to Nutanix-selected components.
- **Nutanix on Dell PowerEdge (certified nodes):** Nutanix software on standard Dell PowerEdge servers. Hardware support from Dell, software support from Nutanix. Allows organizations with existing Dell relationships and spare parts inventory to stay on Dell hardware. Must verify each PowerEdge model against the Nutanix compatibility matrix.
- **Dell XC series:** Previously Dell's branded Nutanix HCI line — now discontinued. Existing XC deployments should plan migration to either Nutanix NX or Nutanix on PowerEdge.
- Hardware reuse during VMware-to-Nutanix migration: if current PowerEdge servers are on the Nutanix compatibility matrix, they can potentially be reimaged with AHV, avoiding a hardware forklift. Verify NIC, HBA, and disk controller compatibility specifically.

### ADR: HPE Partnership Model

**Trigger:** Deploying VMware or Nutanix on HPE hardware, or evaluating HPE GreenLake consumption models.
**Considerations:**

- **HPE ProLiant for VMware:** DL360/DL380 certified for vSphere. HPE custom ESXi images via Vibsdepot/image builder include iLO agents and HPE-certified drivers. HPE OneView provides lifecycle management. Synergy composable infrastructure supports VMware for blade-based deployments.
- **HPE ProLiant DX for Nutanix:** Purpose-configured ProLiant servers for Nutanix workloads. Hardware support from HPE, software support from Nutanix. Integrated with HPE OneView for hardware lifecycle.
- **HPE GreenLake:** As-a-service consumption model for both VMware and Nutanix. HPE owns and manages the hardware; customer pays based on consumption. Shifts CapEx to OpEx. Available for VMware (GreenLake for VMware) and Nutanix (GreenLake for Nutanix). Useful for organizations that want on-premises infrastructure without owning the hardware lifecycle.

### ADR: Lenovo Partnership Model

**Trigger:** Evaluating Lenovo as hardware vendor for VMware or Nutanix environments.
**Considerations:**

- **ThinkAgile VX (VMware vSAN on Lenovo):** Pre-validated Lenovo servers for VMware vSAN. Integrated with Lenovo XClarity for lifecycle management. Competitive pricing compared to Dell and HPE.
- **ThinkAgile HX (Nutanix on Lenovo):** Lenovo servers certified for Nutanix. Hardware support from Lenovo, software support from Nutanix. Good option for organizations with existing Lenovo relationships.
- Lenovo has a smaller market share in enterprise data centers compared to Dell and HPE, which may affect spare parts availability and local support response times. Evaluate regional support coverage before committing.

### ADR: Supermicro for Open-Source Platforms

**Trigger:** Deploying OpenStack, Ceph, Kubernetes bare metal, or other open-source platforms where vendor certification is less critical.
**Considerations:**

- Supermicro offers the lowest hardware cost per node, making it attractive for cost-sensitive deployments and large-scale clusters.
- Nutanix certifies select Supermicro configurations, but the certification matrix is narrower than Dell or HPE.
- For OpenStack, Ceph, and Kubernetes bare metal, there is no formal HCL — Linux kernel support for the hardware components (NIC, storage controller, GPU) is the primary compatibility concern.
- Management tooling (IPMI, Supermicro SuperDoctor) is less polished than Dell iDRAC or HPE iLO but functional. Redfish API support is improving in newer models.
- Best suited for: hyperscale deployments, Ceph storage clusters, Kubernetes bare-metal clusters, and lab/development environments where cost optimization outweighs management polish.

### ADR: Custom ISO Images vs Vendor-Provided Images vs Vanilla Installs

**Trigger:** Deciding which hypervisor installation image to use during deployment.
**Considerations:**

- **Vendor-provided custom images (recommended):** Dell, HPE, and Lenovo publish custom ESXi images that bundle certified drivers, firmware agents, and management tools. These are tested against specific server models and reduce post-install configuration.
- **Vanilla/upstream images:** Using the standard VMware or Nutanix ISO without vendor customizations. Simpler to manage across mixed hardware environments but may lack hardware-specific drivers and management agents. Nutanix Foundation handles driver injection during imaging, reducing the need for custom ISOs on the Nutanix side.
- **Custom-built images:** Organizations build their own ISO with specific driver versions and configurations. Maximum control but highest maintenance burden. Requires retesting with each hypervisor update.
- For VMware, Dell custom ESXi images are available from the Dell support site and are the recommended installation method for PowerEdge servers.

### ADR: Firmware/Driver Lifecycle Management Approach

**Trigger:** Defining the ongoing maintenance process for hardware firmware and driver updates.
**Considerations:**

- **VMware vLCM (vSphere Lifecycle Manager):** Manages ESXi patches, firmware, and drivers as a unified cluster image. Works with Dell, HPE, and Lenovo hardware depots. Recommended for VMware environments — ensures all hosts in a cluster run identical firmware/driver stacks.
- **Nutanix LCM (Life Cycle Manager):** One-click firmware updates for Nutanix-supported hardware. Covers BIOS, BMC, disk firmware, and NIC firmware. Works on NX, Dell, HPE, and Lenovo certified nodes. Highly automated with pre-update compatibility checks.
- **HPE OneView:** Centralized firmware and driver management for HPE servers. Can manage firmware independently of the hypervisor layer. Useful in mixed-hypervisor HPE environments.
- **Manual process:** Download firmware from vendor support site, schedule maintenance window, update via BMC or boot media. Highest effort but maximum control. Common for Supermicro and uncertified configurations.
- Firmware drift (different firmware versions across cluster nodes) is a leading cause of intermittent hardware issues. Integrated lifecycle management tools prevent drift by enforcing consistent versions.

## Reference Links

### Compatibility Guides and HCLs

- [Broadcom/VMware Compatibility Guide](https://compatibilityguide.broadcom.com/) — unified HCL for all VMware products (replaces legacy vmware.com HCL)
- [Nutanix Hardware Platforms](https://www.nutanix.com/products/hardware-platforms) — supported NX, OEM, and partner platforms
- [Nutanix Third-Party Hardware Compatibility Lists](https://portal.nutanix.com/page/documents/list?type=compatibilityList) — per-vendor firmware and hardware compatibility
- [Nutanix Compatibility and Interoperability Matrix](https://portal.nutanix.com/page/documents/compatibility-interoperability-matrix/software) — software compatibility across AOS, AHV, and hypervisors
- [HPE VMware Support and Certification Matrix](https://www.hpe.com/us/en/collaterals/collateral.a50010842enw.html) — ProLiant models certified for vSphere

### Dell + VMware

- [Dell vSAN Ready Nodes](https://www.dell.com/en-us/shop/ipovw/virtual-san-ready-nodes) — pre-configured PowerEdge servers certified for vSAN
- [Dell vSAN Getting Started Guide](https://www.dell.com/support/manuals/en-us/vmware-vsan-poweredge/vsan_gsg_pub/) — deployment guide for vSAN on PowerEdge
- [Dell vSAN Ready Node Firmware Catalog](https://www.dell.com/support/kbdoc/en-us/000183111/firmware-catalog-for-dell-emc-s-vsan-ready-nodes) — certified firmware versions for vLCM

### Dell + Nutanix

- [Dell XC HCI Solutions for Nutanix](https://www.dell.com/en-us/shop/storage-servers-and-networking-for-business/sf/xc-family) — Dell XC series appliances
- [Nutanix on Dell](https://www.nutanix.com/dell) — partnership overview and certified configurations
- [Nutanix Dell PowerEdge Compatibility List](https://portal.nutanix.com/page/documents/list?type=compatibilityList&filterKey=Hardware+Generation&filterVal=Dell+PowerEdge) — certified Dell PowerEdge models

### HPE

- [HPE and VMware Alliance](https://www.hpe.com/us/en/alliance.html) — partnership overview and certified solutions
- [HPE Custom ESXi Images](https://vibsdepot.hpe.com/customimages/Valid-vLCM-Combos.pdf) — valid vLCM combinations for ProLiant

### Lenovo

- [Lenovo ThinkAgile HX Series for Nutanix](https://www.lenovo.com/us/en/servers-storage/sdi/thinkagile-hx-series/) — HX certified nodes and appliances
- [Lenovo ThinkAgile HX on Lenovo Press](https://lenovopress.lenovo.com/servers/thinkagile/hx-series) — product guides and best recipes
- [Nutanix on Lenovo](https://www.nutanix.com/lenovo) — partnership overview
- [Lenovo ThinkAgile Converged Solution for VMware](https://lenovopress.lenovo.com/lp2287-lenovo-thinkagile-converged-solution-for-vmware-v4) — VX series product guide

## See Also

- [hardware-sizing.md](hardware-sizing.md) — physical server specifications, CPU/RAM/disk selection, and reference architectures per role
- [cost-onprem.md](cost-onprem.md) — TCO analysis including hardware procurement, vendor discounts, and depreciation
- [networking-physical.md](networking-physical.md) — NIC selection, switch compatibility, and cabling standards
- [providers/vmware/infrastructure.md](../providers/vmware/infrastructure.md) — VMware vSphere deployment architecture and cluster design
- [providers/nutanix/infrastructure.md](../providers/nutanix/infrastructure.md) — Nutanix cluster architecture and deployment models
- [providers/vmware/vcf-sddc-manager.md](../providers/vmware/vcf-sddc-manager.md) — VCF and SDDC Manager lifecycle management
