import React from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Copy, Check, User, Cpu, Image, FileText, File, Download } from "lucide-react";

const CodeBlock = ({ language, children }) => {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(children);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group my-6">
      <div className="absolute top-0 left-0 right-0 flex items-center justify-between px-5 py-3 glass border-b border-slate-700/50 rounded-t-xl backdrop-blur-xl z-10">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-red-500"></div>
          <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
          <div className="w-2 h-2 rounded-full bg-green-500"></div>
          <span className="text-xs text-slate-400 font-mono uppercase tracking-wider ml-2">
            {language || "code"}
          </span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-2 px-3 py-1.5 text-xs text-slate-400 hover:text-slate-200 bg-slate-800/50 hover:bg-slate-700/50 rounded-lg transition-all duration-300 border border-transparent hover:border-slate-600"
        >
          {copied ? (
            <>
              <Check size={14} className="text-cyber-500" />
              <span>Copied!</span>
            </>
          ) : (
            <>
              <Copy size={14} />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>
      <div className="relative overflow-hidden rounded-xl border border-slate-700 shadow-glow">
        <SyntaxHighlighter
          language={language}
          style={vscDarkPlus}
          customStyle={{
            margin: 0,
            borderRadius: "0 0 12px 12px",
            paddingTop: "3.5rem",
            paddingBottom: "1.5rem",
            background: "linear-gradient(135deg, #0c1220 0%, #0a0a0f 100%)",
            fontSize: "0.875rem",
            lineHeight: "1.6",
          }}
          showLineNumbers
          lineNumberStyle={{
            minWidth: "3em",
            paddingRight: "1em",
            color: "#475569",
            userSelect: "none",
          }}
        >
          {children}
        </SyntaxHighlighter>
      </div>
    </div>
  );
};

const MessageContent = ({ content }) => {
  return (
    <ReactMarkdown
      className="prose max-w-none"
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || "");
          const language = match ? match[1] : "";

          if (!inline && (match || String(children).includes("\n"))) {
            return (
              <CodeBlock language={language}>
                {String(children).replace(/\n$/, "")}
              </CodeBlock>
            );
          }

          return (
            <code className={className} {...props}>
              {children}
            </code>
          );
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
};

const TypingIndicator = () => (
  <div className="flex items-center gap-1 py-2">
    <div className="w-2 h-2 bg-slate-500 rounded-full typing-dot"></div>
    <div className="w-2 h-2 bg-slate-500 rounded-full typing-dot"></div>
    <div className="w-2 h-2 bg-slate-500 rounded-full typing-dot"></div>
  </div>
);

const AttachmentPreview = ({ attachments }) => {
  if (!attachments || attachments.length === 0) return null;

  const getFileIcon = (type) => {
    if (type.startsWith("image/")) return Image;
    if (type.includes("pdf") || type.includes("document")) return FileText;
    return File;
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const handleDownload = (attachment) => {
    const link = document.createElement("a");
    link.href = attachment.data;
    link.download = attachment.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex flex-wrap gap-3 mb-3">
      {attachments.map((attachment) => (
        <div
          key={attachment.id}
          className="relative group rounded-xl overflow-hidden border border-slate-700 bg-slate-800/50"
        >
          {attachment.isImage ? (
            <div className="relative">
              <img
                src={attachment.data}
                alt={attachment.name}
                className="max-w-[300px] max-h-[200px] object-cover rounded-xl"
              />
              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                <button
                  onClick={() => window.open(attachment.data, "_blank")}
                  className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white text-xs"
                >
                  View Full
                </button>
                <button
                  onClick={() => handleDownload(attachment)}
                  className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white"
                >
                  <Download size={16} />
                </button>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-3 p-3 min-w-[200px]">
              <div className="w-10 h-10 flex items-center justify-center bg-slate-700 rounded-lg">
                {React.createElement(getFileIcon(attachment.type), {
                  size: 20,
                  className: "text-slate-300",
                })}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-slate-200 truncate">{attachment.name}</p>
                <p className="text-xs text-slate-500">{formatFileSize(attachment.size)}</p>
              </div>
              <button
                onClick={() => handleDownload(attachment)}
                className="p-2 hover:bg-slate-700 rounded-lg text-slate-400 hover:text-slate-200 transition-colors"
                title="Download"
              >
                <Download size={16} />
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

const ChatMessage = ({ message, isStreaming }) => {
  const isUser = message.role === "user";

  return (
    <div
      className={`message-enter py-6 ${
        isUser ? "bg-transparent" : "bg-slate-900/50"
      }`}
    >
      <div className="max-w-3xl mx-auto px-4 sm:px-6">
        <div className="flex gap-4">
          {/* Avatar */}
          <div
            className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center border ${
              isUser
                ? "bg-gradient-to-br from-slate-600 to-slate-700 border-slate-500"
                : "bg-gradient-to-br from-slate-700 to-slate-900 border-slate-600"
            }`}
          >
            {isUser ? (
              <User size={18} className="text-slate-200" />
            ) : (
              <Cpu size={18} className="text-white" />
            )}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="font-semibold text-slate-100 text-sm">
                {isUser ? "You" : "Core"}
              </span>
              {message.timestamp && (
                <span className="text-xs text-slate-500">
                  {new Date(message.timestamp).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              )}
            </div>

            {/* Attachments */}
            {message.attachments && message.attachments.length > 0 && (
              <AttachmentPreview attachments={message.attachments} />
            )}

            {isStreaming && !message.content ? (
              <TypingIndicator />
            ) : (
              message.content && <MessageContent content={message.content} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
