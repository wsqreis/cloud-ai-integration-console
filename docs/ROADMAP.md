# Roadmap

This is the live plan for moving the console from prototype to a client-pilot-ready internal product.

## Current status

- Done: Primary use case and ICP defined
- Done: MVP scope frozen
- Done: OpenAI SDK integration and local CLI
- Done: SQLite persistence for activity history
- Done: Basic observability and request metrics
- Done: Activity history API and dashboard feed
- Done: Integration tests for persistence and activity
- Deferred: authentication and access control

## Phase 1 - Base of product

- [x] Define the primary use case and ICP: 1 flow, 1 source system, 1 destination system
- [x] Freeze the MVP scope: what is in and what is out
- [ ] Add basic authentication and role-based access
- [x] Add persistence: database for workflows, analyses, prompts, and decisions

## Phase 2 - Reliability

- [ ] Replace mocks/static data with real integrations or clear adapters
- [x] Implement structured logs, metrics, and tracing
- [ ] Standardize backend errors, retries, and timeouts
- [x] Cover critical flows with integration tests

## Phase 3 - Business Value

- [ ] Turn the AI planner into a useful flow: suggestion, human review, approval
- [ ] Keep history of responses and prompt versions
- [ ] Add audit trail: who asked, who approved, what was published
- [ ] Add operational screens: status, failures, pending items, review queue

## Phase 4 - Ready to Pilot

- [ ] Harden security: CORS, secrets, rate limits, resource-level authorization
- [ ] Separate deploy environments: dev / stage / prod
- [ ] Document usage for the internal team and pilot customer
- [ ] Measure success: time saved, approval rate, failures, adoption

## Suggested order

1. Persistence + primary flow
2. Observability + real integrations
3. Audit trail + security + pilot readiness

## Notes

- Authentication is intentionally deferred for now so we can keep validating value in a closed internal environment.
- The active MVP focus is supplier onboarding triage from supplier intake notes into Oracle Fusion Cloud.
- The MVP scope is intentionally frozen around that path so we can avoid scope creep.
- Request IDs and basic metrics are now available through the API for lightweight observability.
- The checklist should stay updated as work lands so it remains the source of truth for the project plan.
