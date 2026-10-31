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


## ADR-011 — Pin and audit the JavaScript CI toolchain

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Context:** The dependency audit identified a vulnerable Playwright version and a vulnerable transitive minimatch version. The repository also lacked a committed npm lockfile, so transitive dependency resolution could change between CI runs.
- **Decision:** Pin direct JavaScript development dependencies, commit package-lock.json (lockfile v3), use \`npm ci\` in CI, and fail npm audit on moderate-or-higher findings. Dependabot checks npm weekly. Do not use \`npm audit fix --force\` when it proposes breaking downgrades.
- **Rationale:** Reproducible dependency trees and explicit updates reduce supply-chain drift.
- **Consequences:** Dependency updates become explicit reviewed changes; lockfile updates must accompany package.json changes. CI installs are reproducible for a given lockfile.
- **Sources:** [Security scanning](SECURITY_SCANNING.md), [Quality gates](QUALITY_GATES.md), [CRM Signals dependency PR #11](https://github.com/MitMike/crm_signals/pull/11).

## ADR-012 — CI success and target-site acceptance are separate release gates

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Quality, Bench, security and dependency workflows prove the tested code/configuration on their CI fixtures only. Production release also requires a target-site preflight, role/permission verification, financial reconciliation, site customization checks, webhook deployment controls and rollback/runbook validation.
- **Rationale:** CI cannot establish the target site's custom fields, roles, installed support apps, currency, workflows or actual financial totals.
- **Consequences:** The release checklist remains open until an authorized target site is available and the checks are recorded. Do not describe a CI-green branch as production accepted.
- **Sources:** [Implementation plan](../IMPLEMENTATION_PLAN.md), [Progress](PROGRESS.md), [D2 specification](../specs/2026-10-31-pillar-d2-billing-realization.md).

## ADR-013 — Keep business thresholds and status semantics explicit and configurable

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Preserve the existing application defaults only as defaults: high-value quotation threshold 200,000 in Company default currency (not hard-coded INR); Opportunity signal status Replied; Lead digest condition modified more than 3 calendar days ago; daily digest at 08:30 in the verified site timezone. D1 terminal statuses default to Cancelled, Closed, Converted, Do Not Contact, Lost and Obsolete, including Lost-prefixed variants. Make these settings configurable and validate them against target-site metadata/workflows. If a required status or currency cannot be resolved, the dependent metric/alert is unavailable rather than guessed.
- **Rationale:** ERPNext workflows, currency and site timezones vary. Source-code constants must not become unreviewed business policy.
- **Consequences:** Add a validated CRM Signals Settings singleton and target-site configuration checklist. D1 must stop counting every Lead/Opportunity as active when a status field is missing.
- **Sources:** [Core spec](../specs/2026-11-01-crm-signals-core-and-access.md), [Events spec](../specs/2026-11-01-crm-signals-events-and-notifications.md), [Digest spec](../specs/2026-11-01-crm-signals-daily-digest.md), [D1 spec](../specs/2026-11-01-pillar-d1-sales-compass.md).

## ADR-014 — CRM Signal read state is a shared team acknowledgement in v1

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Keep the existing \`is_read\` Boolean as one shared signal-level acknowledgement. A read signal is acknowledged by the team, not separately read by every recipient. Per-user inboxes and personal unread counts are out of scope for v1 and require a separate acknowledgement model and spec.
- **Rationale:** The current data model and dashboard use one Boolean. Reinterpreting it as personal state without a schema change would produce inconsistent counts and UX.
- **Consequences:** Document the shared behavior in the UI. Do not claim that unread counts are per user. Revisit only when individual acknowledgement is a confirmed requirement.
- **Sources:** [Core spec](../specs/2026-11-01-crm-signals-core-and-access.md).

## ADR-015 — Signal creation must be idempotent for identifiable source events

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Add source DocType, source document name and source event ID/key to generated CRM Signals. A retry with the same key must not create a second signal or notification. New external integrations must send a stable provider event ID. Existing callers may omit it during a backward-compatible transition, in which case duplicate suppression is not guaranteed.
- **Rationale:** Event delivery and webhook callers can retry. Duplicate signals inflate metrics and create alert fatigue.
- **Consequences:** Add a schema migration, unique-key enforcement and retry tests before enabling integrations that rely on exactly-once business behavior.
- **Sources:** [Events spec](../specs/2026-11-01-crm-signals-events-and-notifications.md), [Core spec](../specs/2026-11-01-crm-signals-core-and-access.md).

## ADR-016 — D3 must discover the installed support source before implementation

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Do not assume that the target site uses ERPNext Issue, Frappe Helpdesk HD Ticket or a custom ticket DocType. First inventory installed apps, ticket/SLA DocTypes, workflow fields, resolution timestamp, SLA deadline/outcome, pause behavior, business calendar, timezone and permissions. Build adapters only for verified sources.
- **Rationale:** A generic ticket count or guessed field does not prove service resolution or SLA performance.
- **Consequences:** D3 implementation is gated on a target-site mapping record. Unsupported or inaccessible data is displayed as unavailable.
- **Sources:** [D3 specification](../specs/2026-11-01-pillar-d3-service-resolution-sla.md).

## ADR-017 — Highlights require first-party or verifiable proposal-link events

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** High-value quotation alerts use Company currency and a configurable threshold. VIP proposal opens are accepted only from first-party tracked links or a provider callback with a stable event ID. Store token hashes rather than bearer tokens; do not fingerprint browsers or retain full IP addresses. Known scanners do not trigger human-engagement alerts; ambiguous traffic is not escalated. Tracking remains disabled until privacy/consent requirements are approved.
- **Rationale:** An arbitrary URL open is not reliable evidence of human engagement, and tracking introduces privacy/security obligations.
- **Consequences:** Implement quote alerts before proposal tracking. Use explicit VIP/customer allowlists, recipient routing and alert cooldowns.
- **Sources:** [H specification](../specs/2026-11-01-pillar-h-highlights.md).

## ADR-018 — Explorer is an adapter-based view of existing source records

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Explorer reads from source systems through explicit adapters. It includes only installed, configured and permission-readable sources with stable source event IDs. The unified feed stores normalized metadata and safe summaries, not copies of full emails, call recordings, WhatsApp messages or attachments.
- **Rationale:** The app must not invent integrations, bypass source permissions or become a second system of record.
- **Consequences:** Each adapter is independently enabled, tested and disabled. Missing integrations, empty results and permission-denied sources remain distinct states.
- **Sources:** [E specification](../specs/2026-11-01-pillar-e-explorer.md).

## ADR-019 — Vault stores append-only aggregates, not copied CRM content

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Vault snapshots contain approved aggregate metric values, dimensions, source counts, metric definition version and provenance. They are append-only; corrections create a linked revision. Do not persist source party names, record IDs, free-text messages or other raw customer content. Snapshot scheduling remains disabled until an explicit retention period and source-visibility policy are configured and approved.
- **Rationale:** Historical reporting needs reproducible values without creating a shadow copy of sensitive CRM data or an accidental indefinite-retention store.
- **Consequences:** Metric registry and retention configuration precede scheduled snapshots. Backfills are bounded, admin-only and audited.
- **Sources:** [V specification](../specs/2026-11-01-pillar-v-vault.md).

## ADR-020 — Analysis resolves only to an approved metric/query registry

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Natural-language questions may map to a constrained metric ID, date range, filter and grouping. Execution always uses server-owned, versioned query definitions and permission-aware Frappe reads. No model-generated SQL, Python, DocType, field or executable query is accepted. A deterministic template path works without an LLM.
- **Rationale:** Business answers must be auditable, permission-aware and tied to accepted metric definitions.
- **Consequences:** Build the metric registry from D1/D2/D3/H definitions before shipping Analysis. Unknown questions fail closed.
- **Sources:** [A specification](../specs/2026-11-01-pillar-a-analysis.md).

## ADR-021 — Deliver in dependency order, not dashboard-card order

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Sequence delivery as repository security/quality gates; target-site and CRM core release hardening; D3 source discovery/implementation; H Highlights; E Explorer; V Vault; and A Analysis. D1/D2 remain implemented foundations with site acceptance still open. Each slice must pass its own spec, tests, permissions, migration and documentation gates before starting its dependent slice.
- **Rationale:** D3 completes the executive dashboard's service view; H/E depend on reliable signal/event routing; V depends on validated metric definitions; A depends on the approved metric registry.
- **Consequences:** Do not build A against guessed metrics or Vault snapshots before source definitions/retention exist. Work may be reordered only through a documented ADR superseding this one.
- **Sources:** [Implementation plan](../IMPLEMENTATION_PLAN.md), [S.A.H.D.E.V. roadmap](SAHDEV_VERTICAL_SLICES.md), [Specifications index](../specs/README.md).


## ADR-022 — Return-sensitive billing metrics require explicit return metadata

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Sales Invoice measures that claim to exclude returns must require the Sales Invoice is_return field. If it is absent or cannot be queried, affected invoiced, POS receipt, outstanding and overdue measures are unavailable. Never silently omit the exclusion filter and proceed.
- **Rationale:** Counting return documents as invoices/receipts or balances would materially distort the metric and conflict with its published definition.
- **Consequences:** D2 acceptance includes metadata-absence tests for each return-sensitive metric. The current conditional filter implementation must be corrected before Stage 1 is complete.
- **Sources:** [D2 Billing Realization spec](../specs/2026-10-31-pillar-d2-billing-realization.md), [Implementation plan](../IMPLEMENTATION_PLAN.md).


## ADR-023 — Enforce CI on main without blocking a solo maintainer

- **Status:** Accepted and verified on 2026-11-01
- **Recorded:** 2026-11-01
- **Decision:** The repository's active ruleset [Protect main](https://github.com/MitMike/crm_signals/rules/26282133) (ID 26282133) targets refs/heads/main. It requires pull requests, strict/up-to-date success for eight contexts (Lint and static checks; Python 3.10, 3.11, 3.12 and 3.14; Semgrep static security analysis; Bench v15/Python 3.11; Bench v16/Python 3.14 with Playwright), and resolved review threads. It blocks branch deletion and non-fast-forward updates (force pushes). Allowed merge methods are merge, squash and rebase. Required approving review count is 0; code-owner and last-push approval are not required. There are no bypass actors, and the current user cannot bypass.
- **Rationale:** Green CI must be enforced rather than advisory, while a fixed second-person approval requirement would deadlock a solo maintainer. Force-push and deletion protection reduce destructive risk.
- **Consequences:** Keep the eight required contexts stable and update the ruleset when workflow job names change. Dependency Security Audit passes as a separate workflow but is not currently one of the eight required contexts. No emergency bypass actor is configured; emergency recovery requires an authorized administrator to edit the ruleset temporarily, record the reason and restore enforcement immediately. [Issue #12](https://github.com/MitMike/crm_signals/issues/12) was closed after the ruleset was verified.
- **Sources:** [Ruleset Protect main](https://github.com/MitMike/crm_signals/rules/26282133), [Quality gates](QUALITY_GATES.md), [Progress](PROGRESS.md), [Issue #12](https://github.com/MitMike/crm_signals/issues/12).
## ADR-024 — Status-dependent metrics are unavailable without status metadata

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Lead and Opportunity active counts require a readable status field and the accepted terminal-status policy. When status is missing, keep status-independent metrics (such as total/created counts and recent records) available, but set active counts to unavailable. Opportunity stage distribution also requires status. Active pipeline additionally requires both amount and currency fields so it can exclude terminal Opportunities and keep currencies separate.
- **Rationale:** Treating all rows as active when status is absent is a false business assertion, not a safe fallback.
- **Consequences:** API results expose explicit availability flags; the UI shows an unavailable state instead of 0 or a misleading all-active count. Regression tests cover metadata absence.
- **Sources:** [D1 Sales Compass specification](../specs/2026-11-01-pillar-d1-sales-compass.md), [Implementation plan](../IMPLEMENTATION_PLAN.md).
