# Azure Bicep

Domain-specific language (DSL) for deploying Azure resources declaratively. Bicep compiles to ARM JSON templates, providing cleaner syntax, type safety, and first-class tooling while maintaining full ARM feature parity.

---

## Checklist

- [ ] **[Critical]** Define all Azure resources in Bicep files — avoid manual portal provisioning for anything beyond exploration
- [ ] **[Critical]** Use `what-if` preview before every production deployment (`az deployment group what-if -f main.bicep -p params.bicepparam`)
- [ ] **[Critical]** Mark sensitive parameters with `@secure()` decorator to prevent values from appearing in deployment logs or Azure activity logs
- [ ] **[Critical]** Use deployment scopes intentionally — deploy at resource group scope by default; use subscription/management group scope only for cross-resource-group or policy resources
- [ ] **[Critical]** Pin module versions in registry references (`br:myregistry.azurecr.io/bicep/modules/vnet:1.2.0`) — never use `latest` in production
- [ ] **[Recommended]** Run the Bicep linter in CI (`az bicep build -f main.bicep` emits linter warnings; configure `bicepconfig.json` for custom rules)
- [ ] **[Recommended]** Use modules to encapsulate reusable components (networking, compute, monitoring) with well-defined parameter interfaces
- [ ] **[Recommended]** Leverage Azure Verified Modules (AVM) for standard resource patterns rather than writing from scratch
- [ ] **[Recommended]** Use `.bicepparam` files to separate parameter values from templates for environment-specific deployments
- [ ] **[Recommended]** Implement deployment stacks for lifecycle management and deny assignments on managed resources
- [ ] **[Recommended]** Use user-defined types (`type`) to create strongly-typed parameter contracts between modules
- [ ] **[Optional]** Set up a private Bicep module registry in Azure Container Registry for organizational module sharing
- [ ] **[Optional]** Use `existing` keyword to reference pre-existing resources without redefining them
- [ ] **[Optional]** Adopt user-defined functions for complex expressions that repeat across templates

---

## Why This Matters

Bicep is Microsoft's recommended language for Azure infrastructure, replacing raw ARM JSON templates. It compiles 1:1 to ARM, meaning there is no runtime dependency or additional service — Azure Resource Manager processes the same JSON it always has. Bicep provides significant developer experience improvements: type safety catches errors at authoring time, IntelliSense in VS Code provides auto-completion for every resource property, and the syntax eliminates the verbosity of ARM JSON (typically 50-70% fewer lines). Unlike Terraform, Bicep has zero-delay support for new Azure resource types and API versions because it generates ARM directly. Deployment stacks add lifecycle management that ARM templates alone lack — grouping resources and protecting them with deny assignments. For Azure-centric organizations, Bicep reduces tooling complexity while providing the same declarative, idempotent deployment model.

---

## Bicep vs ARM Templates

```bicep
// Bicep — clean, readable
param location string = resourceGroup().location
param storageName string

resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

output storageId string = storage.id
```

The equivalent ARM JSON is ~60 lines with explicit schema declarations, parameter definitions, and nested property objects. Bicep compiles to ARM with `az bicep build -f main.bicep`.

## Parameters, Variables, Outputs, and Decorators

```bicep
@description('Environment name used for resource naming')
@allowed(['dev', 'staging', 'prod'])
param environment string

@description('Administrator password')
@secure()
@minLength(12)
param adminPassword string

var resourcePrefix = '${environment}-myapp'
var tags = {
  environment: environment
  managedBy: 'bicep'
}

output vnetId string = vnet.id
output subnetIds array = [for (subnet, i) in subnets: vnet.properties.subnets[i].id]
```

Parameter files (`.bicepparam`):

```bicep
using './main.bicep'

param environment = 'prod'
param adminPassword = readEnvironmentVariable('ADMIN_PASSWORD')
```

## Modules

Modules decompose templates into reusable components:

