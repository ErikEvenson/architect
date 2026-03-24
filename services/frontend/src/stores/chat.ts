import { create } from "zustand";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "tool";
  content: string;
  toolName?: string;
  toolArgs?: string;
  toolResult?: string;
  timestamp: number;
}

export interface ProviderConfig {
  type: "local" | "anthropic";
  base_url: string;
  model_name: string;
  api_key?: string;
}

interface ChatState {
  messages: ChatMessage[];
  isStreaming: boolean;
  providerConfig: ProviderConfig | null;
  versionId: string | null;
  showProviderDialog: boolean;
  addMessage: (msg: Omit<ChatMessage, "id" | "timestamp">) => void;
  appendToLastMessage: (delta: string) => void;
  setStreaming: (streaming: boolean) => void;
  setProviderConfig: (config: ProviderConfig) => void;
  setVersionId: (id: string | null) => void;
  clearMessages: () => void;
  toggleProviderDialog: () => void;
}

const STORAGE_KEY = "architect-chat-provider";

function loadProviderConfig(): ProviderConfig | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return JSON.parse(stored);
  } catch {
    // ignore parse errors
  }
  return null;
}

function saveProviderConfig(config: ProviderConfig): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isStreaming: false,
  providerConfig: loadProviderConfig(),
  versionId: null,
  showProviderDialog: false,

  addMessage: (msg) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: crypto.randomUUID(),
          role: msg.role,
          content: msg.content,
          toolName: msg.toolName,
          toolArgs: msg.toolArgs,
          toolResult: msg.toolResult,
          timestamp: Date.now(),
        },
      ],
    })),

  appendToLastMessage: (delta) =>
    set((state) => {
      const msgs = [...state.messages];
      if (msgs.length === 0) return state;
      const last = msgs[msgs.length - 1]!;
      msgs[msgs.length - 1] = { ...last, content: last.content + delta } as ChatMessage;
      return { messages: msgs };
    }),

  setStreaming: (streaming) => set({ isStreaming: streaming }),

  setProviderConfig: (config) => {
    saveProviderConfig(config);
    set({ providerConfig: config });
  },

  setVersionId: (id) => set({ versionId: id }),

  clearMessages: () => set({ messages: [] }),

  toggleProviderDialog: () =>
    set((state) => ({ showProviderDialog: !state.showProviderDialog })),
}));
