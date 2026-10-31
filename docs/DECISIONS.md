# Decision Register

This register captures durable product and engineering decisions that affect future work. Add a new entry when a decision changes scope, data semantics, security, architecture, compatibility or delivery policy.

**Register created:** 2026-10-31

> **Historical note:** The entries below were reconstructed from the repository's existing README, implementation plan, specifications, source layout and CI configuration. The original decision dates and discussion records were not preserved. They are recorded here as the current repository decisions, not as proof that a formal ADR process existed at the time.

## ADR-001 — CRM Signals is an ERPNext extension, not a replacement CRM

- **Status:** Accepted
- **Recorded:** 2026-10-31
- **Decision:** Keep this project focused on signal capture, event-generated signals, Desk notifications, scheduled digests and the explicitly planned S.A.H.D.E.V. dashboard slices. Lead/contact management, full sales-pipeline ownership, marketing automation, campaigns, omnichannel inbox and full CRM analytics are outside the current extension scope unless separately approved.
- **Rationale:** Avoid duplicating ERPNext CRM capabilities and keep the app's responsibilities bounded.
- **Sources:** [README](../README.md), [Implementation Plan](../IMPLEMENTATION_PLAN.md).

## ADR-002 — Build product capabilities as independently verifiable vertical slices

- **Status:** Accepted
- **Recorded:** 2026-10-31
- **Decision:** Each roadmap slice must have a documented data contract, permission behavior, user experience, tests, operational configuration and documentation before it is treated as complete.
- **Rationale:** A visible dashboard card is not evidence that the underlying metric is valid, permission-safe or deployable.
- **Sources:** [S.A.H.D.E.V. roadmap](SAHDEV_VERTICAL_SLICES.md), [Specifications guide](../specs/README.md).

## ADR-003 — Dashboard and billing reads must respect Frappe permissions

- **Status:** Accepted
- **Recorded:** 2026-10-31
- **Decision:** Use permission-aware Frappe list APIs for dashboard data. For D2 billing metrics, do not use `frappe.get_all`, raw SQL or `ignore_permissions`; check read access independently for Sales Invoice and Payment Entry. An inaccessible or unsupported source must be represented as unavailable, not as a successful zero.
- **Rationale:** A dashboard must not expose financial or CRM data that the requesting user is not allowed to read, and must not hide query/permission failures behind zero values.
- **Sources:** [D2 specification](../specs/2026-10-31-pillar-d2-billing-realization.md), [S.A.H.D.E.V. roadmap](SAHDEV_VERTICAL_SLICES.md).

## ADR-004 — Never aggregate unlike currencies into one total

- **Status:** Accepted
- **Recorded:** 2026-10-31
- **Decision:** Group monetary measures by their correct source currency. Do not create a combined grand total across currencies unless a separately specified, auditable conversion policy is introduced.
- **Rationale:** Adding amounts in different currencies produces a misleading number.
- **Sources:** [D2 specification](../specs/2026-10-31-pillar-d2-billing-realization.md), [README](../README.md).

## ADR-005 — Keep Payment Entry receipts distinct from POS receipts

- **Status:** Accepted
- **Recorded:** 2026-10-31
- **Decision:** Report submitted customer Receive Payment Entries using `received_amount`, grouped by receiving-account currency. This includes allocated and advance/unallocated receipts, so label the measure as receipts received—not as cash allocated to invoices. Report POS receipts separately from submitted non-return POS Sales Invoices using `paid_amount`, grouped by invoice currency.
- **Rationale:** Combining these sources risks double counting and misrepresenting what the figures measure.
- **Sources:** [D2 specification](../specs/2026-10-31-pillar-d2-billing-realization.md), [S.A.H.D.E.V. roadmap](SAHDEV_VERTICAL_SLICES.md).

## ADR-006 — Do not silently substitute missing financial data with zero

- **Status:** Accepted
- **Recorded:** 2026-10-31
- **Decision:** When a source DocType, required field or read permission is unavailable, surface an explicit unavailable state for that section. Do not display zero as though the query succeeded.
- **Rationale:** Zero is a valid business result; unavailable is a different state and must remain distinguishable.
- **Sources:** [D2 specification](../specs/2026-10-31-pillar-d2-billing-realization.md), [S.A.H.D.E.V. roadmap](SAHDEV_VERTICAL_SLICES.md).

## ADR-007 — Webhook writes require an authenticated, least-privilege integration identity

- **Status:** Accepted
- **Recorded:** 2026-10-31
- **Decision:** The signal-ingest endpoint must reject Guest access. External integrations should use a dedicated integration user with API key/secret authentication over HTTPS and only the create permission needed for the integration. Do not use Administrator credentials; rotate secrets and keep them out of source control and logs.
- **Rationale:** Signal ingestion is a write path and must have an attributable identity with limited permissions.
- **Sources:** [README](../README.md), [Security guide](SECURITY_SCANNING.md), [Implementation Plan](../IMPLEMENTATION_PLAN.md).

## ADR-008 — Realtime alerts are recipient-scoped

- **Status:** Accepted
- **Recorded:** 2026-10-31
- **Decision:** Resolve realtime recipients from the related Lead/Customer owner and active ToDo assignees. Do not fall back to a site-wide broadcast. Users must retrieve full signal data through permission-checked APIs.
- **Rationale:** An alert should reach people with a relevant relationship to the record without leaking customer context to unrelated users.
- **Sources:** [README](../README.md), [Implementation Plan](../IMPLEMENTATION_PLAN.md).

## ADR-009 — Require specifications and mapped tests for new behavior

- **Status:** Accepted
- **Recorded:** 2026-10-31
- **Decision:** Start feature work with a spec containing problem/user, goals/non-goals, source of truth, behavior definitions, acceptance criteria, validation mapping, risks and rollout. Map criteria to unit, Bench integration, browser E2E and migration checks as appropriate.
- **Rationale:** Code presence and mocked tests alone are not sufficient evidence of a working Frappe feature.
- **Sources:** [Specifications guide](../specs/README.md), [Quality Gates](QUALITY_GATES.md).

## ADR-010 — Target Frappe/ERPNext v15 and v16, and validate both in CI

- **Status:** Accepted
- **Recorded:** 2026-10-31
- **Decision:** The project declares intended compatibility with Frappe and ERPNext v15 and v16. CI must exercise both version lines; the v16 lane additionally runs browser E2E. A declared dependency range alone is not proof of compatibility, and target-site validation remains separate.
- **Rationale:** Framework behavior and APIs can differ between major versions, including aggregate query syntax and Desk routes.
- **Sources:** [pyproject.toml](../pyproject.toml), [Quality Gates](QUALITY_GATES.md), [Implementation Plan](../IMPLEMENTATION_PLAN.md).

## How to add or change a decision

Append a new ADR with the next available identifier. Include status, date recorded, context, decision, consequences/trade-offs and source links. Do not silently rewrite a superseded decision: mark it **Superseded** and link the replacement ADR. Record unresolved proposals separately as **Proposed**; do not present them as accepted policy.
