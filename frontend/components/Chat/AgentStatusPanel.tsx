"use client";

import React from "react";
import { AgentStep, AgentName } from "@/store/researchStore";
import {
  Brain,
  Search,
  ShieldCheck,
  FileText,
  BarChart3,
  CheckCircle2,
  Loader2,
  Clock,
  AlertCircle,
  Activity,
} from "lucide-react";

interface AgentStatusPanelProps {
  steps: AgentStep[];
  isLoading: boolean;
}

const AGENT_CONFIG: Record<
  AgentName,
  { label: string; icon: React.ReactNode; colorClass: string; bgClass: string; description: string }
> = {
  planner: {
    label: "Planner",
    icon: <Brain size={16} />,
    colorClass: "agent-planner",
    bgClass: "agent-bg-planner",
    description: "Breaking query into research steps",
  },
  researcher: {
    label: "Researcher",
    icon: <Search size={16} />,
    colorClass: "agent-researcher",
    bgClass: "agent-bg-researcher",
    description: "Searching web, arXiv & documents",
  },
  fact_checker: {
    label: "Fact Checker",
    icon: <ShieldCheck size={16} />,
    colorClass: "agent-factcheck",
    bgClass: "agent-bg-factcheck",
    description: "Validating sources & flagging errors",
  },
  summarizer: {
    label: "Summarizer",
    icon: <FileText size={16} />,
    colorClass: "agent-summarizer",
    bgClass: "agent-bg-summarizer",
    description: "Extracting key concepts & notes",
  },
  reporter: {
    label: "Reporter",
    icon: <BarChart3 size={16} />,
    colorClass: "agent-reporter",
    bgClass: "agent-bg-reporter",
    description: "Generating structured report",
  },
  workflow: {
    label: "Workflow",
    icon: <Activity size={16} />,
    colorClass: "text-indigo-400",
    bgClass: "bg-indigo-500/10",
    description: "Orchestrating agent pipeline",
  },
};

const StatusIcon = ({ status }: { status: AgentStep["status"] }) => {
  if (status === "done")
    return <CheckCircle2 size={14} className="text-green-400" />;
  if (status === "running")
    return <Loader2 size={14} className="animate-spin text-indigo-400" />;
  if (status === "error")
    return <AlertCircle size={14} className="text-red-400" />;
  return <Clock size={14} className="text-slate-600" />;
};

const AgentStatusPanel: React.FC<AgentStatusPanelProps> = ({ steps, isLoading }) => {
  if (!isLoading && steps.every((s) => s.status === "pending")) return null;

  const completedCount = steps.filter((s) => s.status === "done").length;
  const progress = (completedCount / steps.length) * 100;

  return (
    <div className="glass rounded-2xl p-4 mb-4 fade-in-up">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isLoading ? "bg-indigo-400 pulse-dot" : "bg-green-400"
            }`}
          />
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Agent Pipeline
          </span>
        </div>
        <span className="text-xs text-slate-500">
          {completedCount}/{steps.length} agents complete
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full h-1 bg-slate-800 rounded-full mb-4 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{
            width: `${progress}%`,
            background: "linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899)",
          }}
        />
      </div>

      {/* Agent steps */}
      <div className="space-y-2">
        {steps.map((step, i) => {
          const config = AGENT_CONFIG[step.agent] || {
            label: step.agent || "Unknown",
            icon: <Activity size={16} />,
            colorClass: "text-slate-400",
            bgClass: "bg-slate-800/50",
            description: "System process",
          };
          const isActive = step.status === "running";
          return (
            <div
              key={step.agent}
              className={`flex items-start gap-3 p-2.5 rounded-xl border transition-all duration-300 ${
                isActive
                  ? `${config.bgClass} scale-[1.01]`
                  : step.status === "done"
                  ? "bg-green-500/5 border-green-500/20"
                  : step.status === "error"
                  ? "bg-red-500/5 border-red-500/20"
                  : "border-transparent"
              }`}
              style={{ animationDelay: `${i * 0.05}s` }}
            >
              <div className={`mt-0.5 ${config.colorClass}`}>{config.icon}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span
                    className={`text-sm font-semibold ${
                      step.status === "pending"
                        ? "text-slate-600"
                        : step.status === "done"
                        ? "text-slate-300"
                        : config.colorClass
                    }`}
                  >
                    {config.label}
                  </span>
                  {isActive && (
                    <span className="text-xs bg-indigo-500/20 text-indigo-300 px-1.5 py-0.5 rounded-full">
                      Active
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-600 mt-0.5">
                  {step.message || config.description}
                </p>
              </div>
              <StatusIcon status={step.status} />
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AgentStatusPanel;
