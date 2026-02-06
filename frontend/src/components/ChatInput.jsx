import React, { useState, useRef, useEffect } from "react";
import { Send, Square, Paperclip, X, Image, FileText, File } from "lucide-react";

const ChatInput = ({ onSend, isLoading, onStop }) => {
  const [message, setMessage] = useState("");
  const [attachments, setAttachments] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + "px";
    }
  }, [message]);

  // Handle paste event for images
  useEffect(() => {
    const handlePaste = (e) => {
      const items = e.clipboardData?.items;
      if (!items) return;

      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if (item.type.startsWith("image/")) {
          e.preventDefault();
          const file = item.getAsFile();
          if (file) {
            addAttachment(file);
          }
        }
      }
    };

    const textarea = textareaRef.current;
    if (textarea) {
      textarea.addEventListener("paste", handlePaste);
      return () => textarea.removeEventListener("paste", handlePaste);
    }
  }, []);

  const addAttachment = (file) => {
    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert("File size must be less than 10MB");
      return;
    }

    // Create preview URL for images
    const isImage = file.type.startsWith("image/");
    const preview = isImage ? URL.createObjectURL(file) : null;

    const attachment = {
      id: Date.now() + Math.random(),
      file,
      name: file.name,
      type: file.type,
      size: file.size,
      preview,
      isImage,
    };

    setAttachments((prev) => [...prev, attachment]);
  };

  const removeAttachment = (id) => {
    setAttachments((prev) => {
      const attachment = prev.find((a) => a.id === id);
      if (attachment?.preview) {
        URL.revokeObjectURL(attachment.preview);
      }
      return prev.filter((a) => a.id !== id);
    });
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files || []);
    files.forEach(addAttachment);
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    files.forEach(addAttachment);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSend(message.trim());
      setMessage("");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const getFileIcon = (type) => {
    if (type.startsWith("image/")) return Image;
    if (type.includes("pdf") || type.includes("document")) return FileText;
    return File;
  };

  const canSend = message.trim() && !isLoading;

  return (
    <div className="border-t border-slate-800 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-3xl mx-auto px-4 py-4">
        <form onSubmit={handleSubmit} className="relative">
          {/* Attachments Preview */}
          {attachments.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3 p-3 bg-slate-800/50 rounded-xl border border-slate-700">
              {attachments.map((attachment) => (
                <div
                  key={attachment.id}
                  className="relative group flex items-center gap-2 bg-slate-700/50 rounded-lg p-2 pr-8 border border-slate-600"
                >
                  {attachment.isImage && attachment.preview ? (
                    <img
                      src={attachment.preview}
                      alt={attachment.name}
                      className="w-12 h-12 object-cover rounded-md"
                    />
                  ) : (
                    <div className="w-12 h-12 flex items-center justify-center bg-slate-600 rounded-md">
                      {React.createElement(getFileIcon(attachment.type), {
                        size: 24,
                        className: "text-slate-300",
                      })}
                    </div>
                  )}
                  <div className="flex flex-col min-w-0">
                    <span className="text-xs text-slate-200 truncate max-w-[120px]">
                      {attachment.name}
                    </span>
                    <span className="text-xs text-slate-500">
                      {formatFileSize(attachment.size)}
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeAttachment(attachment.id)}
                    className="absolute top-1 right-1 p-1 bg-slate-800 hover:bg-red-500/20 text-slate-400 hover:text-red-400 rounded-full transition-colors"
                    title="Remove"
                  >
                    <X size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Main Input Container */}
          <div
            className={`relative flex items-end bg-slate-800 rounded-2xl border transition-colors shadow-lg ${isDragging
              ? "border-slate-500 bg-slate-700/50"
              : "border-slate-700 focus-within:border-slate-600"
              }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            {/* Drag overlay */}
            {isDragging && (
              <div className="absolute inset-0 flex items-center justify-center bg-slate-800/90 rounded-2xl z-10">
                <div className="flex flex-col items-center gap-2 text-slate-400">
                  <Image size={32} />
                  <span className="text-sm">Drop files here</span>
                </div>
              </div>
            )}

            {/* Left side - Hidden attachment button */}
            <div className="flex items-center pl-2 pb-2" style={{ display: 'none' }}>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*,.pdf,.doc,.docx,.txt,.csv,.json,.xml"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>

            {/* Textarea */}
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about your database..."
              rows={1}
              className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 py-3 px-2 focus:outline-none resize-none max-h-[200px]"
              disabled={isLoading}
            />

            {/* Right side buttons */}
            <div className="flex items-center gap-1 p-2">
              {/* Send/Stop button */}
              {isLoading ? (
                <button
                  type="button"
                  onClick={onStop}
                  className="p-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors"
                  title="Stop generating"
                >
                  <Square size={20} fill="currentColor" />
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={!canSend}
                  className={`p-2 rounded-lg transition-all ${canSend
                    ? "bg-emerald-600 text-white hover:bg-emerald-500"
                    : "bg-slate-700 text-slate-500 cursor-not-allowed"
                    }`}
                  title="Generate SQL"
                >
                  <Send size={20} />
                </button>
              )}
            </div>
          </div>

          {/* Footer text */}
          <p className="text-center text-xs text-slate-500 mt-3">
            SQL Agent generates queries based on your schema. Always verify before execution.
          </p>
        </form>
      </div>
    </div>
  );
};

export default ChatInput;
