import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 300000, // 5 min — agents can take time and rate limit backoff can add delay
});

// ─── Chat ───────────────────────────────────────────────────────────────────

export interface ChatRequest {
  query: string;
}

export interface AgentStepResponse {
  agent: string;
  status: string;
  message?: string;
}

export interface ReportResponse {
  title: string;
  executive_summary: string;
  findings: string[];
  key_concepts: string[];
  references: { title: string; url: string; source: string }[];
  conclusion: string;
}

export interface ChatResponse {
  id: number;
  query: string;
  response: string;
  agent_steps: AgentStepResponse[];
  report: ReportResponse;
  created_at: string;
}

export const sendChat = async (query: string): Promise<ChatResponse> => {
  const { data } = await api.post<ChatResponse>("/api/chat", { query });
  return data;
};

export const getApiErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0];
      if (first && typeof first === "object" && "msg" in first) {
        return String(first.msg);
      }
    }

    return error.message;
  }

  return error instanceof Error ? error.message : "Something went wrong. Is the backend running?";
};

export const getChatHistory = async (): Promise<ChatResponse[]> => {
  const { data } = await api.get<ChatResponse[]>("/api/chat/history");
  return data;
};

export const getChatById = async (id: number): Promise<ChatResponse> => {
  const { data } = await api.get<ChatResponse>(`/api/chat/${id}`);
  return data;
};

// ─── Documents ──────────────────────────────────────────────────────────────

export interface DocumentResponse {
  id: number;
  title: string;
  source: string;
  file_path: string;
  created_at: string;
}

export const uploadDocument = async (file: File): Promise<DocumentResponse> => {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<DocumentResponse>(
    "/api/documents/upload",
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return data;
};

export const getDocuments = async (): Promise<DocumentResponse[]> => {
  const { data } = await api.get<DocumentResponse[]>("/api/documents");
  return data;
};

export const deleteDocument = async (id: number): Promise<void> => {
  await api.delete(`/api/documents/${id}`);
};

// ─── Reports ────────────────────────────────────────────────────────────────

export interface ReportListItem {
  id: number;
  title: string;
  created_at: string;
}

export const getReports = async (): Promise<ReportListItem[]> => {
  const { data } = await api.get<ReportListItem[]>("/api/reports");
  return data;
};

export const getReportById = async (id: number): Promise<ReportResponse & { id: number; created_at: string }> => {
  const { data } = await api.get(`/api/reports/${id}`);
  return data;
};

export const deleteReport = async (id: number): Promise<void> => {
  await api.delete(`/api/reports/${id}`);
};

// ─── Health ──────────────────────────────────────────────────────────────────

export const checkHealth = async (): Promise<boolean> => {
  try {
    await api.get("/");
    return true;
  } catch {
    return false;
  }
};

export default api;
