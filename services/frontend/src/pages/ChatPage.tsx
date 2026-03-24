import { useChatStore } from "../stores/chat";
import { ChatPanel } from "../components/Chat/ChatPanel";
import { ProviderConfigDialog } from "../components/Chat/ProviderConfigDialog";
import { VersionSelector } from "../components/Chat/VersionSelector";

export function ChatPage() {
  const { providerConfig, showProviderDialog, toggleProviderDialog } =
    useChatStore();

  return (
    <div className="h-full flex flex-col -m-6">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700 bg-gray-900 shrink-0">
        <VersionSelector />

        {providerConfig && (
          <span className="text-xs text-gray-500 bg-gray-800 px-2.5 py-1 rounded-full border border-gray-700">
            {providerConfig.model_name}
          </span>
        )}

        <button
          onClick={toggleProviderDialog}
          className="text-gray-400 hover:text-gray-200 p-1.5 rounded hover:bg-gray-800"
          title="Configure LLM provider"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a6.759 6.759 0 010 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 010-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.28z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
        </button>
      </div>

      {/* Body */}
      {providerConfig ? (
        <div className="flex-1 overflow-hidden">
          <ChatPanel />
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-gray-400 mb-4">
              No LLM provider configured. Set up a provider to start chatting.
            </p>
            <button
              onClick={toggleProviderDialog}
              className="px-4 py-2 text-sm font-medium rounded-lg bg-blue-600 text-white hover:bg-blue-700"
            >
              Configure Provider
            </button>
          </div>
        </div>
      )}

      {/* Dialog */}
      {showProviderDialog && <ProviderConfigDialog />}
    </div>
  );
}