```bicep
// main.bicep
module network 'modules/vnet.bicep' = {
  name: 'network-deployment'
  params: {
    vnetName: '${resourcePrefix}-vnet'
    addressPrefix: '10.0.0.0/16'
    subnets: [
      { name: 'web', prefix: '10.0.1.0/24' }
      { name: 'app', prefix: '10.0.2.0/24' }
      { name: 'data', prefix: '10.0.3.0/24' }
    ]
  }
}

module appService 'modules/appservice.bicep' = {
  name: 'appservice-deployment'
  params: {
    subnetId: network.outputs.subnetIds[1]  // implicit dependency
  }
}
```

Registry-based modules:

```bicep
module vnet 'br:myregistry.azurecr.io/bicep/modules/vnet:1.2.0' = {
  name: 'vnet-deployment'
  params: { ... }
}

// Azure Verified Modules
module storageAccount 'br/public:avm/res/storage/storage-account:0.9.0' = {
  name: 'storage-deployment'
  params: { ... }
}
```

## Resource Dependencies

Bicep resolves dependencies automatically from property references:

```bicep
resource vnet 'Microsoft.Network/virtualNetworks@2023-05-01' = {
  name: 'myVnet'
  // ...
}

resource subnet 'Microsoft.Network/virtualNetworks/subnets@2023-05-01' = {
  parent: vnet                    // implicit dependency via parent
  name: 'mySubnet'
  properties: {
    addressPrefix: '10.0.1.0/24'
  }
}

resource nic 'Microsoft.Network/networkInterfaces@2023-05-01' = {
  name: 'myNic'
  properties: {
    ipConfigurations: [{
      name: 'ipconfig1'
      properties: {
        subnet: { id: subnet.id }  // implicit dependency via property reference
      }
    }]
  }
}
```

Use explicit `dependsOn` only when there is no property reference but an ordering requirement exists (rare).

## Conditional Deployment and Loops

```bicep
// Conditional
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = if (environment == 'prod') {
  name: '${resourcePrefix}-logs'
  location: location
  properties: { retentionInDays: 90 }
}

// Loop over array
param subnets array
resource nsg 'Microsoft.Network/networkSecurityGroups@2023-05-01' = [for subnet in subnets: {
  name: '${subnet.name}-nsg'
  location: location
}]

// Loop with index and filter
resource publicSubnetNsg 'Microsoft.Network/networkSecurityGroups@2023-05-01' = [for (subnet, i) in subnets: if (subnet.isPublic) {
  name: '${subnet.name}-public-nsg'
  location: location
}]
```

## Deployment Scopes

```bicep
// Resource group scope (default)
az deployment group create -f main.bicep -g myResourceGroup

// Subscription scope — for resource groups, policies, role assignments
targetScope = 'subscription'
az deployment sub create -f main.bicep -l eastus

// Management group scope — for policies across subscriptions
targetScope = 'managementGroup'
az deployment mg create -f main.bicep -m myManagementGroup -l eastus

// Tenant scope — for management group hierarchies
targetScope = 'tenant'
az deployment tenant create -f main.bicep -l eastus
```

Cross-scope module deployments:

```bicep
targetScope = 'subscription'

resource rg 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: 'myapp-prod-rg'
  location: 'eastus'
}

module resources 'modules/resources.bicep' = {
  scope: rg            // deploy into the resource group created above
  name: 'resources'
  params: { ... }
}
```

## What-If Preview

```bash
# Preview changes before deploying
az deployment group what-if \
  --resource-group myapp-prod-rg \
  --template-file main.bicep \
  --parameters @params.prod.bicepparam

# Output shows: Create, Delete, Modify, NoChange, Ignore
# Color-coded: green (create), orange (modify), red (delete)
```

## Deployment Stacks

Deployment stacks manage the lifecycle of resources as a group, including cleanup of removed resources and deny assignments:

```bash
# Create a deployment stack at resource group scope
az stack group create \
  --name myapp-stack \
  --resource-group myapp-prod-rg \
  --template-file main.bicep \
  --deny-settings-mode denyWriteAndDelete \
  --action-on-unmanage deleteAll

# Resources removed from template are automatically deleted
# Deny assignments prevent manual modification of managed resources
```

