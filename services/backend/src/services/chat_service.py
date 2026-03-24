"""Chat service: system prompt assembly and tool execution for architecture chat."""

import json
import os
import uuid
from pathlib import Path

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.adr import ADR
from src.models.artifact import Artifact
from src.models.project import Project
from src.models.question import Question
from src.models.version import Version
from src.services import embedding_service

logger = structlog.get_logger()

KNOWLEDGE_DIR = Path(os.environ.get("KNOWLEDGE_DIR", "/app/knowledge"))
CLAUDE_MD_PATH = Path(os.environ.get("CLAUDE_MD_PATH", "/app/CLAUDE.md"))
WORKFLOW_PATH = KNOWLEDGE_DIR / "WORKFLOW.md"


def _read_file_safe(path: Path) -> str | None:
    """Read a file, returning None if it does not exist."""
    try:
        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8")
    except Exception as e:
        logger.warning("Failed to read file", path=str(path), error=str(e))
    return None


async def build_system_prompt(
    version_id: str | None,
    session: AsyncSession,
) -> str:
    """Assemble the system prompt for the architecture chat LLM."""
    sections: list[str] = []

    # --- Role ---
    sections.append(
        "You are an architecture design assistant helping create cloud infrastructure "
        "designs. You have access to a knowledge library of best practices, checklists, "
        "and design patterns. You can create and modify architecture artifacts (diagrams, "
        "documents), record architectural decision records (ADRs), and manage discovery "
        "questions."
    )

    # --- Behavioral rules ---
    sections.append(
        "## Behavioral Rules\n"
        "- Ask clarifying questions one at a time. Do not overwhelm the user with "
        "multiple questions simultaneously.\n"
        "- Always create ADRs for architectural decisions immediately when a decision "
        "is made.\n"
        "- Cross-reference the knowledge library when building artifacts and asking "
        "questions.\n"
        "- Use [Critical] checklist items from knowledge files to formulate questions.\n"
        "- Follow workflow steps strictly. Never skip general knowledge files for "
        "specialized projects.\n"
        "- Collect all context before writing artifacts. Only recreate artifacts when "
        "explicitly told to.\n"
        "- Artifacts must never indicate AI involvement in their generation.\n"
        "- Artifacts must not reference RAG, vector search, knowledge library, or any "
        "generation process.\n"
        "- Every version is an independent design, not a migration step from a previous "
        "version.\n"
        "- Do thorough architecture analysis across all concerns (networking, security, "
        "storage, compute, identity, monitoring, DR, compliance) before generating "
        "diagrams.\n"
        "- For OpenStack and on-premises designs, always include physical host and "
        "cluster design, not just tenant resources.\n"
        "- Always use stack-specific icons (Python diagrams library) over plain D2 when "
        "cloud provider icons are available.\n"
        "- **CRITICAL: Always base your answers on knowledge library content, not your "
        "training data.** When a user asks about a technology or design topic, search "
        "the knowledge library first, read the relevant files, and present what the "
        "knowledge library says. Cite the source file (e.g., 'Per providers/azure/compute.md'). "
        "If the knowledge library doesn't cover a topic, say so explicitly and offer "
        "your general knowledge as a supplement, clearly marked as such.\n"
        "- When search results come back, read the top-scoring files in full using "
        "read_knowledge_file before answering. Do not just summarize the search snippets — "
        "load the actual files and present their checklist items and recommendations.\n"
        "- Present knowledge library content in a structured way: list the [Critical], "
        "[Recommended], and [Optional] checklist items, explain why they matter, and "
        "highlight the Common Decisions (ADR triggers)."
    )

    # --- Available tools ---
    sections.append(
        "## Available Tools\n"
        "You have access to tools for:\n"
        "- **search_knowledge**: Semantic search across the knowledge library (best "
        "practices, checklists, patterns)\n"
        "- **read_knowledge_file**: Read the full content of a specific knowledge file\n"
        "- **list_artifacts / read_artifact / create_artifact / update_artifact**: "
        "Manage architecture artifacts (diagrams, documents)\n"
        "- **trigger_render**: Render an artifact to produce output files (SVG, PNG, "
        "PDF)\n"
        "- **list_adrs / create_adr**: Manage architectural decision records\n"
        "- **list_questions / create_question / update_question**: Manage discovery "
        "questions\n\n"
        "**How to use the knowledge library:**\n"
        "1. Use **search_knowledge** first to find relevant content by topic. It returns "
        "the source file paths and matching content.\n"
        "2. Use **read_knowledge_file** to load the full file when you need details. "
        "Pass the relative path from the search results (e.g., 'providers/azure/compute.md').\n"
        "3. There is NO single file per provider. Content is organized as:\n"
        "   - general/ — universal concerns (networking.md, compute.md, security.md, disaster-recovery.md, cost.md, etc.)\n"
        "   - providers/{provider}/ — provider-specific files (e.g., providers/azure/compute.md, providers/azure/networking.md, providers/aws/s3.md)\n"
        "   - patterns/ — architecture patterns (three-tier-web.md, microservices.md, hybrid-cloud.md, etc.)\n"
        "   - compliance/ — compliance frameworks (pci-dss.md, hipaa.md, soc2.md, etc.)\n"
        "   - frameworks/ — well-architected frameworks (aws-well-architected.md, azure-well-architected.md, etc.)\n"
        "   - failures/ — anti-patterns and failure modes\n\n"
        "Always search first, then read specific files. Never guess file paths."
    )

    # --- CLAUDE.md content ---
    claude_md = _read_file_safe(CLAUDE_MD_PATH)
    if claude_md:
        sections.append(f"## Project Instructions\n{claude_md}")

    # --- Workflow ---
    workflow = _read_file_safe(WORKFLOW_PATH)
    if workflow:
        sections.append(f"## Architecture Session Workflow\n{workflow}")

    # --- Project context ---
    if version_id:
        context = await _build_project_context(version_id, session)
        if context:
            sections.append(f"## Current Project Context\n{context}")

    return "\n\n".join(sections)


