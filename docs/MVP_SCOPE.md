# MVP Scope

## What Is In

- Supplier intake notes as the source of truth
- Oracle Fusion Cloud as the destination system
- OCI Generative AI for prompt review, document analysis, and suggested actions
- Activity history for assistant runs, document triage, and prompt evaluations
- A dashboard that shows the latest runs, connector readiness, and workflow status

## What Is Out

- Authentication and role-based access control
- Additional ERP flows such as order-risk review
- Knowledge-base article drafting
- Multi-tenant support
- Human approval workflow automation beyond review guidance
- Additional source or destination systems beyond the MVP path

## Decision Rule

If a feature does not directly help validate supplier onboarding from intake notes into Oracle Fusion, it is out of scope for the MVP.

## Acceptance Criteria

- The product can be demoed end to end with one source, one destination, and one AI-assisted review path
- The dashboard and history feed explain what happened during each run
- The scope fits a small internal pilot without expanding to multiple business lines

