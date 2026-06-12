"use client";

import React, { useState } from "react";
import { useResearchStore } from "@/store/researchStore";
import Sidebar from "@/components/Sidebar/Sidebar";
import ChatWindow from "@/components/Chat/ChatWindow";
import ReportViewer from "@/components/Reports/ReportViewer";
import UploadZone from "@/components/Upload/UploadZone";
import { Moon, Sun, Activity, Menu } from "lucide-react";

export default function Home() {
  const { activeTab, sidebarOpen, setSidebarOpen, theme, toggleTheme } = useResearchStore();

  return (
    <div
      className="flex h-[100dvh] overflow-hidden"
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
      <div className="flex-1 flex flex-col min-w-0 relative h-full">
        {/* Top bar */}
        <header
          className="flex items-center justify-between px-4 sm:px-6 py-3 sm:py-4 border-b"
          style={{ borderColor: "var(--border)" }}
        >
          <div className="flex items-center gap-3">
            {/* Mobile Sidebar Toggle */}
            {!sidebarOpen && (
              <button
                onClick={() => setSidebarOpen(true)}
                className="md:hidden p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 transition-colors"
              >
                <Menu size={20} />
              </button>
            )}
            
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

          <div className="flex items-center gap-2 sm:gap-3">
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="relative overflow-hidden w-9 h-9 sm:w-10 sm:h-10 rounded-xl flex items-center justify-center transition-all duration-300 border border-slate-800/60 text-slate-400 hover:border-indigo-500/30 hover:text-indigo-300 glass hover:scale-105"
              title="Toggle Theme"
            >
              <div
                className={`absolute inset-0 flex items-center justify-center transition-transform duration-500 ${
                  theme === "dark" ? "translate-y-0 rotate-0 opacity-100" : "-translate-y-full rotate-90 opacity-0"
                }`}
              >
                <Moon size={18} />
              </div>
              <div
                className={`absolute inset-0 flex items-center justify-center transition-transform duration-500 ${
                  theme === "light" ? "translate-y-0 rotate-0 opacity-100" : "translate-y-full -rotate-90 opacity-0"
                }`}
              >
                <Sun size={18} />
              </div>
            </button>

            {/* Status badge */}
            <div className="flex items-center gap-2 px-3 py-2 glass rounded-xl">
              <div className="w-2 h-2 rounded-full bg-green-400 pulse-dot" />
              <span className="text-xs text-slate-500 hidden sm:inline">5 Agents Ready</span>
              <span className="text-xs text-slate-500 sm:hidden">Ready</span>
            </div>
          </div>
        </header>

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
