import React, { useState } from "react";
import {
  Plus,
  MessageSquare,
  Trash2,
  Edit3,
  Check,
  X,
  ChevronLeft,
  Settings,
  Cpu,
  Search,
  Zap,
  Clock,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";

const Sidebar = ({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
  onRenameConversation,
  isCollapsed,
  onToggleCollapse,
  onOpenSettings,
}) => {
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  const handleStartEdit = (conv) => {
    setEditingId(conv.id);
    setEditTitle(conv.title);
  };

  const handleSaveEdit = (id) => {
    if (editTitle.trim()) {
      onRenameConversation(id, editTitle.trim());
    }
    setEditingId(null);
    setEditTitle("");
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditTitle("");
  };

  const filteredConversations = conversations.filter((conv) =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  if (isCollapsed) {
    return (
      <div className="w-16 bg-slate-900 border-r border-slate-800 flex flex-col items-center py-4 gap-4">
        <button
          onClick={onToggleCollapse}
          className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-all"
          title="Expand sidebar"
        >
          <ChevronLeft size={20} className="rotate-180" />
        </button>
        <button
          onClick={onNewChat}
          className="p-3 bg-slate-700 text-white rounded-xl hover:bg-slate-600 transition-colors"
          title="New chat"
        >
          <Plus size={20} />
        </button>
        <div className="flex-1" />
        <button
          onClick={onOpenSettings}
          className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-all"
          title="Settings"
        >
          <Settings size={20} />
        </button>
      </div>
    );
  }

  return (
    <div className="w-72 bg-slate-900 border-r border-slate-800 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-slate-700 to-slate-900 rounded-lg flex items-center justify-center border border-slate-600">
              <Cpu size={18} className="text-white" />
            </div>
            <span className="font-semibold text-slate-100">Core</span>
          </div>
          <button
            onClick={onToggleCollapse}
            className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-all"
            title="Collapse sidebar"
          >
            <ChevronLeft size={18} />
          </button>
        </div>

        {/* New Chat Button */}
        <button
          onClick={onNewChat}
          className="w-full flex items-center gap-2 px-4 py-2.5 bg-slate-700 hover:bg-slate-600 text-white rounded-xl transition-colors font-medium"
        >
          <Plus size={18} />
          <span>New Chat</span>
        </button>
      </div>

      {/* Search */}
      <div className="px-4 py-3">
        <div className="relative">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
          />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-slate-600"
          />
        </div>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto px-2 py-2">
        {filteredConversations.length === 0 ? (
          <div className="text-center text-slate-500 py-8 px-4">
            <MessageSquare size={32} className="mx-auto mb-2 opacity-50" />
            <p className="text-sm">No conversations yet</p>
          </div>
        ) : (
          <div className="space-y-1">
            {filteredConversations.map((conv) => (
              <div
                key={conv.id}
                className={`group relative rounded-xl transition-all ${
                  activeConversationId === conv.id
                    ? "bg-slate-800 border border-slate-700"
                    : "hover:bg-slate-800/50 border border-transparent"
                }`}
              >
                {editingId === conv.id ? (
                  <div className="flex items-center gap-2 p-3">
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") handleSaveEdit(conv.id);
                        if (e.key === "Escape") handleCancelEdit();
                      }}
                      className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-2 py-1 text-sm text-slate-100 focus:outline-none focus:border-slate-600"
                      autoFocus
                    />
                    <button
                      onClick={() => handleSaveEdit(conv.id)}
                      className="p-1 text-green-500 hover:bg-slate-800 rounded"
                    >
                      <Check size={16} />
                    </button>
                    <button
                      onClick={handleCancelEdit}
                      className="p-1 text-red-500 hover:bg-slate-800 rounded"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => onSelectConversation(conv.id)}
                    className="w-full text-left p-3 pr-16"
                  >
                    <div className="flex items-start gap-2">
                      <MessageSquare
                        size={16}
                        className="text-slate-400 mt-0.5 flex-shrink-0"
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-slate-100 truncate font-medium">
                          {conv.title}
                        </p>
                        <p className="text-xs text-slate-500 mt-0.5">
                          {conv.updated_at &&
                            formatDistanceToNow(new Date(conv.updated_at), {
                              addSuffix: true,
                            })}
                        </p>
                      </div>
                    </div>
                  </button>
                )}

                {/* Action buttons */}
                {editingId !== conv.id && (
                  <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleStartEdit(conv);
                      }}
                      className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
                      title="Rename"
                    >
                      <Edit3 size={14} />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteConversation(conv.id);
                      }}
                      className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
                      title="Delete"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-slate-800">
        <button
          onClick={onOpenSettings}
          className="w-full flex items-center gap-2 px-3 py-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
        >
          <Settings size={18} />
          <span className="text-sm font-medium">Settings</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
