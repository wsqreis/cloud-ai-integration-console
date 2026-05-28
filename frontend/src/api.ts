import {
  activity,
  auditTrail,
  assistantResponse,
  documentAnalysis,
  integrations,
  overview,
  promptHistory,
  promptEvaluation,
  reviews,
  workflows,
} from "./seedData";
import type {
  AssistantResponse,
  ActivityRecord,
  AuditTrailRecord,
  AutomationFlow,
  DocumentAnalysis,
  Integration,
  Overview,
  PromptHistoryRecord,
  PromptEvaluation,
  ReviewRecord,
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

async function withFallback<T>(requester: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await requester();
  } catch {
    return fallback;
  }
}

export function loadOverview(): Promise<Overview> {
  return withFallback(() => request<Overview>("/api/overview"), overview);
}

export function loadIntegrations(): Promise<Integration[]> {
  return withFallback(() => request<Integration[]>("/api/integrations"), integrations);
}

export function loadWorkflows(): Promise<AutomationFlow[]> {
  return withFallback(() => request<AutomationFlow[]>("/api/workflows"), workflows);
}

export function loadActivity(): Promise<ActivityRecord[]> {
  return withFallback(() => request<ActivityRecord[]>("/api/activity"), activity);
}

export function loadAuditTrail(): Promise<AuditTrailRecord[]> {
  return withFallback(() => request<AuditTrailRecord[]>("/api/audit-trail"), auditTrail);
}

export function loadPromptHistory(): Promise<PromptHistoryRecord[]> {
  return withFallback(() => request<PromptHistoryRecord[]>("/api/prompt-history"), promptHistory);
}

export function loadReviews(): Promise<ReviewRecord[]> {
  return withFallback(() => request<ReviewRecord[]>("/api/reviews"), reviews);
}

export function askAssistant(prompt: string, workflowId: string): Promise<AssistantResponse> {
  return withFallback(
    () =>
      request<AssistantResponse>("/api/assistant", {
        method: "POST",
        body: JSON.stringify({ prompt, workflow_id: workflowId }),
      }),
    assistantResponse,
  );
}

export function approveReview(reviewId: number, reviewer = "local-operator"): Promise<ReviewRecord> {
  return request<ReviewRecord>(`/api/reviews/${reviewId}/approve`, {
    method: "POST",
    body: JSON.stringify({ reviewer }),
  });
}

export function rejectReview(reviewId: number, reviewer = "local-operator"): Promise<ReviewRecord> {
  return request<ReviewRecord>(`/api/reviews/${reviewId}/reject`, {
    method: "POST",
    body: JSON.stringify({ reviewer }),
  });
}

export function publishReview(reviewId: number, publisher = "local-operator"): Promise<ReviewRecord> {
  return request<ReviewRecord>(`/api/reviews/${reviewId}/publish`, {
    method: "POST",
    body: JSON.stringify({ publisher }),
  });
}

export function analyzeDocument(title: string, content: string): Promise<DocumentAnalysis> {
  return withFallback(
    () =>
      request<DocumentAnalysis>("/api/documents/analyze", {
        method: "POST",
        body: JSON.stringify({ title, content }),
      }),
    documentAnalysis,
  );
}

export function evaluatePrompt(prompt: string): Promise<PromptEvaluation> {
  return withFallback(
    () =>
      request<PromptEvaluation>("/api/prompts/evaluate", {
        method: "POST",
        body: JSON.stringify({ prompt }),
      }),
    promptEvaluation,
  );
}
