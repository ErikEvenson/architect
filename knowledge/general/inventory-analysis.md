# Inventory Analysis

## Scope

This file covers **systematic analysis of infrastructure inventories** (VM exports, hypervisor reports, CMDB extracts, facility records) to understand the current environment before migration planning, capacity sizing, or modernization. Applies to any inventory data source -- vCenter exports, cloud provider inventories, manual spreadsheets, or discovery tool outputs. For migration execution, see `general/workload-migration.md`. For hardware sizing, see `general/hardware-sizing.md`. For physical server scoping, see `general/physical-server-scope.md`.

## Checklist

- [ ] **[Critical]** Are workloads categorized by naming conventions? (parse VM names for application codes, environment tags -- prod/dev/test/staging, function indicators -- web/app/db/mq, sequence numbers; document the naming standard discovered)
- [ ] **[Critical]** Are sites identified and grouped by geographic distribution? (extract site/datacenter codes from VM names, cluster names, or datastore prefixes; map to physical locations; quantify workload count per site)
- [ ] **[Critical]** Is storage utilization analyzed for provisioned vs actual usage? (compare provisioned disk to consumed space, calculate overcommit ratios per datastore/cluster, identify thin-provisioned vs thick-provisioned disks, flag datastores above 80% utilization)
- [ ] **[Critical]** Is the hypervisor distribution mapped? (count VMs per ESXi host or hypervisor, identify host versions and patch levels, calculate VM density per host, flag hosts running end-of-life software)
- [ ] **[Critical]** Are decommission candidates identified? (filter powered-off VMs, search for "decom", "old", "deprecated", "retire", "temp", "test" in names; calculate reclaimable resources -- CPU, memory, storage; note last power-on date if available)
- [ ] **[Critical]** Are application groupings established for migration wave planning? (cluster VMs by application affinity -- naming patterns, network proximity, shared datastores; identify dependencies between application tiers -- web/app/db groups that must move together)
- [ ] **[Critical]** Is the physical vs virtual server scope delineated? (separate bare-metal hosts from virtual machines in the inventory; identify physical servers not managed by hypervisors; document appliances, storage controllers, network devices; quantify total physical footprint including rack units and power)
- [ ] **[Critical]** Is inventory data validated against other sources? (cross-reference VM lists against network diagrams, CMDB records, facility/rack elevation drawings, DNS records, monitoring tool inventories; document discrepancies and missing entries; establish which source is authoritative)
- [ ] **[Recommended]** Are VM sizing tiers analyzed? (categorize by CPU/memory/disk into small/medium/large/xlarge tiers; define tier boundaries appropriate to the environment; calculate distribution percentages; identify outliers -- oversized VMs with minimal utilization, undersized VMs at resource limits)
- [ ] **[Recommended]** Is cluster-to-site mapping documented? (map each compute cluster to its physical site/datacenter; identify cluster purpose -- production, DR, development; document cluster resource pools and reservation policies; note stretched clusters spanning sites)
- [ ] **[Recommended]** Is inventory completeness verified? (check for missing fields -- OS version, IP address, resource allocation, creation date; identify VMs without owners or cost centers; flag entries with placeholder or default values; calculate data quality percentage per field)
- [ ] **[Recommended]** Are orphaned resources identified? (find orphaned snapshots consuming storage, unused VM templates, mounted ISOs, disconnected virtual disks, abandoned resource pools, empty folders in the inventory hierarchy; calculate total wasted storage)
- [ ] **[Optional]** Is the operating system distribution documented? (count by OS family and version -- Windows Server 2012/2016/2019/2022, RHEL 7/8/9, Ubuntu, etc.; flag end-of-life OS versions requiring upgrade or extended support; note license implications)
- [ ] **[Optional]** Are resource utilization patterns analyzed where performance data is available? (correlate inventory data with monitoring metrics -- average CPU usage, memory consumption, IOPS; identify right-sizing opportunities; calculate waste from idle or underutilized VMs)
- [ ] **[Optional]** Is a naming convention standard proposed for the target environment? (document discovered conventions, recommend standardization where inconsistent, define naming taxonomy for migrated workloads)

## Why This Matters

