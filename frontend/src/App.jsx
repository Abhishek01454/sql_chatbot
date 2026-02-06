import React, { useState, useEffect, useRef, useCallback } from "react";
import { api } from "./api";
import Sidebar from "./components/Sidebar.jsx";
import ChatMessage from "./components/ChatMessage.jsx";
import ChatInput from "./components/ChatInput.jsx";
import WelcomeScreen from "./components/WelcomeScreen.jsx";
import SchemaInput from "./components/SchemaInput.jsx";
import { Menu, Database, Copy, Check, Download, RotateCcw, ChevronDown, ChevronUp } from "lucide-react";

// Default schema
const DEFAULT_SCHEMA = {
  name: "my_database",
  tables: []
};

function App() {
  // State
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [schema, setSchema] = useState(() => {
    const saved = localStorage.getItem("sql-agent-schema");
    return saved ? JSON.parse(saved) : DEFAULT_SCHEMA;
  });
  const [schemaCollapsed, setSchemaCollapsed] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState(null);

  const messagesEndRef = useRef(null);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Save schema to localStorage
  useEffect(() => {
    localStorage.setItem("sql-agent-schema", JSON.stringify(schema));
  }, [schema]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadConversations = async () => {
    try {
      const convs = await api.getConversations();
      setConversations(convs);
    } catch (err) {
      console.error("Failed to load conversations:", err);
    }
  };

  const loadConversation = async (conversationId) => {
    try {
      const conv = await api.getConversation(conversationId);
      setMessages(conv.messages || []);
      setActiveConversationId(conversationId);
      setError(null);
    } catch (err) {
      console.error("Failed to load conversation:", err);
      setError("Failed to load conversation");
    }
  };

  const handleNewChat = () => {
    setActiveConversationId(null);
    setMessages([]);
    setError(null);
  };

  const handleSelectConversation = (conversationId) => {
    if (conversationId !== activeConversationId) {
      loadConversation(conversationId);
    }
  };

  const handleDeleteConversation = async (conversationId) => {
    try {
      await api.deleteConversation(conversationId);
      setConversations((prev) => prev.filter((c) => c.id !== conversationId));
      if (activeConversationId === conversationId) {
        handleNewChat();
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
    }
  };

  const handleRenameConversation = async (conversationId, newTitle) => {
    try {
      await api.updateConversation(conversationId, newTitle);
      setConversations((prev) =>
        prev.map((c) =>
          c.id === conversationId ? { ...c, title: newTitle } : c,
        ),
      );
    } catch (err) {
      console.error("Failed to rename conversation:", err);
    }
  };

  const handleSendMessage = useCallback(
    async (question) => {
      // Validate schema
      if (schema.tables.length === 0) {
        setError("Please define at least one table in your database schema before asking questions.");
        return;
      }

      setIsLoading(true);
      setError(null);

      // Add user message immediately
      const userMessage = {
        role: "user",
        content: question,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      try {
        // Call SQL generation API
        const response = await api.generateSQL(question, schema);

        // Create assistant message with SQL result
        let assistantContent = "";

        if (response.is_valid) {
          assistantContent = `\`\`\`sql\n${response.sql}\n\`\`\``;
          if (response.explanation) {
            assistantContent += `\n\n${response.explanation}`;
          }
        } else {
          assistantContent = "⚠️ **Unable to generate valid SQL**\n\n";
          if (response.sql) {
            assistantContent += `Generated query:\n\`\`\`sql\n${response.sql}\n\`\`\`\n\n`;
          }
          assistantContent += "**Validation Errors:**\n";
          response.validation_errors.forEach((err) => {
            assistantContent += `- ${err.severity.toUpperCase()}: ${err.message}\n`;
          });
        }

        const assistantMessage = {
          role: "assistant",
          content: assistantContent,
          timestamp: new Date().toISOString(),
          sql: response.sql,
          isValid: response.is_valid,
          confidence: response.confidence
        };

        setMessages((prev) => [...prev, assistantMessage]);
        setIsLoading(false);
      } catch (err) {
        setError(err.message || "Failed to generate SQL");
        setIsLoading(false);
      }
    },
    [schema],
  );

  const handleExampleClick = (prompt) => {
    handleSendMessage(prompt);
  };

  const handleCopySQL = async (sql) => {
    await navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleCopyConversation = async () => {
    const text = messages
      .map((m) => {
        if (m.role === "user") {
          return `Question: ${m.content}`;
        } else {
          return `SQL:\n${m.sql || m.content}`;
        }
      })
      .join("\n\n");
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExportConversation = () => {
    const data = {
      schema,
      messages,
      exportedAt: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `sql-conversation-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleClearConversation = () => {
    setMessages([]);
  };

  return (
    <div className="h-screen flex bg-slate-950 text-slate-100 relative overflow-hidden">
      {/* Subtle background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-emerald-900/10 to-transparent pointer-events-none"></div>

      {/* Sidebar */}
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        onDeleteConversation={handleDeleteConversation}
        onRenameConversation={handleRenameConversation}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        onOpenSettings={() => { }} // Settings can be added later
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 relative z-10">
        {/* Header */}
        <header className="h-14 flex items-center justify-between px-6 border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl relative">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="lg:hidden p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
            >
              <Menu size={20} />
            </button>

            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center border border-emerald-400/30">
                <Database size={18} className="text-white" />
              </div>
              <span className="font-semibold text-slate-200 text-lg">SQL Agent</span>
            </div>
          </div>

          {/* Header actions */}
          {messages.length > 0 && (
            <div className="flex items-center gap-1">
              <button
                onClick={handleClearConversation}
                className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
                title="Clear conversation"
              >
                <RotateCcw size={18} />
              </button>
              <button
                onClick={handleCopyConversation}
                className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
                title="Copy conversation"
              >
                {copied ? (
                  <Check size={18} className="text-green-500" />
                ) : (
                  <Copy size={18} />
                )}
              </button>
              <button
                onClick={handleExportConversation}
                className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
                title="Export conversation"
              >
                <Download size={18} />
              </button>
            </div>
          )}
        </header>

        {/* Schema Input Section */}
        <div className="border-b border-slate-800 bg-slate-950/50">
          <div className="max-w-5xl mx-auto px-4 py-4">
            <SchemaInput schema={schema} onSchemaChange={setSchema} />
          </div>
        </div>

        {/* Messages Area */}
        <div className={`flex-1 relative ${messages.length === 0 ? 'overflow-hidden' : 'overflow-y-auto'}`}>
          {messages.length === 0 ? (
            <WelcomeScreen onExampleClick={handleExampleClick} />
          ) : (
            <div className="pb-6">
              {messages.map((message, index) => (
                <ChatMessage
                  key={index}
                  message={message}
                  isStreaming={false}
                />
              ))}

              {/* Typing indicator when loading */}
              {isLoading && (
                <ChatMessage
                  message={{ role: "assistant", content: "Generating SQL query..." }}
                  isStreaming={true}
                />
              )}

              {/* Error message */}
              {error && (
                <div className="max-w-3xl mx-auto px-4 py-4">
                  <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400 text-sm">
                    <strong>Error:</strong> {error}
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <ChatInput
          onSend={handleSendMessage}
          isLoading={isLoading}
          onStop={() => setIsLoading(false)}
        />
      </div>
    </div>
  );
}

export default App;
