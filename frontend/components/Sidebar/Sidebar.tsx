"use client";

import React, { useEffect } from "react";
import { useResearchStore } from "@/store/researchStore";
import { getChatHistory, getDocuments } from "@/services/api";
import {
  MessageSquare,
  Plus,
  FileText,
  Upload,
  ChevronLeft,
  ChevronRight,
  Bot,
  History,
  Folders,
  BookOpen,
  Zap,
} from "lucide-react";
import { format } from "date-fns";

const Sidebar: React.FC = () => {
  const {
    sidebarOpen,
    setSidebarOpen,
    activeTab,
    setActiveTab,
    chatHistory,
    setChatHistory,
    documents,
    setDocuments,
    newChat,
    setActiveChatId,
    activeChatId,
  } = useResearchStore();

  useEffect(() => {
    getChatHistory()
      .then((h) => setChatHistory(h as never[]))
      .catch(() => {});
    getDocuments()
      .then((d) => setDocuments(d))
      .catch(() => {});
  }, []);

  const navItems = [
    { id: "chat", icon: <MessageSquare size={18} />, label: "Chat" },
    { id: "reports", icon: <BookOpen size={18} />, label: "Reports" },
    { id: "documents", icon: <Folders size={18} />, label: "Documents" },
  ];

  return (
    <>
      {/* Collapsed toggle */}
      {!sidebarOpen && (
        <button
          onClick={() => setSidebarOpen(true)}
          className="fixed left-4 top-1/2 -translate-y-1/2 z-30 w-8 h-8 glass-bright rounded-full flex items-center justify-center hover:border-indigo-500/40 transition-all"
        >
          <ChevronRight size={14} className="text-slate-400" />
        </button>
      )}

      {/* Mobile backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-30 md:hidden backdrop-blur-sm transition-opacity"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={`flex flex-col h-full glass-bright transition-all duration-300 ease-in-out z-40 absolute md:relative ${
          sidebarOpen ? "w-72 md:w-72 translate-x-0" : "w-72 md:w-0 -translate-x-full md:translate-x-0 overflow-hidden"
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-5 border-b border-slate-800/60">
          <div className="flex items-center gap-3">
            <div
              className="w-8 h-8 rounded-xl flex items-center justify-center"
              style={{ background: "linear-gradient(135deg, #6366f1, #8b5cf6)" }}
            >
              <Bot size={16} className="text-white" />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-200">Research AI</p>
              <div className="flex items-center gap-1.5">
                <Zap size={10} className="text-green-400" />
                <span className="text-xs text-green-400">Gemini 1.5 Pro</span>
              </div>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="btn-ghost p-1.5 rounded-lg"
          >
            <ChevronLeft size={14} />
          </button>
        </div>

        {/* New Chat button */}
        <div className="px-4 pt-4">
          <button
            onClick={newChat}
            className="btn-primary w-full flex items-center justify-center gap-2 py-2.5"
          >
            <Plus size={16} />
            <span className="text-sm">New Research</span>
          </button>
        </div>

        {/* Nav tabs */}
        <div className="flex gap-1 mx-4 mt-4 p-1 glass rounded-xl">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id as never)}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold transition-all duration-200 ${
                activeTab === item.id
                  ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                  : "text-slate-500 hover:text-slate-300"
              }`}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-4 py-3">
          {/* Chat History Tab */}
          {activeTab === "chat" && (
            <div className="space-y-1">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-600 mb-3 flex items-center gap-2">
                <History size={12} />
                Recent Sessions
              </p>
              {chatHistory.length === 0 ? (
                <div className="text-center py-8">
                  <MessageSquare size={28} className="text-slate-700 mx-auto mb-2" />
                  <p className="text-xs text-slate-600">No sessions yet</p>
                </div>
              ) : (
                chatHistory.slice(0, 20).map((chat) => (
                  <button
                    key={chat.id}
                    onClick={() => setActiveChatId(chat.id)}
                    className={`w-full text-left p-3 rounded-xl transition-all duration-200 ${
                      activeChatId === chat.id
                        ? "bg-indigo-500/10 border border-indigo-500/30"
                        : "hover:bg-slate-800/50"
                    }`}
                  >
                    <p className="text-sm text-slate-300 truncate font-medium">
                      {chat.query}
                    </p>
                    <p className="text-xs text-slate-600 mt-1">
                      {format(new Date(chat.created_at), "MMM d, HH:mm")}
                    </p>
                  </button>
                ))
              )}
            </div>
          )}

          {/* Reports Tab */}
          {activeTab === "reports" && (
            <div className="space-y-1">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-600 mb-3 flex items-center gap-2">
                <FileText size={12} />
                Generated Reports
              </p>
              <p className="text-xs text-slate-600 text-center py-8">
                Reports appear here after completing a research session.
              </p>
            </div>
          )}

          {/* Documents Tab */}
          {activeTab === "documents" && (
            <div className="space-y-1">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-600 mb-3 flex items-center gap-2">
                <Upload size={12} />
                Indexed Documents
              </p>
              {documents.length === 0 ? (
                <div className="text-center py-8">
                  <FileText size={28} className="text-slate-700 mx-auto mb-2" />
                  <p className="text-xs text-slate-600">No PDFs uploaded yet</p>
                  <p className="text-xs text-slate-700 mt-1">
                    Upload PDFs via the toolbar
                  </p>
                </div>
              ) : (
                documents.map((doc) => (
                  <div key={doc.id} className="p-3 rounded-xl hover:bg-slate-800/50 transition-colors">
                    <p className="text-sm text-slate-300 font-medium truncate">{doc.title}</p>
                    <p className="text-xs text-slate-600 mt-0.5">
                      {format(new Date(doc.created_at), "MMM d, yyyy")}
                    </p>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-4 border-t border-slate-800/60">
          <div className="glass rounded-xl p-3">
            <p className="text-xs text-slate-600 text-center">
              5 agents · RAG pipeline · ChromaDB
            </p>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
