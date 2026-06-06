"use client";

import React, { useEffect, useState } from "react";
import { getReports, getReportById, deleteReport } from "@/services/api";
import {
  BookOpen,
  Trash2,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Loader2,
  FileText,
} from "lucide-react";
import { format } from "date-fns";

interface ReportItem {
  id: number;
  title: string;
  executive_summary?: string;
  findings?: string[];
  key_concepts?: string[];
  references?: { title: string; url: string; source: string }[];
  conclusion?: string;
  created_at: string;
}

const ReportViewer: React.FC = () => {
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [expanded, setExpanded] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState<number | null>(null);

  useEffect(() => {
    getReports()
      .then((data) => setReports(data as ReportItem[]))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const toggleReport = async (id: number) => {
    if (expanded === id) {
      setExpanded(null);
      return;
    }
    // Fetch full detail if not already loaded
    const existing = reports.find((r) => r.id === id);
    if (!existing?.findings) {
      setDetailLoading(id);
      try {
        const detail = await getReportById(id);
        setReports((prev) =>
          prev.map((r) => (r.id === id ? { ...r, ...detail } : r))
        );
      } catch {}
      setDetailLoading(null);
    }
    setExpanded(id);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this report?")) return;
    try {
      await deleteReport(id);
      setReports((prev) => prev.filter((r) => r.id !== id));
    } catch {}
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 size={24} className="animate-spin text-indigo-400" />
      </div>
    );
  }

  if (reports.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center fade-in-up">
        <BookOpen size={40} className="text-slate-700 mb-4" />
        <h3 className="text-slate-400 font-semibold text-lg">No reports yet</h3>
        <p className="text-slate-600 text-sm mt-2 max-w-xs">
          Research reports will appear here after you complete a chat session.
        </p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4 overflow-y-auto h-full fade-in-up">
      <div className="flex items-center gap-3 mb-6">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center"
          style={{ background: "linear-gradient(135deg, #6366f1, #ec4899)" }}
        >
          <BookOpen size={18} className="text-white" />
        </div>
        <div>
          <h2 className="font-bold text-slate-200 text-xl">Research Reports</h2>
          <p className="text-sm text-slate-500">{reports.length} report{reports.length !== 1 ? "s" : ""} generated</p>
        </div>
      </div>

      {reports.map((report) => (
        <div key={report.id} className="glass rounded-2xl overflow-hidden">
          {/* Report header */}
          <button
            onClick={() => toggleReport(report.id)}
            className="w-full flex items-center justify-between p-5 text-left hover:bg-white/5 transition-colors"
          >
            <div className="flex items-start gap-3 flex-1 min-w-0">
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                style={{ background: "rgba(99,102,241,0.15)", border: "1px solid rgba(99,102,241,0.3)" }}
              >
                <FileText size={14} className="text-indigo-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-slate-200 truncate">{report.title}</p>
                <p className="text-xs text-slate-600 mt-1">
                  {format(new Date(report.created_at), "MMMM d, yyyy · HH:mm")}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 ml-3">
              <button
                onClick={(e) => { e.stopPropagation(); handleDelete(report.id); }}
                className="p-1.5 rounded-lg text-slate-600 hover:text-red-400 hover:bg-red-500/10 transition-all"
              >
                <Trash2 size={14} />
              </button>
              {detailLoading === report.id ? (
                <Loader2 size={14} className="animate-spin text-indigo-400" />
              ) : expanded === report.id ? (
                <ChevronUp size={16} className="text-slate-500" />
              ) : (
                <ChevronDown size={16} className="text-slate-500" />
              )}
            </div>
          </button>

          {/* Expanded content */}
          {expanded === report.id && report.findings && (
            <div className="px-5 pb-5 space-y-5 border-t border-slate-800/60 pt-5 fade-in-up">
              {/* Executive Summary */}
              {report.executive_summary && (
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                    Executive Summary
                  </h4>
                  <p className="text-sm text-slate-300 leading-relaxed">
                    {report.executive_summary}
                  </p>
                </div>
              )}

              {/* Key Concepts */}
              {report.key_concepts && report.key_concepts.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                    Key Concepts
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {report.key_concepts.map((c, i) => (
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
              {report.findings && report.findings.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                    Key Findings
                  </h4>
                  <ul className="space-y-2">
                    {report.findings.map((f, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                        <span className="text-indigo-400 mt-1 flex-shrink-0">▸</span>
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* References */}
              {report.references && report.references.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                    Sources & References
                  </h4>
                  <div className="space-y-1.5">
                    {report.references.map((ref, i) => (
                      <a
                        key={i}
                        href={ref.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-xs text-slate-400 hover:text-indigo-400 transition-colors group"
                      >
                        <ExternalLink size={10} className="flex-shrink-0" />
                        <span className="truncate">{ref.title || ref.url}</span>
                        <span className="flex-shrink-0 text-slate-600">
                          ({ref.source})
                        </span>
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {/* Conclusion */}
              {report.conclusion && (
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                    Conclusion
                  </h4>
                  <p className="text-sm text-slate-300 leading-relaxed">
                    {report.conclusion}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ReportViewer;