## User-Defined Types and Functions

```bicep
// User-defined type
type subnetConfig = {
  name: string
  addressPrefix: string
  @description('Whether to create a NSG for this subnet')
  createNsg: bool?
}

param subnets subnetConfig[]

// User-defined function
func buildResourceName(prefix string, resourceType string, env string) string =>
  '${prefix}-${resourceType}-${env}'
```

## Bicep vs Terraform for Azure

| Aspect | Bicep | Terraform |
|---|---|---|
| Scope | Azure only | Multi-cloud |
| Language | Bicep DSL | HCL |
| State | Managed by Azure (no state file) | Self-managed state backend |
| New Azure features | Immediate (same day as ARM) | Days to weeks via AzureRM provider |
| Tooling | VS Code extension, built into Azure CLI | Separate installation, providers |
| Module registry | Azure Container Registry, public AVM | Terraform Registry |
| Learning curve | Low for Azure-familiar teams | Moderate; HCL syntax + state concepts |
| Destroy/cleanup | Deployment stacks with `deleteAll` | `terraform destroy` |
| Multi-cloud | Not supported | Core strength |

---

## Common Decisions (ADR Triggers)

- **Bicep vs Terraform for Azure-only infrastructure**: Bicep offers zero-lag Azure support, no state file management, and native Azure CLI integration. Terraform offers multi-cloud and a larger module ecosystem. Record which is chosen and why.
- **Module registry strategy**: Decide between Azure Container Registry (private), public AVM modules, or Git-based module references. Consider versioning, access control, and discoverability.
- **Deployment scope hierarchy**: Determine which resources deploy at which scope (tenant, management group, subscription, resource group). This affects template organization and RBAC requirements.
- **Deployment stacks vs traditional deployments**: Deployment stacks add lifecycle management and deny assignments but are newer. Decide whether the benefits justify adoption versus proven `az deployment group create`.
- **Parameter management**: Choose between `.bicepparam` files, Azure Key Vault references, pipeline variables, or environment variables for sensitive and environment-specific values.
- **Bicep linter configuration**: Decide which linter rules to enforce as errors vs warnings. Custom `bicepconfig.json` rules can enforce organizational standards.

---

## Reference Architectures

### Hub-and-Spoke Network (Subscription Scope)

```
targetScope = 'subscription'
  |
  |-- Resource Group: hub-network-rg
  |     |-- Module: hub-vnet (firewall subnet, gateway subnet, bastion subnet)
  |     |-- Module: azure-firewall (route tables, firewall policies)
  |     |-- Module: vpn-gateway (site-to-site, point-to-site)
  |
  |-- Resource Group: spoke-app1-rg
  |     |-- Module: spoke-vnet (peered to hub)
  |     |-- Module: app-service (integrated with spoke subnet)
  |     |-- Module: sql-database (private endpoint in data subnet)
  |
  |-- Resource Group: spoke-app2-rg
        |-- Module: spoke-vnet (peered to hub)
        |-- Module: aks-cluster (system + user node pools)
```

### CI/CD Pipeline (GitHub Actions)

```
Push to main
  --> az bicep build (compile + lint)
  --> az deployment group what-if (preview changes)
  --> Manual approval (required for prod)
  --> az stack group create (deploy with lifecycle management)
  --> Smoke tests (verify endpoints, health checks)
  --> Notify team (Slack/Teams webhook)
```

### Multi-Environment with Module Registry

```
Azure Container Registry (module registry)
  |-- bicep/modules/vnet:1.2.0
  |-- bicep/modules/appservice:2.0.1
  |-- bicep/modules/sql:1.5.3
  |
Environments (each a parameter file):
  |-- params.dev.bicepparam    --> dev resource group
  |-- params.staging.bicepparam --> staging resource group
  |-- params.prod.bicepparam   --> prod resource group
  |
  main.bicep references registry modules with pinned versions
  Each environment uses the same template with different parameters
```
