"use client";

import React, { useState } from "react";
import { useResearchStore } from "@/store/researchStore";
import Sidebar from "@/components/Sidebar/Sidebar";
import ChatWindow from "@/components/Chat/ChatWindow";
import ReportViewer from "@/components/Reports/ReportViewer";
import UploadZone from "@/components/Upload/UploadZone";
import { Upload, X, Activity } from "lucide-react";

export default function Home() {
  const { activeTab, sidebarOpen } = useResearchStore();
  const [showUpload, setShowUpload] = useState(false);

  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{ background: "var(--bg-primary)" }}
    >
      {/* Ambient background */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background: `
            radial-gradient(ellipse 80% 50% at 20% 20%, rgba(99,102,241,0.08) 0%, transparent 60%),
            radial-gradient(ellipse 60% 40% at 80% 80%, rgba(139,92,246,0.06) 0%, transparent 60%),
            radial-gradient(ellipse 40% 30% at 50% 50%, rgba(20,184,166,0.04) 0%, transparent 60%)
          `,
        }}
      />

      {/* Sidebar */}
      <Sidebar />

      {/* Main area */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        {/* Top bar */}
        <header
          className="flex items-center justify-between px-6 py-4 border-b"
          style={{ borderColor: "var(--border)" }}
        >
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Activity size={16} className="text-indigo-400" />
              <span className="text-sm font-semibold text-slate-300">
                {activeTab === "chat"
                  ? "Research Chat"
                  : activeTab === "reports"
                  ? "Research Reports"
                  : "Document Library"}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Upload button */}
            <button
              onClick={() => setShowUpload(!showUpload)}
              className={`flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-semibold transition-all duration-200 border ${
                showUpload
                  ? "bg-indigo-500/20 border-indigo-500/40 text-indigo-300"
                  : "border-slate-800 text-slate-400 hover:border-indigo-500/30 hover:text-slate-200"
              }`}
            >
              {showUpload ? <X size={14} /> : <Upload size={14} />}
              {showUpload ? "Close" : "Upload PDF"}
            </button>

            {/* Status badge */}
            <div className="flex items-center gap-2 px-3 py-2 glass rounded-xl">
              <div className="w-2 h-2 rounded-full bg-green-400 pulse-dot" />
              <span className="text-xs text-slate-500">5 Agents Ready</span>
            </div>
          </div>
        </header>

        {/* Upload panel (overlay) */}
        {showUpload && (
          <div className="absolute top-[73px] right-6 z-20 w-[480px] fade-in-up">
            <UploadZone onClose={() => setShowUpload(false)} />
          </div>
        )}

        {/* Content */}
        <main className="flex-1 overflow-hidden">
          {activeTab === "chat" ? (
            <ChatWindow />
          ) : activeTab === "reports" ? (
            <ReportViewer />
          ) : (
            <div className="p-6 h-full overflow-y-auto">
              <UploadZone />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
