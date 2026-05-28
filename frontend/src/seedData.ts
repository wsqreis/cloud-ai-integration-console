import type {
  ActivityRecord,
  AssistantResponse,
  AutomationFlow,
  DocumentAnalysis,
  Integration,
  Overview,
  PromptEvaluation,
} from "./types";

export const overview: Overview = {
  metrics: [
    { label: "Active connectors", value: "3", trend: "1 source, 1 destination, 1 AI service" },
    { label: "Prototype flows", value: "1", trend: "focused on supplier onboarding" },
    { label: "Average API latency", value: "294 ms", trend: "-18 ms this week" },
    { label: "AI prompt quality", value: "86%", trend: "+9% after refinement" },
  ],
  capability_map: {
    "Supplier onboarding": ["intake triage", "missing field detection", "Oracle Fusion draft"],
    "AI enablement": ["prompt evaluation", "document analysis", "structured recommendations"],
    "Operator workflow": ["responsive dashboard", "guided review", "activity history"],
    "Delivery support": ["setup guidance", "review checklists", "prototype documentation"],
  },
  recommended_next_actions: [
    "Validate degraded connector retry behavior.",
    "Review AI-generated actions before publishing workflow changes.",
    "Add customer-specific mappings after the prototype is approved.",
  ],
};

export const integrations: Integration[] = [
  {
    id: "supplier-intake",
    name: "Supplier Intake Notes",
    category: "Source System",
    status: "healthy",
    latency_ms: 124,
    last_sync: "2 minutes ago",
    description: "Internal intake notes and document payloads used to start supplier review.",
    capabilities: ["document capture", "field extraction", "review handoff"],
  },
  {
    id: "oracle-fusion",
    name: "Oracle Fusion Cloud",
    category: "Destination System",
    status: "healthy",
    latency_ms: 182,
    last_sync: "8 minutes ago",
    description: "Target ERP system for drafting supplier records after human review.",
    capabilities: ["REST API", "OAuth", "supplier draft", "data validation"],
  },
  {
    id: "oci-genai",
    name: "OCI Generative AI",
    category: "AI Services",
    status: "healthy",
    latency_ms: 260,
    last_sync: "live",
    description: "Prompt endpoint used for summarization, classification, and guided planning.",
    capabilities: ["LLM prompts", "document summaries", "structured extraction"],
  },
];

export const workflows: AutomationFlow[] = [
  {
    id: "supplier-onboarding",
    title: "Supplier Onboarding Triage",
    summary: "Reviews supplier intake notes, validates missing fields, and drafts an Oracle Fusion supplier record.",
    business_value: "Cuts manual review time before supplier records reach the finance queue.",
    systems: ["Supplier Intake Notes", "OCI Generative AI", "Oracle Fusion Cloud"],
    steps: [
      { title: "Capture intake payload", owner: "API", status: "ready" },
      { title: "Extract missing fields", owner: "AI service", status: "ready" },
      { title: "Route exceptions", owner: "Workflow engine", status: "review" },
      { title: "Create supplier draft", owner: "ERP connector", status: "planned" },
    ],
  },
];

export const assistantResponse: AssistantResponse = {
  answer:
    "Start with a narrow proof of concept that proves the data path, AI review step, and operational handoff before expanding scope.",
  assumptions: [
    "The prototype should run without production access.",
    "AI-generated recommendations require review before customer-facing use.",
  ],
  suggested_steps: [
    "Define the source event, target system, and success criteria.",
    "Map required fields and identify missing data handling.",
    "Prototype the REST request and mock error responses.",
    "Document setup, rollback, and support ownership.",
  ],
  quality_checks: [
    "Does the prompt name the business outcome?",
    "Are source and target systems explicit?",
    "Is there a fallback when the AI response is incomplete?",
  ],
  confidence: "medium",
};

export const documentAnalysis: DocumentAnalysis = {
  summary:
    "The note references Oracle Fusion, REST API, and OCI Generative AI. It is ready for action and risk triage.",
  detected_systems: ["Oracle Fusion", "REST API", "OCI Generative AI"],
  action_items: ["Confirm required fields and owner before implementation."],
  risks: ["Missing information may block automation."],
  automation_opportunities: ["Use structured extraction to detect missing or inconsistent fields."],
};

export const promptEvaluation: PromptEvaluation = {
  score: 72,
  strengths: ["Names the technical context.", "Asks for review criteria."],
  gaps: ["Specify the expected response format."],
  improved_prompt:
    "Given the business outcome, source system, target system, constraints, and sample data, produce a structured recommendation with assumptions, risks, validation steps, and a clear next action list.",
};

export const activity: ActivityRecord[] = [
  {
    id: 3,
    kind: "prompt",
    title: "Prompt evaluation",
    summary: "Score 90/100",
    created_at: "just now",
  },
  {
    id: 2,
    kind: "document",
    title: "Supplier intake notes",
    summary: "The note references Oracle Fusion and REST APIs.",
    created_at: "5 minutes ago",
  },
  {
    id: 1,
    kind: "assistant",
    title: "Supplier Onboarding Triage",
    summary: "Start with a narrow proof of concept that proves the data path.",
    workflow_id: "supplier-onboarding",
    created_at: "8 minutes ago",
  },
];
