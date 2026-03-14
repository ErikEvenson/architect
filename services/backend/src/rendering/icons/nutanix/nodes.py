from pathlib import Path

from diagrams.custom import Custom

ICON_DIR = Path(__file__).parent / "resources"


class Prism(Custom):
    def __init__(self, label: str = "Prism Central", **kwargs):
        super().__init__(label, str(ICON_DIR / "prism.png"), **kwargs)


class AHV(Custom):
    def __init__(self, label: str = "AHV", **kwargs):
        super().__init__(label, str(ICON_DIR / "ahv.png"), **kwargs)


class Files(Custom):
    def __init__(self, label: str = "Files", **kwargs):
        super().__init__(label, str(ICON_DIR / "files.png"), **kwargs)


class Objects(Custom):
    def __init__(self, label: str = "Objects", **kwargs):
        super().__init__(label, str(ICON_DIR / "objects.png"), **kwargs)


class Flow(Custom):
    def __init__(self, label: str = "Flow", **kwargs):
        super().__init__(label, str(ICON_DIR / "flow.png"), **kwargs)