async def prefetch_rag_context(
    messages: list,
    session: AsyncSession,
    top_k: int = 10,
    min_score: float = 0.35,
) -> str | None:
    """Search the knowledge library for the user's latest message and return
    formatted context to inject into the system prompt.

    This ensures the LLM has relevant knowledge library content directly in
    its context window, rather than relying on the model to call tools.
    """
    # Find the last user message
    user_query = None
    for msg in reversed(messages):
        role = msg.role if hasattr(msg, "role") else msg.get("role")
        content = msg.content if hasattr(msg, "content") else msg.get("content")
        if role == "user" and content:
            user_query = content
            break

    if not user_query:
        return None

    # Check if embeddings are indexed
    try:
        status = await embedding_service.get_index_status(session)
        if not status.get("indexed"):
            return None
    except Exception:
        return None

    # Search the knowledge library
    try:
        results = await embedding_service.search_knowledge(
            session=session,
            query=user_query,
            top_k=top_k,
            min_score=min_score,
        )
    except Exception:
        return None

    if not results:
        return None

    # Group results by source file for cleaner presentation
    files: dict[str, list[dict]] = {}
    for r in results:
        src = r["source_file"]
        if src not in files:
            files[src] = []
        files[src].append(r)

    # Also load the full content of the top-scoring unique files
    seen_files: set[str] = set()
    full_file_contents: list[str] = []
    max_files_to_load = 2  # Limit to keep context focused

    for r in results:
        src = r["source_file"]
        if src in seen_files or src.startswith("http"):
            continue
        seen_files.add(src)
        if len(full_file_contents) >= max_files_to_load:
            break
        file_path = KNOWLEDGE_DIR / src
        if file_path.exists() and file_path.is_file():
            try:
                content = file_path.read_text(encoding="utf-8")
                full_file_contents.append(
                    f"### File: {src}\n\n{content}"
                )
            except Exception:
                pass

    # Build the context section
    parts = [
        "## Knowledge Library Context (auto-loaded based on your question)\n",
        "IMPORTANT: The following knowledge library files were loaded for this question. "
        "You MUST base your response on this content. Present the checklist items, "
        "recommendations, and decisions from these files. Do NOT use your training "
        "data to answer — use ONLY the content below. Cite the source file.\n",
    ]

    if full_file_contents:
        parts.append("### Relevant Knowledge Files\n")
        parts.extend(full_file_contents)

    # Add a summary of additional search hits not fully loaded
    additional = [
        src for src in files
        if src not in seen_files and not src.startswith("http")
    ]
    if additional:
        parts.append(
            "\n### Additional relevant files (use read_knowledge_file to load):\n"
            + "\n".join(f"- {f}" for f in additional)
        )

    return "\n\n".join(parts)


