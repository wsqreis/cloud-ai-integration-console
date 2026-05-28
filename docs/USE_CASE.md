# Primary Use Case

## ICP

Internal operations consultants and integration architects at ERP-focused services teams who need to validate supplier onboarding changes before they reach Oracle Fusion.

## Primary Flow

Supplier intake notes are reviewed, missing fields are flagged, and the result is drafted into Oracle Fusion for human approval.

- Source system: supplier intake notes / document store
- Destination system: Oracle Fusion Cloud
- Supporting AI service: OCI Generative AI

## Why This Is the MVP

- It has a clear business owner: finance and supplier operations.
- It has a clear handoff: intake notes to Oracle Fusion supplier draft.
- It is narrow enough to validate quickly with real users.
- It produces a visible review artifact for the dashboard and history feed.

## In Scope

- Capture supplier intake notes
- Flag missing or inconsistent fields
- Draft review actions and follow-up steps
- Persist planner output and review history
- Show recent runs in the activity feed

## Out of Scope

- Multi-tenant authentication and authorization
- Other ERP scenarios such as order-risk review
- Knowledge-base article drafting
- Support for additional source and destination systems

