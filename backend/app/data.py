from __future__ import annotations

from app.models import AutomationFlow, Integration, OverviewMetric, WorkflowStep


INTEGRATIONS: list[Integration] = [
    Integration(
        id="supplier-intake",
        name="Supplier Intake Notes",
        category="Source System",
        status="healthy",
        latency_ms=124,
        last_sync="2 minutes ago",
        description="Internal intake notes and document payloads used to start supplier review.",
        capabilities=["document capture", "field extraction", "review handoff"],
    ),
    Integration(
        id="oracle-fusion",
        name="Oracle Fusion Cloud",
        category="Destination System",
        status="healthy",
        latency_ms=182,
        last_sync="8 minutes ago",
        description="Target ERP system for drafting supplier records after human review.",
        capabilities=["REST API", "OAuth", "supplier draft", "data validation"],
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
]


WORKFLOWS: list[AutomationFlow] = [
    AutomationFlow(
        id="supplier-onboarding",
        title="Supplier Onboarding Triage",
        summary="Reviews supplier intake notes, validates missing fields, and drafts an Oracle Fusion supplier record.",
        business_value="Cuts manual review time before supplier records reach the finance queue.",
        systems=["Supplier Intake Notes", "OCI Generative AI", "Oracle Fusion Cloud"],
        steps=[
            WorkflowStep(title="Capture intake payload", owner="API", status="ready"),
            WorkflowStep(title="Extract missing fields", owner="AI service", status="ready"),
            WorkflowStep(title="Route exceptions", owner="Workflow engine", status="review"),
            WorkflowStep(title="Create supplier draft", owner="ERP connector", status="planned"),
        ],
    ),
]


METRICS: list[OverviewMetric] = [
    OverviewMetric(label="Active connectors", value="3", trend="1 source, 1 destination, 1 AI service"),
    OverviewMetric(label="Prototype flows", value="1", trend="focused on supplier onboarding"),
    OverviewMetric(label="Average API latency", value="294 ms", trend="-18 ms this week"),
    OverviewMetric(label="AI prompt quality", value="86%", trend="+9% after refinement"),
]


CAPABILITY_MAP: dict[str, list[str]] = {
    "Supplier onboarding": ["intake triage", "missing field detection", "Oracle Fusion draft"],
    "AI enablement": ["prompt evaluation", "document analysis", "structured recommendations"],
    "Operator workflow": ["responsive dashboard", "guided review", "activity history"],
    "Delivery support": ["setup guidance", "review checklists", "prototype documentation"],
}