Migration projects fail when the source environment is poorly understood. A VM export is raw data -- without systematic analysis, teams miss decommission candidates (wasting migration effort on dead workloads), overlook application dependencies (causing outages when tiers are migrated separately), and missize target infrastructure (because provisioned storage rarely matches actual usage). Storage overcommit ratios are particularly dangerous -- a datastore showing 2TB provisioned may only use 800GB, and migrating at provisioned size wastes budget. Conversely, thin-provisioned disks can grow unexpectedly. Decommission candidates routinely account for 15-30% of VM inventories -- identifying them before migration planning avoids wasted effort and cost. Cross-referencing inventory against diagrams and CMDB records catches shadow IT, forgotten workloads, and stale records that would otherwise surface as surprises mid-migration. Physical server scope is frequently underestimated because hypervisor exports only show virtual machines, missing bare-metal workloads entirely.

## Common Decisions (ADR Triggers)

- **Inventory source of truth** -- which data source is authoritative when CMDB, hypervisor exports, and network diagrams disagree; reconciliation process for discrepancies
- **Decommission criteria** -- what qualifies a VM for decommission (powered off > 90 days, "decom" in name, no owner identified); approval workflow before removing from migration scope
- **Sizing tier definitions** -- boundary thresholds for small/medium/large categories (e.g., small < 4 vCPU/8GB, medium < 8 vCPU/32GB, large above); how tiers map to target instance types or VM sizes
- **Storage calculation method** -- migrate at provisioned size vs actual usage vs actual + growth buffer; handling of thin-to-thick conversion or vice versa
- **Application grouping strategy** -- group by naming convention vs network dependency vs business unit vs shared infrastructure; granularity of migration waves
- **Site migration sequencing** -- which site migrates first based on size, complexity, business criticality, or geographic factors; pilot site selection criteria
- **Orphaned resource disposition** -- delete orphaned snapshots/templates before migration vs archive vs ignore; approval process for cleanup
- **Data quality threshold** -- minimum completeness percentage required before proceeding with planning; which missing fields block migration vs which are acceptable gaps
- **Physical server handling** -- migrate physical-to-virtual (P2V) vs replace with cloud instances vs retain on-premises; criteria for each path

## Naming Convention Analysis

### Extracting Structure from VM Names

VM naming conventions encode critical metadata. Systematic parsing reveals site, environment, function, and application grouping.

**Common naming patterns:**

| Pattern Component | Position | Examples | Information Extracted |
|---|---|---|---|
| Site/datacenter code | Prefix | DEN, NYC, LON, DC1, DC2 | Geographic location, facility |
| Environment indicator | Middle | P, D, T, S, PRD, DEV, TST, STG | Production, development, test, staging |
| Function code | Middle | WEB, APP, DB, MQ, FTP, DNS, AD | Application tier, infrastructure role |
| Application code | Middle | SAP, CRM, ERP, HR, FIN | Business application grouping |
| Sequence number | Suffix | 01, 02, 001 | Instance number within group |

### Inconsistencies and Remediation

Real-world inventories rarely follow a single consistent pattern. Common issues:

- **Multiple naming standards** -- different teams adopted different conventions over the years
- **No naming standard** -- VMs named after the person who created them, project codenames, or random strings
- **Partial compliance** -- site code present but function code missing, or vice versa
- **Case inconsistency** -- DEN-PRD-WEB01 vs den-prd-web01 vs Den-Prd-Web01

**Remediation approach:**
1. Parse all VM names and attempt pattern matching against known conventions
2. Group VMs by detected pattern families
3. For unparseable names, cross-reference against CMDB or contact VM owners
4. Document the mapping between old names and identified attributes
5. Do not rename VMs during migration planning -- renaming is a separate initiative that introduces additional risk

## Site Grouping and Distribution Analysis

### Building the Site Map

Even without explicit site codes in VM names, site grouping can be inferred from:

- **Cluster membership** -- VMs on the same cluster are almost always at the same site
- **Datastore names** -- datastores often contain site codes (DEN-DS01, NYC-VSAN-01)
- **IP address ranges** -- subnet assignments typically map to physical sites
- **ESXi host names** -- host names frequently contain site or rack identifiers
- **vCenter instances** -- some organizations run a vCenter per site

