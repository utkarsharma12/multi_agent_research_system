"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import { Message } from "@/store/researchStore";
import { Bot, User, ChevronDown, ChevronUp, ExternalLink } from "lucide-react";
import { format } from "date-fns";
import AgentStatusPanel from "./AgentStatusPanel";

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const [reportExpanded, setReportExpanded] = React.useState(false);
  const isUser = message.role === "user";
  const time = format(new Date(message.createdAt), "HH:mm");

  if (isUser) {
    return (
      <div className="flex items-end gap-3 justify-end fade-in-up">
        <div className="max-w-[75%]">
          <div
            className="rounded-2xl rounded-br-sm px-5 py-3.5 text-white"
            style={{
              background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              boxShadow: "0 4px 20px rgba(99, 102, 241, 0.3)",
            }}
          >
            <p className="text-sm leading-relaxed">{message.content}</p>
          </div>
          <p className="text-xs text-slate-600 text-right mt-1 mr-1">{time}</p>
        </div>
        <div className="w-8 h-8 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center flex-shrink-0">
          <User size={14} className="text-indigo-300" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3 fade-in-up">
      {/* Bot avatar */}
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1"
        style={{
          background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
          boxShadow: "0 0 16px rgba(99,102,241,0.4)",
        }}
      >
        <Bot size={14} className="text-white" />
      </div>

      <div className="flex-1 min-w-0 max-w-[90%]">
        {/* Agent steps if present */}
        {message.agentSteps && message.agentSteps.length > 0 && (
          <AgentStatusPanel steps={message.agentSteps} isLoading={false} />
        )}

        {/* Main response */}
        <div className="glass rounded-2xl rounded-tl-sm p-5">
          <div className="markdown-body">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>

          {/* Report section */}
          {message.report && (
            <div className="mt-4 border-t border-slate-800 pt-4">
              <button
                onClick={() => setReportExpanded(!reportExpanded)}
                className="flex items-center gap-2 text-sm font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
              >
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ background: "linear-gradient(135deg, #6366f1, #ec4899)" }}
                />
                Full Research Report
                {reportExpanded ? (
                  <ChevronUp size={14} />
                ) : (
                  <ChevronDown size={14} />
                )}
              </button>

              {reportExpanded && (
                <div className="mt-3 space-y-4 fade-in-up">
                  {/* Executive Summary */}
                  <div>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                      Executive Summary
                    </h4>
                    <p className="text-sm text-slate-300 leading-relaxed">
                      {message.report.executive_summary}
                    </p>
                  </div>

                  {/* Key Concepts */}
                  {message.report.key_concepts?.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                        Key Concepts
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {message.report.key_concepts.map((c, i) => (
                          <span
                            key={i}
                            className="text-xs bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 px-2.5 py-1 rounded-full"
                          >
                            {c}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Findings */}
                  {message.report.findings?.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                        Key Findings
                      </h4>
                      <ul className="space-y-1.5">
                        {message.report.findings.map((f, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                            <span className="text-indigo-400 mt-1 flex-shrink-0">▸</span>
                            <span>{f}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* References */}
                  {message.report.references?.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                        Sources
                      </h4>
                      <div className="space-y-1.5">
                        {message.report.references.slice(0, 5).map((ref, i) => (
                          <a
                            key={i}
                            href={ref.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2 text-xs text-slate-400 hover:text-indigo-400 transition-colors group"
                          >
                            <ExternalLink size={10} className="flex-shrink-0 group-hover:text-indigo-400" />
                            <span className="truncate">{ref.title || ref.url}</span>
                            <span className="flex-shrink-0 text-slate-600">({ref.source})</span>
                          </a>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Conclusion */}
                  {message.report.conclusion && (
                    <div>
                      <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                        Conclusion
                      </h4>
                      <p className="text-sm text-slate-300 leading-relaxed">
                        {message.report.conclusion}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
        <p className="text-xs text-slate-600 mt-1 ml-1">{time}</p>
      </div>
    </div>
  );
};

export default MessageBubble;
