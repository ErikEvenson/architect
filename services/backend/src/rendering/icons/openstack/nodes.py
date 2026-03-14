from pathlib import Path

from diagrams.custom import Custom

ICON_DIR = Path(__file__).parent / "resources"


class Nova(Custom):
    def __init__(self, label: str = "Nova", **kwargs):
        super().__init__(label, str(ICON_DIR / "nova.png"), **kwargs)


class Neutron(Custom):
    def __init__(self, label: str = "Neutron", **kwargs):
        super().__init__(label, str(ICON_DIR / "neutron.png"), **kwargs)


class Cinder(Custom):
    def __init__(self, label: str = "Cinder", **kwargs):
        super().__init__(label, str(ICON_DIR / "cinder.png"), **kwargs)


class Swift(Custom):
    def __init__(self, label: str = "Swift", **kwargs):
        super().__init__(label, str(ICON_DIR / "swift.png"), **kwargs)


class Keystone(Custom):
    def __init__(self, label: str = "Keystone", **kwargs):
        super().__init__(label, str(ICON_DIR / "keystone.png"), **kwargs)
