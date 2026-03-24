import { useState, useEffect } from "react";
import { useChatStore } from "../../stores/chat";
import type { ProviderConfig } from "../../stores/chat";

export function ProviderConfigDialog() {
  const { providerConfig, setProviderConfig, toggleProviderDialog } =
    useChatStore();

  const [type, setType] = useState<"local" | "anthropic">(
    providerConfig?.type || "local"
  );
  const [baseUrl, setBaseUrl] = useState(
    providerConfig?.base_url || "http://localhost:1234/v1"
  );
  const [modelName, setModelName] = useState(
    providerConfig?.model_name || "default"
  );
  const [apiKey, setApiKey] = useState(providerConfig?.api_key || "");

  useEffect(() => {
    if (providerConfig) {
      setType(providerConfig.type);
      setBaseUrl(providerConfig.base_url);
      setModelName(providerConfig.model_name);
      setApiKey(providerConfig.api_key || "");
    }
  }, [providerConfig]);

  const applyPreset = (preset: "lmstudio" | "ollama") => {
    if (preset === "lmstudio") {
      setType("local");
      setBaseUrl("http://localhost:1234/v1");
      setModelName("default");
    } else {
      setType("local");
      setBaseUrl("http://localhost:11434/v1");
      setModelName("default");
    }
  };

  const handleSave = () => {
    const config: ProviderConfig = {
      type,
      base_url: baseUrl,
      model_name: modelName,
    };
    if (type === "anthropic" && apiKey) {
      config.api_key = apiKey;
    }
    setProviderConfig(config);
    toggleProviderDialog();
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 max-w-md w-full mx-4">
        <h2 className="text-lg font-semibold text-gray-100 mb-4">
          LLM Provider Configuration
        </h2>

        {/* Presets */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => applyPreset("lmstudio")}
            className="px-3 py-1.5 text-xs font-medium rounded bg-gray-700 text-gray-300 hover:bg-gray-600 border border-gray-600"
          >
            LM Studio
          </button>
          <button
            onClick={() => applyPreset("ollama")}
            className="px-3 py-1.5 text-xs font-medium rounded bg-gray-700 text-gray-300 hover:bg-gray-600 border border-gray-600"
          >
            Ollama
          </button>
        </div>

        <div className="space-y-4">
          {/* Type */}
          <div>
            <label className="block text-sm text-gray-300 mb-1">Type</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value as "local" | "anthropic")}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-blue-500"
            >
              <option value="local">Local Model</option>
              <option value="anthropic">Anthropic Claude</option>
            </select>
          </div>

          {/* Base URL */}
          <div>
            <label className="block text-sm text-gray-300 mb-1">
              Base URL
            </label>
            <input
              type="text"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              placeholder="http://localhost:1234/v1"
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Model Name */}
          <div>
            <label className="block text-sm text-gray-300 mb-1">
              Model Name
            </label>
            <input
              type="text"
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
              placeholder="default"
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* API Key (Anthropic only) */}
          {type === "anthropic" && (
            <div>
              <label className="block text-sm text-gray-300 mb-1">
                API Key
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-ant-..."
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
              />
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-2 mt-6">
          <button
            onClick={toggleProviderDialog}
            className="px-4 py-2 text-sm font-medium rounded-lg text-gray-300 hover:text-gray-100 hover:bg-gray-700"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 text-sm font-medium rounded-lg bg-blue-600 text-white hover:bg-blue-700"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
