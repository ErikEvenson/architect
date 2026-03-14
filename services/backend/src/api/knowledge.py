import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

# Knowledge directory is at the repo root, mounted or available at this path
# In Docker, we'll copy it into the image. In dev, it's relative.
KNOWLEDGE_DIR = Path(os.environ.get("KNOWLEDGE_DIR", "/app/knowledge"))


class KnowledgeFile(BaseModel):
    path: str
    name: str
    category: str


class KnowledgeTree(BaseModel):
    general: list[KnowledgeFile]
    providers: dict[str, list[KnowledgeFile]]
    patterns: list[KnowledgeFile]


class KnowledgeContent(BaseModel):
    path: str
    name: str
    content: str


@router.get("", response_model=KnowledgeTree)
async def list_knowledge():
    """List all available knowledge files organized by category."""
    tree = KnowledgeTree(general=[], providers={}, patterns=[])

    # General
    general_dir = KNOWLEDGE_DIR / "general"
    if general_dir.exists():
        for f in sorted(general_dir.glob("*.md")):
            tree.general.append(KnowledgeFile(
                path=f"general/{f.name}",
                name=f.stem.replace("-", " ").title(),
                category="general",
            ))

    # Providers
    providers_dir = KNOWLEDGE_DIR / "providers"
    if providers_dir.exists():
        for provider_dir in sorted(providers_dir.iterdir()):
            if provider_dir.is_dir():
                files = []
                for f in sorted(provider_dir.glob("*.md")):
                    files.append(KnowledgeFile(
                        path=f"providers/{provider_dir.name}/{f.name}",
                        name=f.stem.replace("-", " ").title(),
                        category=provider_dir.name,
                    ))
                if files:
                    tree.providers[provider_dir.name] = files

    # Patterns
    patterns_dir = KNOWLEDGE_DIR / "patterns"
    if patterns_dir.exists():
        for f in sorted(patterns_dir.glob("*.md")):
            tree.patterns.append(KnowledgeFile(
                path=f"patterns/{f.name}",
                name=f.stem.replace("-", " ").title(),
                category="patterns",
            ))

    return tree


@router.get("/{path:path}", response_model=KnowledgeContent)
async def get_knowledge_file(path: str):
    """Read a specific knowledge file."""
    file_path = KNOWLEDGE_DIR / path

    # Prevent path traversal
    if not file_path.resolve().is_relative_to(KNOWLEDGE_DIR.resolve()):
        raise HTTPException(status_code=400, detail="Invalid path")

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Knowledge file not found")

    content = file_path.read_text(encoding="utf-8")
    name = file_path.stem.replace("-", " ").title()

    return KnowledgeContent(path=path, name=name, content=content)
