"use client";

import React, { useEffect, useRef, useState } from "react";
import { useResearchStore, AgentStep } from "@/store/researchStore";
import { getApiErrorMessage, getChatById, sendChat } from "@/services/api";
import MessageBubble from "./MessageBubble";
import AgentStatusPanel from "./AgentStatusPanel";
import UploadZone from "../Upload/UploadZone";
import { Send, Sparkles, Loader2, Paperclip } from "lucide-react";

const EXAMPLE_QUERIES = [
  "Explain quantum computing and its real-world applications",
  "What are the latest breakthroughs in large language models?",
  "Summarize the key findings in CRISPR gene editing research",
  "How does transformer architecture work in modern AI?",
];

const MIN_QUERY_LENGTH = 3;
const NON_RESEARCH_INPUTS = new Set([
  "hello",
  "hi",
  "hey",
  "hii",
  "hiii",
  "ok",
  "okay",
  "test",
  "thanks",
  "thank you",
]);

const ChatWindow: React.FC = () => {
  const {
    messages,
    addMessage,
    updateLastAssistantMessage,
    activeAgentSteps,
    setActiveAgentSteps,
    updateAgentStep,
    isLoading,
    setIsLoading,
    setChatHistory,
    activeChatId,
    documents,
  } = useResearchStore();

  const [input, setInput] = useState("");
  const [showUploadZone, setShowUploadZone] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  useEffect(() => {
    if (!activeChatId || isLoading) return;

    let cancelled = false;

    const loadChat = async () => {
      try {
        const chat = await getChatById(activeChatId);
        if (cancelled) return;

        useResearchStore.setState({
          messages: [
            {
              id: `chat-${chat.id}-user`,
              role: "user",
              content: chat.query,
              createdAt: new Date(chat.created_at).getTime(),
            },
            {
              id: `chat-${chat.id}-assistant`,
              role: "assistant",
              content: chat.response,
              agentSteps: chat.agent_steps as AgentStep[],
              report: chat.report,
              createdAt: new Date(chat.created_at).getTime(),
            },
          ],
          activeTab: "chat",
        });
      } catch (err: unknown) {
        if (cancelled) return;
        addMessage({
          id: crypto.randomUUID(),
          role: "assistant",
          content: `Could not open that chat: ${getApiErrorMessage(err)}`,
          createdAt: Date.now(),
        });
      }
    };

    loadChat();

    return () => {
      cancelled = true;
    };
  }, [activeChatId, addMessage, isLoading]);

  // Auto-resize textarea
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = "auto";
      ta.style.height = Math.min(ta.scrollHeight, 160) + "px";
    }
  };

  const simulateAgentProgress = async (
    onUpdate: (agent: string, status: string, msg: string) => void
  ) => {
    const agents = [
      { name: "planner", msg: "Creating research plan…" },
      { name: "researcher", msg: "Searching web, arXiv & documents…" },
      { name: "fact_checker", msg: "Validating sources…" },
      { name: "summarizer", msg: "Extracting key concepts…" },
      { name: "reporter", msg: "Generating report…" },
    ];
    for (const a of agents) {
      onUpdate(a.name, "running", a.msg);
      await new Promise((r) => setTimeout(r, 400));
    }
  };

  const handleSubmit = async () => {
    let query = input.trim();
    
    // If input is empty but documents exist, use a default analysis query
    if (!query && documents.length > 0) {
      query = "Please analyze the uploaded documents and provide a comprehensive summary of their key findings and concepts.";
    }

    if (!query || isLoading) return;
    if (query.length < MIN_QUERY_LENGTH) {
      setInput("");
      addMessage({
        id: crypto.randomUUID(),
        role: "assistant",
        content: "Please enter at least 3 characters for your research question.",
        createdAt: Date.now(),
      });
      return;
    }
    if (NON_RESEARCH_INPUTS.has(query.toLowerCase())) {
      setInput("");
      addMessage({
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          "Please ask a specific research question, for example: \"What are the latest applications of quantum computing?\"",
        createdAt: Date.now(),
      });
      return;
    }

    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";

    // Add user message
    const userMsg = {
      id: crypto.randomUUID(),
      role: "user" as const,
      content: query,
      createdAt: Date.now(),
    };
    addMessage(userMsg);

    // Reset & start agent steps
    const freshSteps: AgentStep[] = [
      { agent: "planner",      status: "pending" },
      { agent: "researcher",   status: "pending" },
      { agent: "fact_checker", status: "pending" },
      { agent: "summarizer",   status: "pending" },
      { agent: "reporter",     status: "pending" },
    ];
    setActiveAgentSteps(freshSteps);
    setIsLoading(true);

    // Add placeholder assistant message
    const assistantId = crypto.randomUUID();
    addMessage({
      id: assistantId,
      role: "assistant",
      content: "",
      createdAt: Date.now(),
    });

    // Animate agent steps while API call runs
    simulateAgentProgress((agent, status, msg) => {
      updateAgentStep(agent as AgentStep["agent"], { status: status as AgentStep["status"], message: msg });
    });

    try {
      const result = await sendChat(query);

      // Mark all steps done
      const completedSteps: AgentStep[] = [
        { agent: "planner",      status: "done", message: "Plan created" },
        { agent: "researcher",   status: "done", message: "Research complete" },
        { agent: "fact_checker", status: "done", message: "Facts verified" },
        { agent: "summarizer",   status: "done", message: "Summary ready" },
        { agent: "reporter",     status: "done", message: "Report generated" },
      ];
      setActiveAgentSteps(completedSteps);

      // Update the assistant message
      updateLastAssistantMessage({
        content: result.response,
        agentSteps: completedSteps,
        report: result.report,
      });

      // Refresh chat history
      try {
        const { getChatHistory } = await import("@/services/api");
        const hist = await getChatHistory();
        setChatHistory(hist as never[]);
      } catch {}
    } catch (err: unknown) {
      const errorSteps: AgentStep[] = freshSteps.map((s) =>
        s.status === "running" ? { ...s, status: "error" } : s
      );
      setActiveAgentSteps(errorSteps);

      const errorMsg = getApiErrorMessage(err);
      updateLastAssistantMessage({
        content: `❌ **Error**: ${errorMsg}\n\nMake sure the backend is running at \`http://localhost:8000\`.`,
        agentSteps: errorSteps,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 sm:py-6 space-y-4 sm:space-y-6">
        {isEmpty ? (
          <div className="flex flex-col items-center justify-center h-full text-center fade-in-up">
            {/* Hero */}
            <div
              className="w-20 h-20 rounded-3xl flex items-center justify-center mb-6"
              style={{
                background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                boxShadow: "0 0 60px rgba(99,102,241,0.4)",
              }}
            >
              <Sparkles size={36} className="text-white" />
            </div>
            <h1 className="text-3xl font-bold gradient-text mb-3">
              Multi-Agent Research System
            </h1>
            <p className="text-slate-500 max-w-md mb-10 leading-relaxed">
              Ask any research question. 5 specialized AI agents will plan, research,
              fact-check, summarize, and generate a full report — powered by Google Gemini.
            </p>

            {/* Example queries */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl w-full">
              {EXAMPLE_QUERIES.map((q) => (
                <button
                  key={q}
                  onClick={() => {
                    setInput(q);
                    textareaRef.current?.focus();
                  }}
                  className="text-left glass rounded-xl px-4 py-3 text-sm text-slate-400 hover:text-slate-200 hover:border-indigo-500/40 transition-all duration-200 hover:scale-[1.01]"
                >
                  <span className="text-indigo-500 mr-2">▸</span>
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}

            {/* Live agent panel while loading */}
            {isLoading && (
              <AgentStatusPanel steps={activeAgentSteps} isLoading={isLoading} />
            )}
          </>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="px-3 sm:px-6 pb-4 sm:pb-6 pt-2 relative">
        {showUploadZone && (
          <div className="mb-4">
            <UploadZone onClose={() => setShowUploadZone(false)} />
          </div>
        )}
        <div
          className="glass-bright rounded-2xl p-2 transition-all duration-200"
          style={{
            boxShadow: isLoading
              ? "0 0 0 1px rgba(99,102,241,0.5), 0 0 30px rgba(99,102,241,0.15)"
              : undefined,
          }}
        >
          <div className="flex items-end gap-2">
            <button
              onClick={() => setShowUploadZone(!showUploadZone)}
              className={`p-2.5 rounded-xl transition-colors mb-0.5 flex-shrink-0 ${showUploadZone ? 'text-indigo-400 bg-indigo-500/10' : 'text-slate-400 hover:text-indigo-400 hover:bg-indigo-500/10'}`}
              title="Upload PDF"
            >
              <Paperclip size={18} />
            </button>
            <textarea
              ref={textareaRef}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Ask a research question… (Shift+Enter for new line)"
              rows={1}
              className="flex-1 bg-transparent border-none outline-none text-slate-200 placeholder-slate-600 resize-none text-sm leading-relaxed py-2.5 px-2 font-outfit"
              style={{ maxHeight: "160px" }}
              disabled={isLoading}
            />
            <button
              onClick={handleSubmit}
              disabled={(input.trim().length < MIN_QUERY_LENGTH && documents.length === 0) || isLoading}
              className="btn-primary flex items-center justify-center gap-2 px-3 sm:px-5 py-2.5 rounded-xl flex-shrink-0"
            >
              {isLoading ? (
                <>
                  <Loader2 size={15} className="animate-spin" />
                  <span className="text-sm hidden sm:inline">Researching…</span>
                </>
              ) : (
                <>
                  <Send size={15} />
                  <span className="text-sm hidden sm:inline">Send</span>
                </>
              )}
            </button>
          </div>

          {/* Hint */}
          <p className="text-xs text-slate-700 px-2 pb-1 mt-1">
            Powered by Google Gemini · LangGraph · 5 Specialized Agents
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;
