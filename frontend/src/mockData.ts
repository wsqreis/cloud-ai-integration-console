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
    { label: "Active connectors", value: "4", trend: "+1 planned" },
    { label: "Prototype flows", value: "3", trend: "2 ready for review" },
    { label: "Average API latency", value: "294 ms", trend: "-18 ms this week" },
    { label: "AI prompt quality", value: "86%", trend: "+9% after refinement" },
  ],
  capability_map: {
    "Cloud integration": ["REST orchestration", "connector monitoring", "workflow staging"],
    "AI enablement": ["prompt evaluation", "document analysis", "structured recommendations"],
    "Front-end delivery": ["responsive dashboard", "guided assistant", "operator-friendly UX"],
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
    id: "oracle-fusion",
    name: "Oracle Fusion Cloud",
    category: "Enterprise Applications",
    status: "healthy",
    latency_ms: 182,
    last_sync: "8 minutes ago",
    description: "REST connector for procurement, finance, and supplier workflows.",
    capabilities: ["REST API", "OAuth", "event polling", "data validation"],
  },
  {
    id: "jde",
    name: "JD Edwards",
    category: "Enterprise Applications",
    status: "degraded",
    latency_ms: 441,
    last_sync: "23 minutes ago",
    description: "Legacy ERP bridge for order, inventory, and customer records.",
    capabilities: ["batch import", "SQL staging", "change detection"],
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
  {
    id: "digital-assistant",
    name: "Oracle Digital Assistant",
    category: "Conversational AI",
    status: "planned",
    latency_ms: 0,
    last_sync: "prototype queued",
    description: "Chat channel concept for guided enterprise self-service flows.",
    capabilities: ["intents", "dialog flows", "handoff actions"],
  },
];

export const workflows: AutomationFlow[] = [
  {
    id: "supplier-onboarding",
    title: "Supplier Onboarding Triage",
    summary: "Classifies supplier intake notes, validates missing fields, and drafts follow-up tasks.",
    business_value: "Cuts manual review time before supplier records reach the finance queue.",
    systems: ["Oracle Fusion Cloud", "OCI Generative AI", "Document Store"],
    steps: [
      { title: "Capture intake payload", owner: "API", status: "ready" },
      { title: "Extract missing fields", owner: "AI service", status: "ready" },
      { title: "Route exceptions", owner: "Workflow engine", status: "review" },
      { title: "Create supplier draft", owner: "ERP connector", status: "planned" },
    ],
  },
  {
    id: "order-risk-review",
    title: "Order Risk Review",
    summary: "Combines ERP order signals with natural language notes to highlight risk factors.",
    business_value: "Helps consultants find orders that need human review before downstream impact.",
    systems: ["JD Edwards", "Analytics Warehouse", "OCI Generative AI"],
    steps: [
      { title: "Sync candidate orders", owner: "Integration job", status: "ready" },
      { title: "Score note urgency", owner: "AI service", status: "ready" },
      { title: "Build evidence summary", owner: "API", status: "review" },
      { title: "Publish dashboard alert", owner: "Frontend", status: "ready" },
    ],
  },
  {
    id: "knowledge-base-draft",
    title: "Knowledge Base Drafting",
    summary: "Turns implementation notes into setup guides, caveats, and searchable snippets.",
    business_value: "Improves handover quality between research, consultants, and customer teams.",
    systems: ["Document Store", "OCI Generative AI", "Support Portal"],
    steps: [
      { title: "Upload notes", owner: "Consultant", status: "ready" },
      { title: "Create structured outline", owner: "AI service", status: "ready" },
      { title: "Review generated guidance", owner: "Architect", status: "review" },
      { title: "Publish approved article", owner: "Support team", status: "planned" },
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
