# A — Analysis and natural-language sales questions

**Status:** Design specified; implementation planned after the metric registry and source permissions are stable.

## Problem and users

Sales Managers need to ask common operational questions without writing reports or SQL. Answers must be traceable to approved metrics, visible filters and source records.

## Goals

- Translate plain-language questions into a small, approved set of query intents.
- Use a versioned metric/field registry derived from implemented D1, D2, D3 and Highlights definitions.
- Execute only server-owned, permission-aware query definitions.
- Return the answer, time window, filters, currency basis, metric definition version and source links.
- Fail closed when a question cannot be safely mapped or the user lacks permission.

## Non-goals

- Arbitrary text-to-SQL or model-generated SQL execution.
- Raw SQL execution assembled from user text.
- Automatic exploration of arbitrary DocTypes or fields.
- Treating an LLM answer as the source of truth for a business metric.
- Cross-currency totals without a separately approved conversion policy.

## Query architecture

1. Maintain an approved registry with metric ID, description, owner, definition version, source DocTypes/fields, permitted filters, allowed groupings, currency semantics and query implementation.
2. Parse the user's question into a constrained intent object: metric ID, date range, allowed filter values and allowed grouping.
3. Validate the intent against the registry and current user's permissions.
4. Execute the registered server-side query using permission-aware Frappe APIs.
5. Return structured results with metric name, definition version, filters, period, unit/currency, eligible record count and authorized source links.
6. Log the intent ID and execution outcome without logging secrets or unnecessary prompt content.

An optional language model may classify text into the constrained intent schema, but it cannot supply query text, DocType names, field names, SQL, Python or executable expressions. The first release must also support a deterministic template/intent path so analysis works without an external model.

## Initial approved questions

- How many Leads were created in the last 30 days?
- How many active Opportunities exist by stage?
- What is the active pipeline by currency?
- What was invoiced in the last 30 days by invoice currency?
- What customer receipts were received in the last 30 days by receiving-account currency?
- Which positive-balance invoices are overdue?
- Which configured high-value Quotations have no verified interaction in the selected period? This last query is enabled only after H engagement data is implemented.

Each question maps to the exact D1/D2/H metric definition. D3 questions are added only after support source mappings and SLA semantics are accepted.

## Guardrails

- Use a maximum default period of 365 days; wider ranges require a privileged role and explicit confirmation.
- Cap result rows and paginate drill-down data.
- Use allowlisted filters/operators only. Validate date ranges and all link values.
- Check read permission on every source DocType; respect row-level query permissions.
- Monetary results remain grouped by currency.
- No result should reveal the existence or name of a record hidden by Frappe permissions.
- Return "unsupported question" or "data unavailable" when required sources, fields or permissions are missing; never guess an answer.
- No unrestricted export in the first release.

## Acceptance criteria

| ID | Requirement | Validation |
|---|---|---|
| A-AC1 | Natural language maps only to approved metric IDs | Parser contract/property tests |
| A-AC2 | Unknown or ambiguous questions fail safely | Unit + API tests |
| A-AC3 | Query execution comes from a server registry, not generated SQL | Code review/static test ensuring no dynamic SQL entry point |
| A-AC4 | Intent filters and groupings are validated against schema and allowlists | Adversarial input tests |
| A-AC5 | Results match the source metric's calculation and currency basis | Cross-check tests against D1/D2/D3 endpoint fixtures |
| A-AC6 | Frappe row and DocType permissions apply to every source read | Sales User/Manager Bench tests |
| A-AC7 | Results include period, filters, definition version and authorized source links | API schema and Playwright E2E |
| A-AC8 | Default maximum period is 365 days and row limits are enforced | Boundary and pagination tests |
| A-AC9 | Missing permissions/data return unavailable rather than a fabricated zero | API + UI state tests |
| A-AC10 | Deterministic intent templates work with no model configured | Bench/E2E test |

## Dependencies and rollout

D1 and D2 definitions must be reconciled on the target site; D3 and H metrics are registered only after their sources are available. Ship a small deterministic catalog first, then add optional natural-language classification. Keep every supported question listed in the registry and in the product help text.
