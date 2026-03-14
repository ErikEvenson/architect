# Private Cloud Icons Specification

## Overview

Extend the `diagrams_py` renderer with custom node classes for private cloud providers: Nutanix, VMware, and OpenStack. These nodes work alongside the built-in public cloud nodes (AWS, Azure, GCP) in mixed-provider diagrams.

## Icon Sources

### Nutanix
- Source: Nutanix brand/media resources
- Key icons: Prism, AHV, Files, Objects, Flow, Calm, Era, Karbon, Xi
- Format: PNG (converted from SVG/brand assets as needed)
- License: Used for architectural diagram purposes per brand guidelines

### VMware
- Source: VMware icon library / media resources
- Key icons: vSphere, ESXi, vCenter, NSX, vSAN, HCX, Tanzu, vRealize
- Format: PNG
- License: Used for architectural diagram purposes per brand guidelines

### OpenStack
- Source: OpenStack project logos (openstack.org)
- Key icons: Nova, Neutron, Cinder, Swift, Keystone, Glance, Heat, Horizon
- Format: PNG
- License: Apache 2.0 (OpenStack project logos are freely available)

## Icon Directory Structure

```
services/backend/src/rendering/icons/
├── __init__.py
├── nutanix/
│   ├── __init__.py
│   ├── nodes.py          # Custom node wrapper classes
│   └── resources/        # PNG icon files
│       ├── prism.png
│       ├── ahv.png
│       ├── files.png
│       ├── objects.png
│       ├── flow.png
│       └── ...
├── vmware/
│   ├── __init__.py
│   ├── nodes.py
│   └── resources/
│       ├── vsphere.png
│       ├── esxi.png
│       ├── vcenter.png
│       ├── nsx.png
│       ├── vsan.png
│       └── ...
└── openstack/
    ├── __init__.py
    ├── nodes.py
    └── resources/
        ├── nova.png
        ├── neutron.png
        ├── cinder.png
        ├── swift.png
        ├── keystone.png
        └── ...
```

## Custom Node Classes

Each provider module exposes node classes that use the `diagrams` library's `Custom` node:

```python
from diagrams.custom import Custom
from pathlib import Path

ICON_DIR = Path(__file__).parent / "resources"

class Prism(Custom):
    def __init__(self, label: str, **kwargs):
        super().__init__(label, str(ICON_DIR / "prism.png"), **kwargs)
```

### Usage in Diagrams

```python
from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2
from src.rendering.icons.nutanix.nodes import Prism, AHV
from src.rendering.icons.vmware.nodes import VSphere

with Diagram("Hybrid Cloud", show=False, outformat=["svg", "png"]):
    with Cluster("AWS"):
        ec2 = EC2("web")
    with Cluster("On-Prem - Nutanix"):
        prism = Prism("Prism Central")
        ahv = AHV("Hypervisor")
    with Cluster("On-Prem - VMware"):
        vsphere = VSphere("vSphere")

    ec2 >> prism >> ahv
    ec2 >> vsphere
```

## Provider Node Classes

### Nutanix
| Class | Icon | Description |
|---|---|---|
| `Prism` | prism.png | Prism Central management |
| `AHV` | ahv.png | Acropolis Hypervisor |
| `Files` | files.png | File storage |
| `Objects` | objects.png | Object storage |
| `Flow` | flow.png | Network microsegmentation |

### VMware
| Class | Icon | Description |
|---|---|---|
| `VSphere` | vsphere.png | vSphere platform |
| `ESXi` | esxi.png | ESXi hypervisor |
| `VCenter` | vcenter.png | vCenter Server |
| `NSX` | nsx.png | NSX networking |
| `VSAN` | vsan.png | vSAN storage |

### OpenStack
| Class | Icon | Description |
|---|---|---|
| `Nova` | nova.png | Compute |
| `Neutron` | neutron.png | Networking |
| `Cinder` | cinder.png | Block storage |
| `Swift` | swift.png | Object storage |
| `Keystone` | keystone.png | Identity |

## Placeholder Icons

Until real vendor icons are sourced, generate simple placeholder PNGs:
- 64x64 pixels
- Solid color background (Nutanix: blue, VMware: gray, OpenStack: red)
- White text with abbreviation (e.g., "PC" for Prism Central)
- These are functional placeholders that allow the full rendering pipeline to work

## Docker Image

Icons are baked into the backend Docker image via the `COPY src/ /app/src/` step.
No additional Dockerfile changes needed — icons live in the source tree under `src/rendering/icons/`.

## Testing

- Verify each custom node class resolves its icon path correctly
- Verify a mixed-provider diagram (AWS + Nutanix + VMware) can be constructed without errors
- Icon existence tests (all referenced PNGs exist)
