import { useState, useRef, useEffect, useCallback } from "react";
import { useChatStore } from "../../stores/chat";
import { streamChat } from "../../api/chat";
import type { ChatMessage } from "../../stores/chat";

function renderMarkdown(md: string): string {
  let html = md
    // Code blocks (must come before inline transformations)
    .replace(/```[\w]*\n([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    // Headers
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Checklist items
    .replace(/^- \[ \] (.+)$/gm, '<li>&#9744; $1</li>')
    .replace(/^- \[x\] (.+)$/gm, '<li>&#9745; $1</li>')
    // Regular list items
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    // Numbered list items
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // Table rows
    .replace(/^\|(.+)\|$/gm, (match) => {
      const cells = match.split('|').filter(Boolean).map((c) => c.trim());
      if (cells.every((c) => /^-+$/.test(c))) return '';
      return '<tr>' + cells.map((c) => `<td>${c}</td>`).join('') + '</tr>';
    })
    // Paragraphs (lines not already tagged)
    .replace(/^(?!<[hluotp]|<tr|$)(.+)$/gm, '<p>$1</p>');

  // Wrap consecutive <li> in <ul>
  html = html.replace(/(<li>[\s\S]*?<\/li>(\n|$))+/g, (match) => `<ul>${match}</ul>`);
  // Wrap consecutive <tr> in <table>
  html = html.replace(/(<tr>[\s\S]*?<\/tr>(\n|$))+/g, (match) => `<table>${match}</table>`);

  return html;
}

function ToolMessage({ message }: { message: ChatMessage }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="px-4 py-1">
      <button
        onClick={() => setExpanded(!expanded)}
        className="text-xs text-gray-500 hover:text-gray-400 flex items-center gap-1"
      >
        <span className="text-gray-600">{expanded ? "▼" : "▶"}</span>
        <span>Used tool: {message.toolName || "unknown"}</span>
      </button>
      {expanded && (
        <div className="mt-1 ml-4 text-xs text-gray-500 space-y-1">
          {message.toolArgs && (
            <div>
              <span className="text-gray-600">Args: </span>
              <pre className="inline whitespace-pre-wrap break-all">{message.toolArgs}</pre>
            </div>
          )}
          {message.toolResult && (
            <div>
              <span className="text-gray-600">Result: </span>
              <pre className="inline whitespace-pre-wrap break-all max-h-40 overflow-y-auto block">
                {message.toolResult}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function ChatPanel() {
  const {
    messages,
    isStreaming,
    providerConfig,
    versionId,
    addMessage,
    appendToLastMessage,
    setStreaming,
  } = useChatStore();

  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const _abortRef = useRef<AbortController | null>(null);
  void _abortRef; // reserved for future stop-streaming support

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 150) + "px";
  }, [input]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || isStreaming || !providerConfig) return;

    setInput("");
    addMessage({ role: "user", content: trimmed });
    setStreaming(true);

    // Build message history for the API
    const apiMessages = [
      ...useChatStore.getState().messages.filter((m) => m.role !== "tool").map((m) => ({
        role: m.role,
        content: m.content,
      })),
    ];

    // Add empty assistant message to accumulate into
    addMessage({ role: "assistant", content: "" });

    try {
      for await (const event of streamChat(apiMessages, providerConfig, versionId)) {
        switch (event.type) {
          case "content":
            if (event.delta) {
              appendToLastMessage(event.delta);
            }
            break;
          case "tool_call":
            addMessage({
              role: "tool",
              content: "",
              toolName: event.name,
              toolArgs: event.arguments,
            });
            break;
          case "tool_result":
            // Update the last tool message with the result
            useChatStore.setState((state) => {
              const msgs = [...state.messages];
              for (let i = msgs.length - 1; i >= 0; i--) {
                const m = msgs[i]!;
                if (m.role === "tool") {
                  msgs[i] = { ...m, toolResult: event.result } as ChatMessage;
                  break;
                }
              }
              return { messages: msgs };
            });
            // Add a new assistant message for continuing content
            addMessage({ role: "assistant", content: "" });
            break;
          case "error":
            appendToLastMessage(
              `\n\n**Error:** ${event.message || "Unknown error"}`
            );
            break;
          case "done":
            break;
        }
      }
    } catch (err) {
      appendToLastMessage(
        `\n\n**Error:** ${err instanceof Error ? err.message : "Stream failed"}`
      );
    } finally {
      setStreaming(false);
      // Clean up empty trailing assistant messages
      useChatStore.setState((state) => ({
        messages: state.messages.filter(
          (m, i) =>
            !(m.role === "assistant" && m.content === "" && i === state.messages.length - 1)
        ),
      }));
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p className="text-lg mb-2">Start a conversation</p>
            <p className="text-sm">
              Ask questions about architecture, design patterns, or get help
              with your project.
            </p>
          </div>
        )}

        {messages.map((msg) => {
          if (msg.role === "tool") {
            return <ToolMessage key={msg.id} message={msg} />;
          }

          if (msg.role === "user") {
            return (
              <div key={msg.id} className="flex justify-end">
                <div className="max-w-[75%] px-4 py-2.5 rounded-2xl rounded-br-sm bg-blue-600 text-white text-sm whitespace-pre-wrap">
                  {msg.content}
                </div>
              </div>
            );
          }

          // assistant
          return (
            <div key={msg.id} className="flex justify-start">
              <div
                className="max-w-[85%] px-4 py-3 rounded-2xl rounded-bl-sm bg-gray-800 border border-gray-700 text-sm
                  prose prose-invert prose-sm max-w-none
                  [&_h1]:text-base [&_h1]:font-bold [&_h1]:text-gray-100 [&_h1]:mt-4 [&_h1]:mb-2
                  [&_h2]:text-sm [&_h2]:font-semibold [&_h2]:text-gray-200 [&_h2]:mt-3 [&_h2]:mb-1
                  [&_h3]:text-sm [&_h3]:font-semibold [&_h3]:text-gray-300 [&_h3]:mt-2 [&_h3]:mb-1
                  [&_p]:text-gray-300 [&_p]:mb-1.5 [&_p]:leading-relaxed
                  [&_li]:text-gray-300
                  [&_ul]:mb-2 [&_ol]:mb-2
                  [&_code]:bg-gray-700 [&_code]:px-1 [&_code]:rounded [&_code]:text-gray-200 [&_code]:text-xs
                  [&_pre]:bg-gray-900 [&_pre]:p-3 [&_pre]:rounded [&_pre]:overflow-x-auto [&_pre]:my-2
                  [&_strong]:text-gray-100
                  [&_table]:w-full [&_table]:mb-2
                  [&_th]:bg-gray-700 [&_th]:px-2 [&_th]:py-1 [&_th]:text-left [&_th]:text-gray-200 [&_th]:text-xs
                  [&_td]:border-t [&_td]:border-gray-700 [&_td]:px-2 [&_td]:py-1 [&_td]:text-gray-300 [&_td]:text-xs
                "
                dangerouslySetInnerHTML={{
                  __html: renderMarkdown(msg.content),
                }}
              />
            </div>
          );
        })}

        {isStreaming && (
          <div className="flex justify-start px-4">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              <div
                className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"
                style={{ animationDelay: "0.2s" }}
              />
              <div
                className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"
                style={{ animationDelay: "0.4s" }}
              />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-700 p-3">
        <div className="flex items-end gap-2">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isStreaming || !providerConfig}
            placeholder={
              providerConfig
                ? "Type a message... (Enter to send, Shift+Enter for newline)"
                : "Configure a provider to start chatting"
            }
            rows={1}
            className="flex-1 resize-none bg-gray-800 border border-gray-600 rounded-lg px-4 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            onClick={handleSend}
            disabled={isStreaming || !input.trim() || !providerConfig}
            className="px-4 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
