"""Parse knowledge library markdown files into individual checklist items and sections."""

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ParsedChunk:
    """A single chunk extracted from a knowledge file."""

    source_file: str
    source_type: str  # "knowledge_file", "vendor_doc", or "upload"
    section: str
    checklist_item: str | None
    priority: str | None  # "critical", "recommended", "optional"
    content: str
    content_hash: str = field(init=False)

    def __post_init__(self):
        self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()


# Pattern to match checklist items with priority tags
CHECKLIST_PATTERN = re.compile(
    r"^- \[[ x]\] \*\*\[(Critical|Recommended|Optional)\]\*\*\s+(.+)",
    re.IGNORECASE,
)

# Pattern to match markdown headings
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)")


def parse_knowledge_file(file_path: Path, base_dir: Path) -> list[ParsedChunk]:
    """Parse a knowledge file into individual chunks.

    Extracts each checklist item as its own chunk, preserving priority tags.
    Also extracts non-checklist sections (Why This Matters, Common Decisions, etc.)
    as contextual chunks.
    """
    relative_path = str(file_path.relative_to(base_dir))
    content = file_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    chunks: list[ParsedChunk] = []

    current_section = "Untitled"
    section_content_lines: list[str] = []

    def flush_section():
        """Flush accumulated non-checklist section content as a chunk."""
        if section_content_lines:
            text = "\n".join(section_content_lines).strip()
            if text and current_section not in ("Untitled", "Checklist", "See Also"):
                chunks.append(ParsedChunk(
                    source_file=relative_path,
                    source_type="knowledge_file",
                    section=current_section,
                    checklist_item=None,
                    priority=None,
                    content=text,
                ))

    for line in lines:
        # Check for heading
        heading_match = HEADING_PATTERN.match(line)
        if heading_match:
            flush_section()
            section_content_lines = []
            current_section = heading_match.group(2).strip()
            continue

        # Check for checklist item
        checklist_match = CHECKLIST_PATTERN.match(line)
        if checklist_match:
            priority = checklist_match.group(1).lower()
            item_text = checklist_match.group(2).strip()
            chunks.append(ParsedChunk(
                source_file=relative_path,
                source_type="knowledge_file",
                section=current_section,
                checklist_item=item_text,
                priority=priority,
                content=item_text,
            ))
            continue

        # Accumulate non-checklist content
        section_content_lines.append(line)

    # Flush final section
    flush_section()

    return chunks


def parse_knowledge_directory(knowledge_dir: Path) -> list[ParsedChunk]:
    """Parse all knowledge files in a directory tree."""
    chunks: list[ParsedChunk] = []

    for md_file in sorted(knowledge_dir.rglob("*.md")):
        # Skip non-knowledge files
        if md_file.name in ("README.md", "CONTRIBUTING.md", "WORKFLOW.md", "references.md"):
            continue

        chunks.extend(parse_knowledge_file(md_file, knowledge_dir))

    return chunks


def extract_vendor_doc_urls(knowledge_dir: Path) -> list[dict[str, str]]:
    """Extract vendor documentation URLs from knowledge files.

    Looks for markdown links in See Also sections and inline references
    that point to external vendor documentation.
    """
    url_pattern = re.compile(r"\[([^\]]+)\]\((https?://[^\)]+)\)")
    urls: list[dict[str, str]] = []
    seen: set[str] = set()

    for md_file in sorted(knowledge_dir.rglob("*.md")):
        if md_file.name in ("README.md", "CONTRIBUTING.md", "WORKFLOW.md", "references.md"):
            continue

        content = md_file.read_text(encoding="utf-8")
        relative_path = str(md_file.relative_to(knowledge_dir))

        for match in url_pattern.finditer(content):
            url = match.group(2)
            if url not in seen:
                seen.add(url)
                urls.append({
                    "title": match.group(1),
                    "url": url,
                    "source_file": relative_path,
                })

    return urls


