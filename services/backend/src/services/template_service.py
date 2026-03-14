from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

AVAILABLE_TEMPLATES = {
    "architecture": "architecture.md.j2",
    "runbook": "runbook.md.j2",
}


def render_template(template_name: str, **kwargs) -> str | None:
    """Render a document template with the given variables. Returns None if template not found."""
    filename = AVAILABLE_TEMPLATES.get(template_name)
    if not filename:
        return None
    template = env.get_template(filename)
    return template.render(**kwargs)


def list_templates() -> list[str]:
    """Return available template names."""
    return list(AVAILABLE_TEMPLATES.keys())
