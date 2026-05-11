from __future__ import annotations

from app.models import AutomationFlow, Integration, OverviewMetric, WorkflowStep


INTEGRATIONS: list[Integration] = [
    Integration(
        id="oracle-fusion",
        name="Oracle Fusion Cloud",
        category="Enterprise Applications",
        status="healthy",
        latency_ms=182,
        last_sync="8 minutes ago",
        description="REST connector for procurement, finance, and supplier workflows.",
        capabilities=["REST API", "OAuth", "event polling", "data validation"],
    ),
    Integration(
        id="jde",
        name="JD Edwards",
        category="Enterprise Applications",
        status="degraded",
        latency_ms=441,
        last_sync="23 minutes ago",
        description="Legacy ERP bridge for order, inventory, and customer records.",
        capabilities=["batch import", "SQL staging", "change detection"],
    ),
    Integration(
        id="oci-genai",
        name="OCI Generative AI",
        category="AI Services",
        status="healthy",
        latency_ms=260,
        last_sync="live",
        description="Prompt endpoint used for summarization, classification, and guided planning.",
        capabilities=["LLM prompts", "document summaries", "structured extraction"],
    ),
    Integration(
        id="digital-assistant",
        name="Oracle Digital Assistant",
        category="Conversational AI",
        status="planned",
        latency_ms=0,
        last_sync="prototype queued",
        description="Chat channel concept for guided enterprise self-service flows.",
        capabilities=["intents", "dialog flows", "handoff actions"],
    ),
]


WORKFLOWS: list[AutomationFlow] = [
    AutomationFlow(
        id="supplier-onboarding",
        title="Supplier Onboarding Triage",
        summary="Classifies supplier intake notes, validates missing fields, and drafts follow-up tasks.",
        business_value="Cuts manual review time before supplier records reach the finance queue.",
        systems=["Oracle Fusion Cloud", "OCI Generative AI", "Document Store"],
        steps=[
            WorkflowStep(title="Capture intake payload", owner="API", status="ready"),
            WorkflowStep(title="Extract missing fields", owner="AI service", status="ready"),
            WorkflowStep(title="Route exceptions", owner="Workflow engine", status="review"),
            WorkflowStep(title="Create supplier draft", owner="ERP connector", status="planned"),
        ],
    ),
    AutomationFlow(
        id="order-risk-review",
        title="Order Risk Review",
        summary="Combines ERP order signals with natural language notes to highlight risk factors.",
        business_value="Helps consultants find orders that need human review before downstream impact.",
        systems=["JD Edwards", "Analytics Warehouse", "OCI Generative AI"],
        steps=[
            WorkflowStep(title="Sync candidate orders", owner="Integration job", status="ready"),
            WorkflowStep(title="Score note urgency", owner="AI service", status="ready"),
            WorkflowStep(title="Build evidence summary", owner="API", status="review"),
            WorkflowStep(title="Publish dashboard alert", owner="Frontend", status="ready"),
        ],
    ),
    AutomationFlow(
        id="knowledge-base-draft",
        title="Knowledge Base Drafting",
        summary="Turns implementation notes into setup guides, caveats, and searchable snippets.",
        business_value="Improves handover quality between research, consultants, and customer teams.",
        systems=["Document Store", "OCI Generative AI", "Support Portal"],
        steps=[
            WorkflowStep(title="Upload notes", owner="Consultant", status="ready"),
            WorkflowStep(title="Create structured outline", owner="AI service", status="ready"),
            WorkflowStep(title="Review generated guidance", owner="Architect", status="review"),
            WorkflowStep(title="Publish approved article", owner="Support team", status="planned"),
        ],
    ),
]


METRICS: list[OverviewMetric] = [
    OverviewMetric(label="Active connectors", value="4", trend="+1 planned"),
    OverviewMetric(label="Prototype flows", value="3", trend="2 ready for review"),
    OverviewMetric(label="Average API latency", value="294 ms", trend="-18 ms this week"),
    OverviewMetric(label="AI prompt quality", value="86%", trend="+9% after refinement"),
]


CAPABILITY_MAP: dict[str, list[str]] = {
    "Cloud integration": ["REST orchestration", "connector monitoring", "workflow staging"],
    "AI enablement": ["prompt evaluation", "document analysis", "structured recommendations"],
    "Front-end delivery": ["responsive dashboard", "guided assistant", "operator-friendly UX"],
    "Delivery support": ["setup guidance", "review checklists", "prototype documentation"],
}