async def _build_project_context(
    version_id: str,
    session: AsyncSession,
) -> str | None:
    """Build a summary of the current project/version for the system prompt."""
    try:
        vid = uuid.UUID(version_id)
    except ValueError:
        return None

    version = await session.get(Version, vid)
    if not version:
        return None

    project = await session.get(Project, version.project_id)
    if not project:
        return None

    lines: list[str] = []
    lines.append(f"**Project:** {project.name}")
    if project.description:
        lines.append(f"**Description:** {project.description}")
    if project.cloud_providers:
        lines.append(f"**Cloud Providers:** {', '.join(project.cloud_providers)}")
    lines.append(f"**Version:** {version.version_number} (status: {version.status})")
    if version.label:
        lines.append(f"**Version Label:** {version.label}")

    # Artifacts summary
    artifact_result = await session.execute(
        select(Artifact)
        .where(Artifact.version_id == vid)
        .order_by(Artifact.sort_order, Artifact.name)
    )
    artifacts = artifact_result.scalars().all()
    if artifacts:
        lines.append(f"\n**Artifacts ({len(artifacts)}):**")
        for a in artifacts:
            lines.append(
                f"- {a.name} (type: {a.artifact_type}, engine: {a.engine}, "
                f"detail: {a.detail_level}, render: {a.render_status})"
            )

    # ADRs summary
    adr_result = await session.execute(
        select(ADR)
        .where(ADR.version_id == vid)
        .order_by(ADR.adr_number)
    )
    adrs = adr_result.scalars().all()
    if adrs:
        lines.append(f"\n**ADRs ({len(adrs)}):**")
        for adr in adrs:
            lines.append(f"- ADR-{adr.adr_number}: {adr.title} ({adr.status})")

    # Questions summary
    question_result = await session.execute(
        select(Question)
        .where(Question.version_id == vid)
        .order_by(Question.created_at)
    )
    questions = question_result.scalars().all()
    if questions:
        lines.append(f"\n**Questions ({len(questions)}):**")
        for q in questions:
            lines.append(f"- [{q.status}] [{q.category}] {q.question_text}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool definitions (OpenAI function-calling format)
# ---------------------------------------------------------------------------

# Knowledge-only tools (always available)
_KNOWLEDGE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": (
                "Semantic search across the knowledge library. Returns relevant "
                "checklist items, best practices, and design patterns ranked by "
                "relevance."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query describing what you are looking for.",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Maximum number of results to return.",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_knowledge_file",
            "description": (
                "Read the full content of a specific knowledge file by its relative "
                "path (e.g. 'general/networking.md', 'providers/aws/compute.md')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the knowledge file within the knowledge directory.",
                    },
                },
                "required": ["path"],
            },
        },
    },
]