### Distribution Metrics

For each identified site, capture:

| Metric | Purpose |
|--------|---------|
| Total VM count | Migration scope sizing |
| Total vCPU allocation | Compute capacity requirement |
| Total memory allocation | Memory capacity requirement |
| Total provisioned storage | Storage capacity requirement |
| Total consumed storage | Actual storage requirement (more accurate) |
| Production vs non-production ratio | Risk and priority assessment |
| Powered-off VM percentage | Decommission opportunity |
| OS distribution | Compatibility and licensing planning |

## Storage Utilization Analysis

### Provisioned vs Consumed

The gap between provisioned and consumed storage is typically 30-60% in enterprise environments:

```
Provisioned Storage           Consumed Storage
(what the VM thinks           (what is actually
 it has allocated)              used on disk)
     |                              |
     |  2 TB provisioned            |  800 GB consumed
     |                              |
     |  Overcommit ratio: 2.5:1     |
     |                              |
     |  Migration at provisioned    |  Migration at consumed
     |  size: wastes 1.2 TB         |  size: saves budget
     |  per VM on average           |  but needs growth buffer
```

### Storage Analysis Checklist

1. **Calculate per-VM provisioned vs consumed** -- identify the biggest gaps
2. **Flag datastores above 80% consumed** -- these are at risk of running out during migration
3. **Identify thin vs thick provisioning** -- thin-provisioned VMs can grow unexpectedly during migration
4. **Calculate total consumed storage per site** -- this is the migration data volume
5. **Estimate daily change rate** -- required for migration tool bandwidth planning
6. **Identify VMs with multiple disks** -- some migration tools handle multi-disk VMs differently
7. **Flag disks larger than 2 TB** -- some migration tools have per-disk size limits

### Datastore Health Indicators

| Indicator | Healthy | Warning | Critical |
|-----------|---------|---------|----------|
| Utilization | < 70% | 70-85% | > 85% |
| Overcommit ratio (thin) | < 1.5:1 | 1.5:1 - 3:1 | > 3:1 |
| Snapshot space | < 10% of datastore | 10-25% | > 25% |
| Number of VMs per datastore | < 20 | 20-40 | > 40 |

## Decommission Candidate Identification

### Automated Filtering Criteria

Apply these filters to the inventory to identify decommission candidates:

| Criterion | How to Detect | Confidence |
|-----------|---------------|------------|
| **Powered off > 90 days** | VM power state + last power-on date | High -- if no one missed it in 90 days, it is likely not needed |
| **Name contains decom/retire/old/deprecated** | String matching on VM name | Medium -- naming may be aspirational rather than completed |
| **No owner identified** | CMDB cross-reference, custom attributes | Medium -- may be infrastructure without a business owner |
| **End-of-life OS without extended support** | OS version check | Low on its own -- EOL OS does not mean the workload is not needed |
| **Orphaned from application** | Application decomposition, no tier grouping | Medium -- may be standalone utility VM |
| **Zero network traffic** | NetFlow analysis over 30+ days | High -- a VM with no network activity is likely unused |
| **Development/test with no active project** | Project code cross-reference | Medium -- project may be paused, not completed |

### Decommission Savings Estimation

For each decommission candidate, calculate the savings from excluding it from migration scope:

- **Migration effort avoided** -- hours of planning, testing, cutover, validation per VM
- **Target infrastructure saved** -- compute, memory, storage not required at the target
- **License savings** -- OS licenses, application licenses, per-core hypervisor licensing
- **Ongoing operational savings** -- patching, monitoring, backup, support for one fewer VM

**Rule of thumb:** Decommissioning 15-30% of the inventory before migration can reduce project cost by 10-20% and shorten the timeline proportionally.

## Application Grouping for Wave Planning

### Grouping Methods

| Method | Data Source | Accuracy | Effort |
|--------|-----------|----------|--------|
| **Naming convention** | VM names | Medium -- depends on naming consistency | Low -- automated parsing |
| **Network flow analysis** | Firewall logs, NetFlow | High -- shows actual communication | Medium -- requires data collection and analysis |
| **Shared datastore** | Hypervisor inventory | Medium -- co-location suggests but does not prove relationship | Low -- available in VM export |
| **CMDB application mapping** | CMDB records | Varies -- depends on CMDB accuracy | Low -- query existing data |
| **Application owner interviews** | Human knowledge | Highest -- but labor-intensive | High -- schedule and conduct interviews |

