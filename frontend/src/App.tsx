import {
  Activity,
  Bot,
  CheckCircle2,
  ChevronRight,
  CloudCog,
  DatabaseZap,
  FileSearch,
  Gauge,
  GitBranch,
  Loader2,
  Clock3,
  MessageSquareText,
  Network,
  RefreshCw,
  Send,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  analyzeDocument,
  askAssistant,
  evaluatePrompt,
  loadActivity,
  loadIntegrations,
  loadOverview,
  loadWorkflows,
} from "./api";
import architectureMap from "./assets/integration-map.svg";
import type {
  ActivityRecord,
  AssistantResponse,
  AutomationFlow,
  DocumentAnalysis,
  Integration,
  Overview,
  PromptEvaluation,
  Status,
} from "./types";

const samplePrompt =
  "Goal: reduce manual supplier review by validating intake notes before ERP updates. Use Oracle Fusion, a REST API, and AI summarization. Return JSON with risks, assumptions, validation steps, and confidence.";

const sampleDocument =
  "The supplier record is missing tax fields and approval ownership. Finance needs to validate the route before the ERP update. Manual email follow up caused delay, and the team should create documentation for rollback steps.";

const statusLabel: Record<Status, string> = {
  healthy: "Healthy",
  degraded: "Degraded",
  planned: "Planned",
};

