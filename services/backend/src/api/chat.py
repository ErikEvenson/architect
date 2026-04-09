"""Chat API endpoint with SSE streaming."""

import json
from typing import Optional

import structlog
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.services import chat_service

logger = structlog.get_logger()
router = APIRouter(prefix="/chat", tags=["chat"])


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ChatMessage(BaseModel):
    role: str  # system, user, assistant, tool
    content: Optional[str] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None
    tool_calls: Optional[list[dict]] = None


class ProviderConfig(BaseModel):
    type: str = "local"  # local, anthropic
    base_url: str = "http://localhost:1234/v1"
    model_name: str = "local-model"
    api_key: Optional[str] = None


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    provider: ProviderConfig
    version_id: Optional[str] = None


# ---------------------------------------------------------------------------
# SSE streaming endpoint
# ---------------------------------------------------------------------------


@router.post("")
async def chat(
    request: ChatRequest,
    session: AsyncSession = Depends(get_session),
):
    """Stream chat completions via SSE with tool-call loop."""
    system_prompt = await chat_service.build_system_prompt(
        request.version_id, session
    )

    # Pre-fetch RAG results for the user's latest message
    rag_context = await chat_service.prefetch_rag_context(
        request.messages, session
    )

    return StreamingResponse(
        _stream_chat(
            system_prompt=system_prompt,
            rag_context=rag_context,
            messages=request.messages,
            provider=request.provider,
            version_id=request.version_id,
            session=session,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def _sse(data: dict) -> str:
    """Format a dict as an SSE data line."""
    return f"data: {json.dumps(data)}\n\n"


async def _stream_chat(
    system_prompt: str,
    rag_context: str | None,
    messages: list[ChatMessage],
    provider: ProviderConfig,
    version_id: str | None,
    session: AsyncSession,
):
    """Generator that yields SSE events for the chat stream."""
    client = AsyncOpenAI(
        base_url=provider.base_url,
        api_key=provider.api_key or "not-needed",
    )

    # Build the messages list for the API call
    api_messages: list[dict] = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        m: dict = {"role": msg.role}
        if msg.content is not None:
            m["content"] = msg.content
        if msg.tool_call_id is not None:
            m["tool_call_id"] = msg.tool_call_id
        if msg.name is not None:
            m["name"] = msg.name
        if msg.tool_calls is not None:
            m["tool_calls"] = msg.tool_calls
        api_messages.append(m)

    # Inject RAG context as a system message right before the last user message
    # so the model sees it as immediately relevant context
    if rag_context:
        # Find the last user message index and insert RAG before it
        last_user_idx = None
        for i in range(len(api_messages) - 1, -1, -1):
            if api_messages[i].get("role") == "user":
                last_user_idx = i
                break
        if last_user_idx is not None:
            api_messages.insert(last_user_idx, {
                "role": "system",
                "content": rag_context,
            })
        else:
            api_messages.append({"role": "system", "content": rag_context})

    use_tools = True
    max_tool_rounds = 20  # Safety limit to prevent infinite tool loops

    for _round in range(max_tool_rounds):
        try:
            kwargs: dict = {
                "model": provider.model_name,
                "messages": api_messages,
                "stream": True,
                "max_tokens": 16384,
            }
            if use_tools:
                kwargs["tools"] = chat_service.get_tools(version_id)

            stream = await client.chat.completions.create(**kwargs)
        except Exception as e:
            error_msg = str(e)
            # If tools are not supported, retry without tools
            if use_tools and ("tool" in error_msg.lower() or "function" in error_msg.lower()):
                logger.warning("Tools not supported by model, falling back to no-tools mode")
                use_tools = False
                try:
                    stream = await client.chat.completions.create(
                        model=provider.model_name,
                        messages=api_messages,
                        stream=True,
                    )
                except Exception as e2:
                    yield _sse({"type": "error", "message": str(e2)})
                    yield _sse({"type": "done"})
                    return
            else:
                yield _sse({"type": "error", "message": error_msg})
                yield _sse({"type": "done"})
                return

        # Accumulate the streamed response
        collected_content = ""
        collected_tool_calls: dict[int, dict] = {}  # index -> {id, name, arguments}

        try:
            async for chunk in stream:
                if not chunk.choices:
                    continue

                choice = chunk.choices[0]
                delta = choice.delta

                # Stream text content
                if delta.content:
                    collected_content += delta.content
                    yield _sse({"type": "content", "delta": delta.content})

                # Accumulate tool calls (may come across multiple chunks)
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in collected_tool_calls:
                            collected_tool_calls[idx] = {
                                "id": "",
                                "name": "",
                                "arguments": "",
                            }
                        if tc.id:
                            collected_tool_calls[idx]["id"] = tc.id
                        if tc.function and tc.function.name:
                            collected_tool_calls[idx]["name"] = tc.function.name
                        if tc.function and tc.function.arguments:
                            collected_tool_calls[idx]["arguments"] += tc.function.arguments

        except Exception as e:
            yield _sse({"type": "error", "message": f"Stream error: {e}"})
            yield _sse({"type": "done"})
            return

        # If no tool calls, we are done
        if not collected_tool_calls:
            break

        # Process tool calls
        # Build the assistant message with tool_calls
        assistant_tool_calls = []
        for idx in sorted(collected_tool_calls.keys()):
            tc = collected_tool_calls[idx]
            assistant_tool_calls.append({
                "id": tc["id"],
                "type": "function",
                "function": {
                    "name": tc["name"],
                    "arguments": tc["arguments"],
                },
            })

        assistant_msg: dict = {"role": "assistant"}
        if collected_content:
            assistant_msg["content"] = collected_content
        if assistant_tool_calls:
            assistant_msg["tool_calls"] = assistant_tool_calls
        api_messages.append(assistant_msg)

        # Execute each tool call and append results
        for tc_msg in assistant_tool_calls:
            tool_name = tc_msg["function"]["name"]
            tool_args_str = tc_msg["function"]["arguments"]
            tool_call_id = tc_msg["id"]

            yield _sse({
                "type": "tool_call",
                "name": tool_name,
                "arguments": tool_args_str,
                "tool_call_id": tool_call_id,
            })

            # Parse arguments
            try:
                tool_args = json.loads(tool_args_str) if tool_args_str else {}
            except json.JSONDecodeError:
                tool_args = {}

            # Execute the tool
            try:
                result = await chat_service.execute_tool(
                    name=tool_name,
                    arguments=tool_args,
                    version_id=version_id,
                    session=session,
                )
            except Exception as e:
                result = {"error": str(e)}

            result_str = json.dumps(result, default=str)

            yield _sse({
                "type": "tool_result",
                "name": tool_name,
                "result": result_str,
                "tool_call_id": tool_call_id,
            })

            # Append tool result to messages for the next LLM call
            api_messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": result_str,
            })

        # Loop back to make another completion call with tool results
        continue

    yield _sse({"type": "done"})
