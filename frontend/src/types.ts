export type Status = "healthy" | "degraded" | "planned";

export interface Integration {
  id: string;
  name: string;
  category: string;
  status: Status;
  latency_ms: number;
  last_sync: string;
  description: string;
  capabilities: string[];
}

export interface WorkflowStep {
  title: string;
  owner: string;
  status: "ready" | "review" | "blocked" | "planned";
}

export interface AutomationFlow {
  id: string;
  title: string;
  summary: string;
  business_value: string;
  systems: string[];
  steps: WorkflowStep[];
}

export interface OverviewMetric {
  label: string;
  value: string;
  trend: string;
}

export interface Overview {
  metrics: OverviewMetric[];
  capability_map: Record<string, string[]>;
  recommended_next_actions: string[];
}

export interface AssistantResponse {
  answer: string;
  assumptions: string[];
  suggested_steps: string[];
  quality_checks: string[];
  confidence: "low" | "medium" | "high";
  review_id?: number | null;
  review_status?: "pending" | "approved" | "rejected";
}

export interface DocumentAnalysis {
  summary: string;
  detected_systems: string[];
  action_items: string[];
  risks: string[];
  automation_opportunities: string[];
}

export interface PromptEvaluation {
  score: number;
  strengths: string[];
  gaps: string[];
  improved_prompt: string;
}

export interface PromptHistoryRecord {
  id: number;
  kind: "assistant" | "document" | "prompt";
  title: string;
  workflow_id?: string | null;
  version: number;
  prompt: string;
  response_summary: string;
  response_payload: unknown;
  created_at: string;
}

export interface ReviewRecord {
  id: number;
  workflow_id?: string | null;
  workflow_title: string;
  prompt: string;
  status: "pending" | "approved" | "rejected";
  reviewer?: string | null;
  decision_note?: string | null;
  response: AssistantResponse;
  created_at: string;
  reviewed_at?: string | null;
}

export interface ActivityRecord {
  id: number;
  kind: "assistant" | "document" | "prompt" | "review";
  title: string;
  summary: string;
  workflow_id?: string | null;
  created_at: string;
}