export function App() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [workflows, setWorkflows] = useState<AutomationFlow[]>([]);
  const [activityEntries, setActivityEntries] = useState<ActivityRecord[]>([]);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState("supplier-onboarding");
  const [prompt, setPrompt] = useState(samplePrompt);
  const [documentTitle, setDocumentTitle] = useState("Supplier intake notes");
  const [documentText, setDocumentText] = useState(sampleDocument);
  const [assistantResult, setAssistantResult] = useState<AssistantResponse | null>(null);
  const [documentResult, setDocumentResult] = useState<DocumentAnalysis | null>(null);
  const [promptResult, setPromptResult] = useState<PromptEvaluation | null>(null);
  const [loadingAction, setLoadingAction] = useState<string | null>(null);

  useEffect(() => {
    void Promise.all([loadOverview(), loadIntegrations(), loadWorkflows(), loadActivity()]).then(
      ([overviewData, integrationData, workflowData, activityData]) => {
        setOverview(overviewData);
        setIntegrations(integrationData);
        setWorkflows(workflowData);
        setActivityEntries(activityData);
        setSelectedWorkflowId(workflowData[0]?.id ?? "supplier-onboarding");
      },
    );
  }, []);

  const selectedWorkflow = useMemo(
    () => workflows.find((workflow) => workflow.id === selectedWorkflowId) ?? workflows[0],
    [selectedWorkflowId, workflows],
  );

  async function handleAssistantSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoadingAction("assistant");
    const response = await askAssistant(prompt, selectedWorkflowId);
    setAssistantResult(response);
    setLoadingAction(null);
  }

  async function handleDocumentSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoadingAction("document");
    const response = await analyzeDocument(documentTitle, documentText);
    setDocumentResult(response);
    setLoadingAction(null);
  }

  async function handlePromptEvaluate() {
    setLoadingAction("prompt");
    const response = await evaluatePrompt(prompt);
    setPromptResult(response);
    setLoadingAction(null);
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-lockup">
          <div className="brand-mark">
            <CloudCog size={24} aria-hidden="true" />
          </div>
          <div>
            <p className="eyebrow">Innovation Workspace</p>
            <h1>Cloud AI Integration Console</h1>
          </div>
        </div>
        <nav className="nav-list" aria-label="Workspace sections">
          <a href="#overview">
            <Gauge size={18} aria-hidden="true" />
            Overview
          </a>
          <a href="#connectors">
            <Network size={18} aria-hidden="true" />
            Connectors
          </a>
          <a href="#assistant">
            <Bot size={18} aria-hidden="true" />
            AI Planner
          </a>
          <a href="#documents">
            <FileSearch size={18} aria-hidden="true" />
            Documents
          </a>
        </nav>
        <div className="sidebar-status">
          <Activity size={18} aria-hidden="true" />
          <span>API-first prototype</span>
        </div>
      </aside>

      <main>
        <section className="workspace-header" id="overview">
          <div>
            <p className="eyebrow">Cloud integration lab</p>
            <h2>AI-enabled workflow prototyping for enterprise systems</h2>
          </div>
          <div className="header-actions">
            <button className="icon-button" type="button" title="Refresh workspace data">
              <RefreshCw size={18} aria-hidden="true" />
            </button>
            <button className="primary-button" type="button" onClick={handlePromptEvaluate}>
              {loadingAction === "prompt" ? (
                <Loader2 className="spin" size={18} aria-hidden="true" />
              ) : (
                <Sparkles size={18} aria-hidden="true" />
              )}
              Evaluate prompt
            </button>
          </div>
        </section>

        <section className="metric-grid" aria-label="Workspace metrics">
          {(overview?.metrics ?? []).map((metric) => (
            <article className="metric-card" key={metric.label}>
              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
              <small>{metric.trend}</small>
            </article>
          ))}
        </section>

        <section className="two-column">
          <div className="panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Architecture view</p>
                <h3>Service path</h3>
              </div>
              <ShieldCheck size={22} aria-hidden="true" />
            </div>
            <img
              className="architecture-map"
              src={architectureMap}
              alt="Cloud integration map connecting enterprise applications, APIs, AI services, and an operations console."
            />
          </div>

          <div className="panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Capability map</p>
                <h3>Delivery coverage</h3>
              </div>
              <DatabaseZap size={22} aria-hidden="true" />
            </div>
            <div className="capability-list">
              {Object.entries(overview?.capability_map ?? {}).map(([group, items]) => (
                <article className="capability-item" key={group}>
                  <h4>{group}</h4>
                  <p>{items.join(" / ")}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="panel" id="connectors">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Connectors</p>
              <h3>API and platform readiness</h3>
            </div>
            <GitBranch size={22} aria-hidden="true" />
          </div>
          <div className="connector-grid">
            {integrations.map((integration) => (
              <article className="connector-card" key={integration.id}>
                <div className="connector-topline">
                  <div>
                    <h4>{integration.name}</h4>
                    <p>{integration.category}</p>
                  </div>
                  <span className={`status-pill ${integration.status}`}>
                    {statusLabel[integration.status]}
                  </span>
                </div>
                <p>{integration.description}</p>
                <div className="connector-meta">
                  <span>{integration.latency_ms || "-"} ms</span>
                  <span>{integration.last_sync}</span>
                </div>
                <div className="tag-row">
                  {integration.capabilities.map((capability) => (
                    <span key={capability}>{capability}</span>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="two-column aligned-start">
          <div className="panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Prototype flows</p>
                <h3>Automation candidates</h3>
              </div>
              <CheckCircle2 size={22} aria-hidden="true" />
            </div>
            <div className="workflow-list">
              {workflows.map((workflow) => (
                <button
                  className={`workflow-row ${workflow.id === selectedWorkflowId ? "selected" : ""}`}
                  key={workflow.id}
                  onClick={() => setSelectedWorkflowId(workflow.id)}
                  type="button"
                >
                  <span>
                    <strong>{workflow.title}</strong>
                    <small>{workflow.business_value}</small>
                  </span>
                  <ChevronRight size={18} aria-hidden="true" />
                </button>
              ))}
            </div>
          </div>

          <div className="panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Selected workflow</p>
                <h3>{selectedWorkflow?.title ?? "Workflow"}</h3>
              </div>
              <Network size={22} aria-hidden="true" />
            </div>
            <p className="muted-copy">{selectedWorkflow?.summary}</p>
            <div className="step-list">
              {selectedWorkflow?.steps.map((step, index) => (
                <article className="step-row" key={step.title}>
                  <span>{index + 1}</span>
                  <div>
                    <strong>{step.title}</strong>
                    <small>
                      {step.owner} / {step.status}
                    </small>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="panel" id="activity">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Activity</p>
              <h3>Recent persisted runs</h3>
            </div>
            <Clock3 size={22} aria-hidden="true" />
          </div>
          <div className="activity-feed">
            {activityEntries.map((entry) => (
              <article className="activity-row" key={entry.id}>
                <div className="activity-main">
                  <div className={`activity-kind ${entry.kind}`}>{entry.kind}</div>
                  <div>
                    <strong>{entry.title}</strong>
                    <p>{entry.summary}</p>
                  </div>
                </div>
                <small>{entry.created_at}</small>
              </article>
            ))}
          </div>
        </section>

        <section className="two-column aligned-start">
          <form className="panel form-panel" id="assistant" onSubmit={handleAssistantSubmit}>
            <div className="section-heading">
              <div>
                <p className="eyebrow">AI planner</p>
                <h3>Prompt and workflow review</h3>
              </div>
              <MessageSquareText size={22} aria-hidden="true" />
            </div>
            <label htmlFor="prompt">Prompt</label>
            <textarea id="prompt" value={prompt} onChange={(event) => setPrompt(event.target.value)} />
            <div className="form-actions">
              <select
                aria-label="Select workflow"
                value={selectedWorkflowId}
                onChange={(event) => setSelectedWorkflowId(event.target.value)}
              >
                {workflows.map((workflow) => (
                  <option key={workflow.id} value={workflow.id}>
                    {workflow.title}
                  </option>
                ))}
              </select>
              <button className="primary-button" type="submit">
                {loadingAction === "assistant" ? (
                  <Loader2 className="spin" size={18} aria-hidden="true" />
                ) : (
                  <Send size={18} aria-hidden="true" />
                )}
                Send
              </button>
            </div>
            {promptResult && (
              <output className="result-block">
                <strong>Prompt score: {promptResult.score}</strong>
                <span>{promptResult.improved_prompt}</span>
              </output>
            )}
          </form>

          <div className="panel result-panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Planner output</p>
                <h3>Review pack</h3>
              </div>
              <Bot size={22} aria-hidden="true" />
            </div>
            {assistantResult ? (
              <ResultList
                lead={assistantResult.answer}
                groups={[
                  ["Suggested steps", assistantResult.suggested_steps],
                  ["Quality checks", assistantResult.quality_checks],
                  ["Assumptions", assistantResult.assumptions],
                ]}
              />
            ) : (
              <EmptyState text="Submit a prompt to generate a structured integration review." />
            )}
          </div>
        </section>

        <section className="two-column aligned-start">
          <form className="panel form-panel" id="documents" onSubmit={handleDocumentSubmit}>
            <div className="section-heading">
              <div>
                <p className="eyebrow">Document triage</p>
                <h3>Notes to actions</h3>
              </div>
              <FileSearch size={22} aria-hidden="true" />
            </div>
            <label htmlFor="document-title">Title</label>
            <input
              id="document-title"
              value={documentTitle}
              onChange={(event) => setDocumentTitle(event.target.value)}
            />
            <label htmlFor="document-text">Content</label>
            <textarea
              id="document-text"
              value={documentText}
              onChange={(event) => setDocumentText(event.target.value)}
            />
            <button className="primary-button" type="submit">
              {loadingAction === "document" ? (
                <Loader2 className="spin" size={18} aria-hidden="true" />
              ) : (
                <Sparkles size={18} aria-hidden="true" />
              )}
              Analyze
            </button>
          </form>

          <div className="panel result-panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Analysis output</p>
                <h3>Extracted structure</h3>
              </div>
              <Activity size={22} aria-hidden="true" />
            </div>
            {documentResult ? (
              <ResultList
                lead={documentResult.summary}
                groups={[
                  ["Detected systems", documentResult.detected_systems],
                  ["Action items", documentResult.action_items],
                  ["Risks", documentResult.risks],
                  ["Automation opportunities", documentResult.automation_opportunities],
                ]}
              />
            ) : (
              <EmptyState text="Analyze notes to extract systems, risks, and automation opportunities." />
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

function ResultList({ lead, groups }: { lead: string; groups: [string, string[]][] }) {
  return (
    <div className="result-list">
      <p>{lead}</p>
      {groups.map(([title, items]) => (
        <section key={title}>
          <h4>{title}</h4>
          <ul>
            {items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return (
    <div className="empty-state">
      <Sparkles size={24} aria-hidden="true" />
      <p>{text}</p>
    </div>
  );
}
