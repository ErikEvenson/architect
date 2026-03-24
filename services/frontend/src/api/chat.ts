import type { ProviderConfig } from "../stores/chat";

export interface ChatEvent {
  type: "content" | "tool_call" | "tool_result" | "error" | "done";
  delta?: string;
  name?: string;
  arguments?: string;
  result?: string;
  message?: string;
}

const API_BASE = "/api/v1";

export async function* streamChat(
  messages: { role: string; content: string }[],
  provider: ProviderConfig,
  versionId: string | null
): AsyncGenerator<ChatEvent> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages,
        provider,
        version_id: versionId,
      }),
    });
  } catch (err) {
    yield {
      type: "error",
      message: err instanceof Error ? err.message : "Network error",
    };
    return;
  }

  if (!response.ok) {
    let errorMsg = response.statusText;
    try {
      const body = await response.json();
      errorMsg = body.detail || errorMsg;
    } catch {
      // use statusText
    }
    yield { type: "error", message: errorMsg };
    return;
  }

  const reader = response.body?.getReader();
  if (!reader) {
    yield { type: "error", message: "No response body" };
    return;
  }

  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split("\n\n");
      // Keep the last incomplete part in the buffer
      buffer = parts.pop() || "";

      for (const part of parts) {
        const trimmed = part.trim();
        if (!trimmed) continue;

        // Extract data from SSE format
        const lines = trimmed.split("\n");
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const jsonStr = line.slice(6);

          try {
            const event: ChatEvent = JSON.parse(jsonStr);
            yield event;
            if (event.type === "done" || event.type === "error") return;
          } catch {
            // skip malformed JSON lines
          }
        }
      }
    }

    // Process any remaining buffer
    if (buffer.trim()) {
      const lines = buffer.trim().split("\n");
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        try {
          const event: ChatEvent = JSON.parse(line.slice(6));
          yield event;
        } catch {
          // skip
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