def parse_vendor_doc_content(
    url: str,
    title: str,
    content: str,
    max_chunk_size: int = 1000,
) -> list[ParsedChunk]:
    """Parse fetched vendor doc content into chunks."""
    chunks: list[ParsedChunk] = []

    # Split by paragraphs, group into chunks of max_chunk_size chars
    paragraphs = content.split("\n\n")
    current_chunk_lines: list[str] = []
    current_size = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if current_size + len(para) > max_chunk_size and current_chunk_lines:
            chunk_text = "\n\n".join(current_chunk_lines)
            chunks.append(ParsedChunk(
                source_file=url,
                source_type="vendor_doc",
                section=title,
                checklist_item=None,
                priority=None,
                content=chunk_text,
            ))
            current_chunk_lines = []
            current_size = 0

        current_chunk_lines.append(para)
        current_size += len(para)

    if current_chunk_lines:
        chunk_text = "\n\n".join(current_chunk_lines)
        chunks.append(ParsedChunk(
            source_file=url,
            source_type="vendor_doc",
            section=title,
            checklist_item=None,
            priority=None,
            content=chunk_text,
        ))

    return chunks


# Text-based content types that can be indexed
INDEXABLE_CONTENT_TYPES = {
    "text/plain",
    "text/markdown",
    "text/csv",
    "text/html",
    "text/xml",
    "application/json",
    "application/xml",
    "application/yaml",
    "application/x-yaml",
    "text/yaml",
    "text/x-yaml",
}

# Extensions to treat as text even if content_type is generic
INDEXABLE_EXTENSIONS = {
    ".md", ".txt", ".csv", ".json", ".xml", ".yaml", ".yml",
    ".html", ".htm", ".log", ".cfg", ".conf", ".ini", ".toml",
    ".py", ".js", ".ts", ".sh", ".tf", ".hcl",
}


def is_indexable(filename: str, content_type: str) -> bool:
    """Check whether a file is text-based and suitable for indexing."""
    if content_type in INDEXABLE_CONTENT_TYPES:
        return True
    if content_type.startswith("text/"):
        return True
    ext = Path(filename).suffix.lower()
    return ext in INDEXABLE_EXTENSIONS


def parse_upload_content(
    source_label: str,
    filename: str,
    content: str,
    max_chunk_size: int = 1000,
) -> list[ParsedChunk]:
    """Parse uploaded file content into chunks for embedding.

    Args:
        source_label: Identifier for the upload (e.g. "upload:{upload_id}").
        filename: Original filename (used as section label).
        content: The text content of the file.
        max_chunk_size: Max chars per chunk.
    """
    chunks: list[ParsedChunk] = []

    # If it looks like markdown, use the knowledge file parser logic
    if filename.lower().endswith(".md"):
        lines = content.split("\n")
        current_section = filename
        section_content_lines: list[str] = []

        def flush():
            if section_content_lines:
                text = "\n".join(section_content_lines).strip()
                if text:
                    chunks.append(ParsedChunk(
                        source_file=source_label,
                        source_type="upload",
                        section=current_section,
                        checklist_item=None,
                        priority=None,
                        content=text,
                    ))

        for line in lines:
            heading_match = HEADING_PATTERN.match(line)
            if heading_match:
                flush()
                section_content_lines = []
                current_section = heading_match.group(2).strip()
                continue

            checklist_match = CHECKLIST_PATTERN.match(line)
            if checklist_match:
                priority = checklist_match.group(1).lower()
                item_text = checklist_match.group(2).strip()
                chunks.append(ParsedChunk(
                    source_file=source_label,
                    source_type="upload",
                    section=current_section,
                    checklist_item=item_text,
                    priority=priority,
                    content=item_text,
                ))
                continue

            section_content_lines.append(line)

        flush()
        return chunks

    # For other text files, chunk by paragraphs
    paragraphs = content.split("\n\n")
    current_chunk_lines: list[str] = []
    current_size = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if current_size + len(para) > max_chunk_size and current_chunk_lines:
            chunks.append(ParsedChunk(
                source_file=source_label,
                source_type="upload",
                section=filename,
                checklist_item=None,
                priority=None,
                content="\n\n".join(current_chunk_lines),
            ))
            current_chunk_lines = []
            current_size = 0

        current_chunk_lines.append(para)
        current_size += len(para)

    if current_chunk_lines:
        chunks.append(ParsedChunk(
            source_file=source_label,
            source_type="upload",
            section=filename,
            checklist_item=None,
            priority=None,
            content="\n\n".join(current_chunk_lines),
        ))

    return chunks