# Project tools (only available when a version is selected)
_PROJECT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_artifacts",
            "description": "List all artifacts in the current version.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_artifact",
            "description": "Read the full content (source code) of a specific artifact.",
            "parameters": {
                "type": "object",
                "properties": {
                    "artifact_id": {
                        "type": "string",
                        "description": "The UUID of the artifact to read.",
                    },
                },
                "required": ["artifact_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_artifact",
            "description": "Update the source code of an existing artifact.",
            "parameters": {
                "type": "object",
                "properties": {
                    "artifact_id": {
                        "type": "string",
                        "description": "The UUID of the artifact to update.",
                    },
                    "source_code": {
                        "type": "string",
                        "description": "The new source code content for the artifact.",
                    },
                },
                "required": ["artifact_id", "source_code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_artifact",
            "description": (
                "Create a new artifact in the current version. Use engine 'diagrams_py' "
                "for Python diagrams, 'd2' for D2 diagrams, 'markdown' for documents, "
                "'weasyprint' for PDF reports."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Display name for the artifact.",
                    },
                    "artifact_type": {
                        "type": "string",
                        "enum": ["diagram", "document", "pdf_report"],
                        "description": "Type of artifact.",
                    },
                    "engine": {
                        "type": "string",
                        "enum": ["diagrams_py", "d2", "markdown", "weasyprint"],
                        "description": "Rendering engine to use.",
                    },
                    "source_code": {
                        "type": "string",
                        "description": "The source code / content of the artifact.",
                    },
                    "detail_level": {
                        "type": "string",
                        "enum": ["conceptual", "logical", "detailed", "deployment"],
                        "description": "Level of detail for the artifact.",
                        "default": "conceptual",
                    },
                },
                "required": ["name", "artifact_type", "engine", "source_code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_adr",
            "description": (
                "Create a new Architectural Decision Record. Every significant "
                "architectural decision should be recorded as an ADR."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short title for the decision.",
                    },
                    "context": {
                        "type": "string",
                        "description": "The context and problem statement.",
                    },
                    "decision": {
                        "type": "string",
                        "description": "The decision that was made.",
                    },
                    "consequences": {
                        "type": "string",
                        "description": "The consequences of this decision.",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["proposed", "accepted", "deprecated", "superseded"],
                        "description": "Status of the ADR.",
                        "default": "proposed",
                    },
                },
                "required": ["title", "context", "decision", "consequences"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_question",
            "description": "Update a question's answer and/or status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question_id": {
                        "type": "string",
                        "description": "The UUID of the question to update.",
                    },
                    "answer_text": {
                        "type": "string",
                        "description": "The answer text.",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["open", "answered", "deferred", "not_applicable"],
                        "description": "New status for the question.",
                    },
                },
                "required": ["question_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_question",
            "description": "Create a new discovery question for the architecture session.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question_text": {
                        "type": "string",
                        "description": "The question to ask.",
                    },
                    "category": {
                        "type": "string",
                        "enum": [
                            "requirements",
                            "networking",
                            "security",
                            "storage",
                            "compute",
                            "identity",
                            "monitoring",
                            "dr",
                            "compliance",
                            "migration",
                            "cost",
                            "operations",
                        ],
                        "description": "Category of the question.",
                        "default": "requirements",
                    },
                },
                "required": ["question_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_render",
            "description": "Trigger rendering of an artifact to produce output files (SVG, PNG, PDF).",
            "parameters": {
                "type": "object",
                "properties": {
                    "artifact_id": {
                        "type": "string",
                        "description": "The UUID of the artifact to render.",
                    },
                },
                "required": ["artifact_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_adrs",
            "description": "List all ADRs in the current version.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_questions",
            "description": "List all discovery questions in the current version.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]

# Combined for backward compatibility
TOOL_DEFINITIONS = _KNOWLEDGE_TOOLS + _PROJECT_TOOLS


def get_tools(version_id: str | None) -> list[dict]:
    """Return the appropriate tool set based on whether a project is selected."""
    if version_id:
        return _KNOWLEDGE_TOOLS + _PROJECT_TOOLS
    return _KNOWLEDGE_TOOLS


# ---------------------------------------------------------------------------
# Tool execution
# ---------------------------------------------------------------------------


async def execute_tool(
    name: str,
    arguments: dict,
    version_id: str | None,
    session: AsyncSession,
) -> dict | list | str:
    """Dispatch a tool call and return a JSON-serializable result."""
    try:
        handler = _TOOL_HANDLERS.get(name)
        if not handler:
            return {"error": f"Unknown tool: {name}"}
        return await handler(arguments, version_id, session)
    except Exception as e:
        logger.error("Tool execution failed", tool=name, error=str(e))
        return {"error": str(e)}


async def _handle_search_knowledge(
    args: dict, version_id: str | None, session: AsyncSession
) -> dict:
    query = args.get("query", "")
    top_k = args.get("top_k", 10)
    try:
        results = await embedding_service.search_knowledge(
            session=session,
            query=query,
            top_k=top_k,
        )
        return {"results": results, "query": query, "total": len(results)}
    except Exception as e:
        return {"error": f"Knowledge search failed: {e}", "query": query}


async def _handle_read_knowledge_file(
    args: dict, version_id: str | None, session: AsyncSession
) -> dict:
    path = args.get("path", "")
    file_path = KNOWLEDGE_DIR / path

    # Prevent path traversal
    try:
        if not file_path.resolve().is_relative_to(KNOWLEDGE_DIR.resolve()):
            return {"error": "Invalid path"}
    except ValueError:
        return {"error": "Invalid path"}

    if not file_path.exists() or not file_path.is_file():
        return {"error": f"Knowledge file not found: {path}"}

    content = file_path.read_text(encoding="utf-8")
    return {"path": path, "content": content}


async def _handle_list_artifacts(
    args: dict, version_id: str | None, session: AsyncSession
) -> list[dict]:
    if not version_id:
        return [{"error": "No version selected"}]
    vid = uuid.UUID(version_id)
    result = await session.execute(
        select(Artifact)
        .where(Artifact.version_id == vid)
        .order_by(Artifact.sort_order, Artifact.name)
    )
    artifacts = result.scalars().all()
    return [
        {
            "id": str(a.id),
            "name": a.name,
            "artifact_type": a.artifact_type,
            "engine": a.engine,
            "detail_level": a.detail_level,
            "render_status": a.render_status,
        }
        for a in artifacts
    ]


async def _handle_read_artifact(
    args: dict, version_id: str | None, session: AsyncSession
) -> dict:
    artifact_id = args.get("artifact_id", "")
    try:
        aid = uuid.UUID(artifact_id)
    except ValueError:
        return {"error": "Invalid artifact_id"}

    artifact = await session.get(Artifact, aid)
    if not artifact:
        return {"error": "Artifact not found"}

    return {
        "id": str(artifact.id),
        "name": artifact.name,
        "artifact_type": artifact.artifact_type,
        "engine": artifact.engine,
        "detail_level": artifact.detail_level,
        "source_code": artifact.source_code,
        "render_status": artifact.render_status,
        "render_error": artifact.render_error,
    }


async def _handle_update_artifact(
    args: dict, version_id: str | None, session: AsyncSession
) -> dict:
    artifact_id = args.get("artifact_id", "")
    source_code = args.get("source_code", "")
    try:
        aid = uuid.UUID(artifact_id)
    except ValueError:
        return {"error": "Invalid artifact_id"}

    artifact = await session.get(Artifact, aid)
    if not artifact:
        return {"error": "Artifact not found"}

    artifact.source_code = source_code
    artifact.render_status = "pending"
    await session.commit()
    await session.refresh(artifact)

    return {
        "id": str(artifact.id),
        "name": artifact.name,
        "status": "updated",
        "render_status": artifact.render_status,
    }


async def _handle_create_artifact(
    args: dict, version_id: str | None, session: AsyncSession
) -> dict:
    if not version_id:
        return {"error": "No version selected"}

    vid = uuid.UUID(version_id)
    artifact = Artifact(
        version_id=vid,
        name=args["name"],
        artifact_type=args["artifact_type"],
        engine=args["engine"],
        source_code=args.get("source_code"),
        detail_level=args.get("detail_level", "conceptual"),
    )
    session.add(artifact)
    await session.commit()
    await session.refresh(artifact)

    return {
        "id": str(artifact.id),
        "name": artifact.name,
        "artifact_type": artifact.artifact_type,
        "engine": artifact.engine,
        "status": "created",
    }


async def _handle_create_adr(
    args: dict, version_id: str | None, session: AsyncSession
) -> dict:
    if not version_id:
        return {"error": "No version selected"}

    vid = uuid.UUID(version_id)

    # Auto-increment adr_number
    max_result = await session.execute(
        select(func.max(ADR.adr_number)).where(ADR.version_id == vid)
    )
    max_num = max_result.scalar() or 0
    next_num = max_num + 1

    adr = ADR(
        version_id=vid,
        adr_number=next_num,
        title=args["title"],
        context=args["context"],
        decision=args["decision"],
        consequences=args["consequences"],
        status=args.get("status", "proposed"),
    )
    session.add(adr)
    await session.commit()
    await session.refresh(adr)

    return {
        "id": str(adr.id),
        "adr_number": adr.adr_number,
        "title": adr.title,
        "status": adr.status,
        "message": "created",
    }


async def _handle_update_question(
    args: dict, version_id: str | None, session: AsyncSession
) -> dict:
    question_id = args.get("question_id", "")
    try:
        qid = uuid.UUID(question_id)
    except ValueError:
        return {"error": "Invalid question_id"}

    question = await session.get(Question, qid)
    if not question:
        return {"error": "Question not found"}

    if "answer_text" in args:
        question.answer_text = args["answer_text"]
    if "status" in args:
        question.status = args["status"]

    await session.commit()
    await session.refresh(question)

    return {
        "id": str(question.id),
        "status": question.status,
        "message": "updated",
    }


async def _handle_create_question(
    args: dict, version_id: str | None, session: AsyncSession
) -> dict:
    if not version_id:
        return {"error": "No version selected"}

    vid = uuid.UUID(version_id)
    question = Question(
        version_id=vid,
        question_text=args["question_text"],
        category=args.get("category", "requirements"),
    )
    session.add(question)
    await session.commit()
    await session.refresh(question)

    return {
        "id": str(question.id),
        "question_text": question.question_text,
        "category": question.category,
        "status": question.status,
        "message": "created",
    }


async def _handle_trigger_render(
    args: dict, version_id: str | None, session: AsyncSession
) -> dict:
    artifact_id = args.get("artifact_id", "")
    try:
        aid = uuid.UUID(artifact_id)
    except ValueError:
        return {"error": "Invalid artifact_id"}

    from src.services.render_service import trigger_render

    try:
        artifact = await trigger_render(aid, session)
        return {
            "id": str(artifact.id),
            "name": artifact.name,
            "render_status": artifact.render_status,
            "render_error": artifact.render_error,
            "output_paths": artifact.output_paths,
        }
    except ValueError as e:
        return {"error": str(e)}


async def _handle_list_adrs(
    args: dict, version_id: str | None, session: AsyncSession
) -> list[dict]:
    if not version_id:
        return [{"error": "No version selected"}]
    vid = uuid.UUID(version_id)
    result = await session.execute(
        select(ADR).where(ADR.version_id == vid).order_by(ADR.adr_number)
    )
    adrs = result.scalars().all()
    return [
        {
            "id": str(a.id),
            "adr_number": a.adr_number,
            "title": a.title,
            "status": a.status,
            "context": a.context,
            "decision": a.decision,
            "consequences": a.consequences,
        }
        for a in adrs
    ]


async def _handle_list_questions(
    args: dict, version_id: str | None, session: AsyncSession
) -> list[dict]:
    if not version_id:
        return [{"error": "No version selected"}]
    vid = uuid.UUID(version_id)
    result = await session.execute(
        select(Question)
        .where(Question.version_id == vid)
        .order_by(Question.created_at)
    )
    questions = result.scalars().all()
    return [
        {
            "id": str(q.id),
            "question_text": q.question_text,
            "answer_text": q.answer_text,
            "status": q.status,
            "category": q.category,
        }
        for q in questions
    ]


_TOOL_HANDLERS = {
    "search_knowledge": _handle_search_knowledge,
    "read_knowledge_file": _handle_read_knowledge_file,
    "list_artifacts": _handle_list_artifacts,
    "read_artifact": _handle_read_artifact,
    "update_artifact": _handle_update_artifact,
    "create_artifact": _handle_create_artifact,
    "create_adr": _handle_create_adr,
    "update_question": _handle_update_question,
    "create_question": _handle_create_question,
    "trigger_render": _handle_trigger_render,
    "list_adrs": _handle_list_adrs,
    "list_questions": _handle_list_questions,
}