### Building Application Groups

1. Start with naming conventions -- group VMs that share application codes
2. Overlay network flow data -- add VMs that communicate heavily with the group
3. Verify with CMDB -- confirm membership and add VMs listed in CMDB but not caught by naming
4. Validate with owners -- present groups to application owners for confirmation
5. Identify cross-group dependencies -- some VMs belong to multiple application groups (shared databases, middleware)

### Migration Wave Formation

Once application groups are defined, form migration waves:

- **Group tightly coupled applications** in the same wave to avoid cross-environment latency
- **Separate independent applications** to limit blast radius per wave
- **Place shared infrastructure last** -- DNS, AD, monitoring, backup servers migrate after all dependent workloads
- **Size waves based on cutover window** -- total data volume, staff capacity, and acceptable downtime per wave

## Data Validation Techniques

### Cross-Reference Matrix

| Data Source A | Data Source B | What to Compare | Common Discrepancies |
|---|---|---|---|
| Hypervisor export | CMDB | VM count, names, IPs | CMDB stale (VMs deleted from hypervisor still in CMDB) |
| Hypervisor export | DNS | VM names vs DNS records | Orphaned DNS records, VMs without DNS entries |
| Hypervisor export | Monitoring | VM names vs monitored hosts | Unmonitored VMs, monitoring agents on decommissioned VMs |
| Hypervisor export | Network diagrams | IP addresses, VLANs | Network diagrams out of date |
| CMDB | Facility drawings | Rack locations, serial numbers | Physical moves not reflected in CMDB |
| Backup system | Hypervisor export | Backed-up VMs vs total VMs | VMs not being backed up (risk) |

### Establishing the Authoritative Source

When sources disagree, establish one as authoritative per data type:

- **VM existence and configuration** -- hypervisor is authoritative (it is the running system)
- **Ownership and business context** -- CMDB is authoritative (when maintained)
- **Network topology** -- live network scans are authoritative (diagrams may be stale)
- **Physical location** -- facility management system or rack elevation drawings are authoritative
- **Application relationships** -- application owner interviews are authoritative (no system captures this reliably)

## Sizing Tier Analysis

### Defining Tier Boundaries

Define tiers that match the target environment's instance types or VM sizing standards:

| Tier | vCPU Range | Memory Range | Disk Range | Typical Workload |
|------|-----------|-------------|------------|------------------|
| **XS (Extra Small)** | 1-2 vCPU | 1-4 GB | < 50 GB | Utility VMs, jump hosts, lightweight monitoring |
| **S (Small)** | 2-4 vCPU | 4-8 GB | 50-100 GB | Web servers, application servers, containers |
| **M (Medium)** | 4-8 vCPU | 8-32 GB | 100-500 GB | Application servers, mid-tier databases |
| **L (Large)** | 8-16 vCPU | 32-64 GB | 500 GB-2 TB | Database servers, large applications |
| **XL (Extra Large)** | 16+ vCPU | 64+ GB | 2+ TB | Enterprise databases, analytics, data warehouses |

### Distribution Analysis

Calculate the percentage of VMs in each tier. A healthy distribution for a typical enterprise looks like:

- XS + S: 40-60% of VMs (many small VMs, but low resource consumption)
- M: 20-30% of VMs
- L: 10-15% of VMs
- XL: 5-10% of VMs (few VMs, but dominant resource consumption)

**Outlier detection:** VMs in the XL tier warrant individual review. They often have the highest migration risk, the longest cutover windows, and the greatest licensing impact. They may also be candidates for right-sizing if actual utilization is significantly below allocation.

## See Also

- `general/workload-migration.md` -- Migration strategy, wave planning, cutover procedures
- `general/physical-server-scope.md` -- Physical server assessment and disposition
- `general/hardware-sizing.md` -- Target environment capacity planning
- `general/capacity-planning.md` -- Capacity planning methodology
- `general/cost-onprem.md` -- On-premises cost modeling
