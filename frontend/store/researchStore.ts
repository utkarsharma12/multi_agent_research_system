import { create } from "zustand";

export type AgentName = "planner" | "researcher" | "fact_checker" | "summarizer" | "reporter" | "workflow" | string;

export interface AgentStep {
  agent: AgentName;
  status: "pending" | "running" | "done" | "error";
  message?: string;
  startedAt?: number;
  finishedAt?: number;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  agentSteps?: AgentStep[];
  report?: Report;
  createdAt: number;
}

export interface Chat {
  id: number;
  query: string;
  response: string;
  created_at: string;
}

export interface Document {
  id: number;
  title: string;
  source: string;
  created_at: string;
}

export interface Report {
  id?: number;
  title: string;
  executive_summary: string;
  findings: string[];
  key_concepts: string[];
  references: { title: string; url: string; source: string }[];
  conclusion: string;
}

interface ResearchState {
  // Messages in current session
  messages: Message[];
  addMessage: (msg: Message) => void;
  updateLastAssistantMessage: (partial: Partial<Message>) => void;

  // Agent steps for active query
  activeAgentSteps: AgentStep[];
  setActiveAgentSteps: (steps: AgentStep[]) => void;
  updateAgentStep: (agent: AgentName, partial: Partial<AgentStep>) => void;

  // Loading
  isLoading: boolean;
  setIsLoading: (v: boolean) => void;

  // Chat history
  chatHistory: Chat[];
  setChatHistory: (chats: Chat[]) => void;

  // Active chat
  activeChatId: number | null;
  setActiveChatId: (id: number | null) => void;

  // Documents
  documents: Document[];
  setDocuments: (docs: Document[]) => void;
  addDocument: (doc: Document) => void;

  // Reports
  reports: Report[];
  setReports: (reports: Report[]) => void;

  // Sidebar
  sidebarOpen: boolean;
  setSidebarOpen: (v: boolean) => void;

  // Active tab
  activeTab: "chat" | "reports" | "documents";
  setActiveTab: (tab: "chat" | "reports" | "documents") => void;

  // Reset session
  newChat: () => void;
}

const INITIAL_AGENT_STEPS: AgentStep[] = [
  { agent: "planner",     status: "pending" },
  { agent: "researcher",  status: "pending" },
  { agent: "fact_checker",status: "pending" },
  { agent: "summarizer",  status: "pending" },
  { agent: "reporter",    status: "pending" },
];

export const useResearchStore = create<ResearchState>((set) => ({
  messages: [],
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  updateLastAssistantMessage: (partial) =>
    set((s) => {
      const msgs = [...s.messages];
      for (let i = msgs.length - 1; i >= 0; i--) {
        if (msgs[i].role === "assistant") {
          msgs[i] = { ...msgs[i], ...partial };
          break;
        }
      }
      return { messages: msgs };
    }),

  activeAgentSteps: INITIAL_AGENT_STEPS.map((s) => ({ ...s })),
  setActiveAgentSteps: (steps) => set({ activeAgentSteps: steps }),
  updateAgentStep: (agent, partial) =>
    set((s) => ({
      activeAgentSteps: s.activeAgentSteps.map((step) =>
        step.agent === agent ? { ...step, ...partial } : step
      ),
    })),

  isLoading: false,
  setIsLoading: (v) => set({ isLoading: v }),

  chatHistory: [],
  setChatHistory: (chats) => set({ chatHistory: chats }),

  activeChatId: null,
  setActiveChatId: (id) => set({ activeChatId: id }),

  documents: [],
  setDocuments: (docs) => set({ documents: docs }),
  addDocument: (doc) => set((s) => ({ documents: [doc, ...s.documents] })),

  reports: [],
  setReports: (reports) => set({ reports }),

  sidebarOpen: true,
  setSidebarOpen: (v) => set({ sidebarOpen: v }),

  activeTab: "chat",
  setActiveTab: (tab) => set({ activeTab: tab }),

  newChat: () =>
    set({
      messages: [],
      activeAgentSteps: INITIAL_AGENT_STEPS.map((s) => ({ ...s })),
      activeChatId: null,
      isLoading: false,
    }),
}));
