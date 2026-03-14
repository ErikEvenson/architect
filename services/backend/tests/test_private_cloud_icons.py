from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.rendering.base import RenderResult
from src.rendering.icons.nutanix.nodes import AHV, Files, Flow, Objects, Prism
from src.rendering.icons.vmware.nodes import ESXi, NSX, VSAN, VCenter, VSphere
from src.rendering.icons.openstack.nodes import Cinder, Keystone, Neutron, Nova, Swift

API = "/api/v1"


# --- Icon file existence tests ---

class TestIconFilesExist:
    def _check_icon(self, node_class, icon_name):
        icon_dir = Path(node_class.__module__.replace(".", "/")).parent / "resources"
        # Resolve relative to the src directory
        base = Path(__file__).parent.parent / "src" / "rendering" / "icons"
        provider = node_class.__module__.split(".")[-2]
        icon_path = base / provider / "resources" / f"{icon_name}.png"
        assert icon_path.exists(), f"Icon not found: {icon_path}"

    # Nutanix
    def test_nutanix_prism_icon(self):
        self._check_icon(Prism, "prism")

    def test_nutanix_ahv_icon(self):
        self._check_icon(AHV, "ahv")

    def test_nutanix_files_icon(self):
        self._check_icon(Files, "files")

    def test_nutanix_objects_icon(self):
        self._check_icon(Objects, "objects")

    def test_nutanix_flow_icon(self):
        self._check_icon(Flow, "flow")

    # VMware
    def test_vmware_vsphere_icon(self):
        self._check_icon(VSphere, "vsphere")

    def test_vmware_esxi_icon(self):
        self._check_icon(ESXi, "esxi")

    def test_vmware_vcenter_icon(self):
        self._check_icon(VCenter, "vcenter")

    def test_vmware_nsx_icon(self):
        self._check_icon(NSX, "nsx")

    def test_vmware_vsan_icon(self):
        self._check_icon(VSAN, "vsan")

    # OpenStack
    def test_openstack_nova_icon(self):
        self._check_icon(Nova, "nova")

    def test_openstack_neutron_icon(self):
        self._check_icon(Neutron, "neutron")

    def test_openstack_cinder_icon(self):
        self._check_icon(Cinder, "cinder")

    def test_openstack_swift_icon(self):
        self._check_icon(Swift, "swift")

    def test_openstack_keystone_icon(self):
        self._check_icon(Keystone, "keystone")


# --- Node icon path resolution tests ---

class TestNodeIconPaths:
    def test_nutanix_prism_icon_path(self):
        """Verify the icon path resolves to an existing file."""
        nodes_file = Path(__file__).parent.parent / "src" / "rendering" / "icons" / "nutanix" / "nodes.py"
        icon_dir = nodes_file.parent / "resources"
        assert (icon_dir / "prism.png").exists()

    def test_vmware_vsphere_icon_path(self):
        nodes_file = Path(__file__).parent.parent / "src" / "rendering" / "icons" / "vmware" / "nodes.py"
        icon_dir = nodes_file.parent / "resources"
        assert (icon_dir / "vsphere.png").exists()

    def test_openstack_nova_icon_path(self):
        nodes_file = Path(__file__).parent.parent / "src" / "rendering" / "icons" / "openstack" / "nodes.py"
        icon_dir = nodes_file.parent / "resources"
        assert (icon_dir / "nova.png").exists()


# --- Mixed-provider diagram rendering test ---

class TestMixedProviderDiagram:
    @pytest.mark.asyncio
    async def test_render_mixed_provider_diagram(self, client, sample_version):
        """Test that a diagram mixing AWS + Nutanix + VMware can be submitted and rendered."""
        version_id = sample_version["id"]

        mixed_source = '''
from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2
from src.rendering.icons.nutanix.nodes import Prism
from src.rendering.icons.vmware.nodes import VSphere

with Diagram("Hybrid Cloud", show=False, outformat=["svg", "png"]):
    with Cluster("AWS"):
        ec2 = EC2("web")
    with Cluster("Nutanix"):
        prism = Prism("Prism Central")
    with Cluster("VMware"):
        vsphere = VSphere("vSphere")
    ec2 >> prism
    ec2 >> vsphere
'''

        art = await client.post(
            f"{API}/versions/{version_id}/artifacts",
            json={
                "name": "Hybrid Cloud",
                "artifact_type": "diagram",
                "engine": "diagrams_py",
                "source_code": mixed_source,
            },
        )
        artifact_id = art.json()["id"]

        mock_result = RenderResult(
            success=True, output_paths=["hybrid_cloud.svg", "hybrid_cloud.png"]
        )
        with patch(
            "src.services.render_service.DiagramsRenderer.render",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            resp = await client.post(
                f"{API}/versions/{version_id}/artifacts/{artifact_id}/render"
            )

        assert resp.status_code == 202
        assert resp.json()["render_status"] == "success"
        assert "hybrid_cloud.svg" in resp.json()["output_paths"]
