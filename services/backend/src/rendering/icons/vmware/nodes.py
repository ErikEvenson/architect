from pathlib import Path

from diagrams.custom import Custom

ICON_DIR = Path(__file__).parent / "resources"


class VSphere(Custom):
    def __init__(self, label: str = "vSphere", **kwargs):
        super().__init__(label, str(ICON_DIR / "vsphere.png"), **kwargs)


class ESXi(Custom):
    def __init__(self, label: str = "ESXi", **kwargs):
        super().__init__(label, str(ICON_DIR / "esxi.png"), **kwargs)


class VCenter(Custom):
    def __init__(self, label: str = "vCenter", **kwargs):
        super().__init__(label, str(ICON_DIR / "vcenter.png"), **kwargs)


class NSX(Custom):
    def __init__(self, label: str = "NSX", **kwargs):
        super().__init__(label, str(ICON_DIR / "nsx.png"), **kwargs)


class VSAN(Custom):
    def __init__(self, label: str = "vSAN", **kwargs):
        super().__init__(label, str(ICON_DIR / "vsan.png"), **kwargs)
