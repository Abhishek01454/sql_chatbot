import React, { useState } from "react";
import {
  X,
  Sliders,
  Thermometer,
  MessageSquare,
  Zap,
  Save,
  Cpu,
  RotateCcw,
} from "lucide-react";

const SettingsModal = ({ isOpen, onClose, settings, onSaveSettings }) => {
  const [localSettings, setLocalSettings] = useState(settings);

  if (!isOpen) return null;

  const handleSave = () => {
    onSaveSettings(localSettings);
    onClose();
  };

  const handleReset = () => {
    const defaults = {
      temperature: 0.7,
      maxTokens: 4096,
      systemPrompt:
        "You are Core AI, an advanced artificial intelligence assistant. You are intelligent, precise, and provide insightful responses. You excel at coding, analysis, problem-solving, and creative tasks.",
      streaming: true,
    };
    setLocalSettings(defaults);
  };

  const systemPromptPresets = [
    {
      name: "Default Assistant",
      prompt:
        "You are Core, a helpful AI assistant. You are knowledgeable, precise, and provide clear, well-structured responses. You can help with coding, writing, analysis, and problem-solving.",
      icon: Cpu,
      color: "from-slate-700 to-slate-900",
    },
    {
      name: "Code Expert",
      prompt:
        "You are an expert software engineer and coding assistant. You write clean, efficient, well-documented code. You explain your solutions clearly and follow best practices. When asked about code, provide complete, working solutions with explanations.",
      icon: Zap,
      color: "from-slate-600 to-slate-800",
    },
    {
      name: "Data Analyst",
      prompt:
        "You are a data analysis expert. You help users understand data, create visualizations, write SQL queries, and perform statistical analysis. You explain complex concepts in simple terms and provide actionable insights.",
      icon: Sliders,
      color: "from-slate-600 to-slate-800",
    },
    {
      name: "Creative Writer",
      prompt:
        "You are a creative writing assistant with expertise in storytelling, poetry, and various writing styles. You help users craft compelling narratives, develop characters, and improve their writing. Be imaginative and inspiring.",
      icon: MessageSquare,
      color: "from-slate-600 to-slate-800",
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-slate-900 rounded-2xl border border-slate-700 shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-slate-700 to-slate-900 rounded-xl flex items-center justify-center border border-slate-600">
              <Sliders size={20} className="text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-100">Settings</h2>
              <p className="text-sm text-slate-500">
                Customize your chat experience
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {/* Temperature */}
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-3">
              <Thermometer size={18} className="text-slate-400" />
              <label className="text-sm font-medium text-slate-100">
                Temperature
              </label>
              <span className="ml-auto text-sm text-slate-400 font-mono">
                {localSettings.temperature.toFixed(1)}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={localSettings.temperature}
              onChange={(e) =>
                setLocalSettings({
                  ...localSettings,
                  temperature: parseFloat(e.target.value),
                })
              }
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-slate-500"
            />
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>Precise</span>
              <span>Creative</span>
            </div>
          </div>

          {/* Max Tokens */}
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-3">
              <Zap size={18} className="text-slate-400" />
              <label className="text-sm font-medium text-slate-100">
                Max Response Length
              </label>
              <span className="ml-auto text-sm text-slate-400 font-mono">
                {localSettings.maxTokens} tokens
              </span>
            </div>
            <input
              type="range"
              min="256"
              max="4096"
              step="256"
              value={localSettings.maxTokens}
              onChange={(e) =>
                setLocalSettings({
                  ...localSettings,
                  maxTokens: parseInt(e.target.value),
                })
              }
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-slate-500"
            />
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>Short</span>
              <span>Long</span>
            </div>
          </div>

          {/* System Prompt */}
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <MessageSquare size={18} className="text-slate-400" />
              <label className="text-sm font-medium text-slate-100">
                System Prompt
              </label>
            </div>

            {/* Presets */}
            <div className="flex flex-wrap gap-2 mb-3">
              {systemPromptPresets.map((preset) => (
                <button
                  key={preset.name}
                  onClick={() =>
                    setLocalSettings({
                      ...localSettings,
                      systemPrompt: preset.prompt,
                    })
                  }
                  className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${
                    localSettings.systemPrompt === preset.prompt
                      ? "bg-slate-700 border-slate-600 text-slate-200"
                      : "bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600"
                  }`}
                >
                  {preset.name}
                </button>
              ))}
            </div>

            <textarea
              value={localSettings.systemPrompt}
              onChange={(e) =>
                setLocalSettings({
                  ...localSettings,
                  systemPrompt: e.target.value,
                })
              }
              rows={4}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-slate-600 resize-none"
              placeholder="Enter a custom system prompt..."
            />
          </div>

          {/* Streaming toggle */}
          <div className="flex items-center justify-between p-4 bg-slate-800 rounded-xl border border-slate-700">
            <div>
              <p className="text-sm font-medium text-slate-100">
                Streaming Responses
              </p>
              <p className="text-xs text-slate-500 mt-0.5">
                See responses as they're generated
              </p>
            </div>
            <button
              onClick={() =>
                setLocalSettings({
                  ...localSettings,
                  streaming: !localSettings.streaming,
                })
              }
              className={`relative w-12 h-6 rounded-full transition-colors ${
                localSettings.streaming ? "bg-slate-700" : "bg-slate-600"
              }`}
            >
              <div
                className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
                  localSettings.streaming ? "translate-x-7" : "translate-x-1"
                }`}
              />
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-800">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-slate-400 hover:text-slate-200 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white text-sm font-medium rounded-lg transition-colors shadow-lg"
          >
            <Save size={16} />
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;
