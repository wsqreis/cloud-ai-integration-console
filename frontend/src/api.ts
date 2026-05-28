import {
  activity,
  assistantResponse,
  documentAnalysis,
  integrations,
  overview,
  promptEvaluation,
  workflows,
} from "./seedData";
import type {
  AssistantResponse,
  ActivityRecord,
  AutomationFlow,
  DocumentAnalysis,
  Integration,
  Overview,
  PromptEvaluation,
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
