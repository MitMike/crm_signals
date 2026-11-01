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


## ADR-025 — Enforce graduated source-size and complexity guardrails

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Context:** Frappe repositories inspected use Ruff, ESLint/Prettier, pre-commit and custom Semgrep rules, but the sampled configurations did not establish a universal per-file line-count limit. A flat 400-line hard cap would be overly restrictive for cohesive Frappe controllers, Desk pages and test modules.
- **Decision:** Use review warnings and hard CI ceilings rather than a universal 400-line cap. Production source files warn above 500 non-blank lines and fail above 800; test/E2E files warn above 800 and fail above 1,200. Production Python functions/methods warn above 50 lines and fail above 100; test functions warn above 80 and fail above 150. Ruff and ESLint enforce cyclomatic complexity no higher than 15; complexity above 10 is a review signal. Enforce in CI and pre-commit. Ignore generated, minified and vendored output. Exceptions must be exact-path entries with a reason.
- **Rationale:** File size alone is a weak proxy for maintainability. Graduated limits identify outliers without forcing arbitrary decomposition; complexity and function size target difficult-to-test logic more directly.
- **Consequences:** Add a standard-library checker, automated tests, Ruff/ESLint rules, pre-commit integration and a dedicated exception register. Warnings are visible but do not block CI; hard-limit violations fail the Quality Checks gate. Revisit thresholds against actual code review and warning volume after adoption.
- **Sources:** [Quality Gates](QUALITY_GATES.md), [Frappe Semgrep rules](https://github.com/frappe/semgrep-rules), [Frappe Insights custom rules](https://github.com/frappe/insights/blob/develop/.semgrep/insights.yml).


## ADR-026 — Configure CRM Signals through one validated site Settings singleton

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Use a System Manager-only `CRM Signals Settings` singleton for the site-wide master switch, external ingestion, Quotation threshold, Opportunity trigger statuses, digest window/time and additional recipients. Provide Balanced, Sales Focused and Executive starter presets; choosing a preset applies values but does not prevent subsequent customisation.
- **Rationale:** Business policy must be changed by an administrator without editing application source. Starter profiles reduce setup work without pretending that one set of values fits every site.
- **Consequences:** Validate inputs server-side. Keep the source defaults as bootstrap values only. Do not expose settings to Sales Users.
- **Sources:** [Settings and reliability spec](../specs/2026-11-01-settings-and-core-reliability.md), [Administrator guide](ADMIN_GUIDE.md).

## ADR-027 — The first release has one site-wide quotation threshold currency

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Interpret the quotation threshold in the default Company's currency and compare against Quotation `base_grand_total`. Display the Quotation's own transaction currency. If the Quotation Company's base currency does not match the configured threshold currency, do not emit a threshold alert.
- **Rationale:** Comparing a transaction-currency amount directly to a threshold in another currency is incorrect. A conversion policy would need an explicit rate date/source and audit semantics.
- **Consequences:** Multi-company sites using different base currencies require per-company settings before quotation alerts can be enabled across those companies. Do not assume INR.
- **Sources:** [Settings and reliability spec](../specs/2026-11-01-settings-and-core-reliability.md), [Administrator guide](ADMIN_GUIDE.md).

## ADR-028 — Enforce idempotency with a unique source-event hash

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Derive a SHA-256 key from source type, source identity and stable source event ID, and enforce uniqueness on CRM Signal. Check for an existing record for the common retry path and use the database unique constraint as the race-safe boundary. A duplicate returns the original record and emits no second notification.
- **Rationale:** Webhook/provider retries and repeated document hooks must not create duplicate alerts.
- **Consequences:** External callers must reuse the same integration user, source namespace and `source_event_id` for a retry. When source metadata is omitted, the authenticated user is used as the namespace; when source DocType/name are supplied, that pair defines the namespace. Requests without an event ID retain legacy non-idempotent behavior. Existing records remain valid with a null source key.
- **Sources:** [Settings and reliability spec](../specs/2026-11-01-settings-and-core-reliability.md), [Core/access spec](../specs/2026-11-01-crm-signals-core-and-access.md).

## ADR-029 — Run the digest at a configurable site-local time and mark the queued date transactionally

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Check the digest every minute, compare against the timezone configured in System Settings, and queue a separate permission-filtered email for each recipient. Track the recipients queued for the site-local date in Settings only after each `frappe.sendmail` call succeeds; save the email-queue request and recipient marker in the same transaction.
- **Rationale:** A source-code cron expression cannot reflect runtime administrator settings, and each recipient must only receive source rows their ERPNext account can read. Per-recipient tracking lets a later scheduler run retry a failed recipient without resending to those already queued.
- **Consequences:** Actual delivery can be delayed by scheduler/worker/mail-queue load. Concurrent scheduler executions can still race before the recipient marker commits; a per-recipient lock/unique delivery record remains a follow-up. Validate timezone and queue transaction behavior on the target site.
- **Sources:** [Daily digest spec](../specs/2026-11-01-crm-signals-daily-digest.md), [Settings and reliability spec](../specs/2026-11-01-settings-and-core-reliability.md).

## ADR-030 — Isolate realtime notification errors from source-document saves

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Attempt realtime delivery after the CRM Signal is saved, catch and log failures per recipient, and continue to the next recipient. A notification failure must not roll back the Quotation/Opportunity or CRM Signal transaction.
- **Rationale:** Realtime notification is ancillary to the ERPNext source transaction; a transient socket or broker failure must not prevent a quotation from being submitted.
- **Consequences:** This is failure isolation, not a durable retry queue. Automatic retry/reconciliation of failed signal creation or notification delivery remains a tracked follow-up.
- **Sources:** [Settings and reliability spec](../specs/2026-11-01-settings-and-core-reliability.md), [Notification implementation](../crm_signals/notifications.py).


## ADR-031 — Additional digest recipients must be registered enabled System Users

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Accept additional digest recipients only when the supplied email resolves to a registered, enabled Frappe System User. Validate this when Settings is saved and filter again when the digest is queued.
- **Rationale:** Avoid silently accepting an address that the scheduler later ignores, and prevent arbitrary external email delivery from a trusted scheduler context.
- **Consequences:** Guest, disabled users, Website Users, unknown addresses and arbitrary external recipients are rejected. Sales Manager role recipients remain automatically resolved from enabled System Users.
- **Sources:** [Settings and reliability spec](../specs/2026-11-01-settings-and-core-reliability.md), [Administrator guide](ADMIN_GUIDE.md).


## ADR-032 — CRM Signal source-event hashes are server-derived

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Derive `source_event_key` in CRM Signal DocType validation from the normalized source type, source name and source event ID. Ignore/replace caller-supplied hashes; clear the hash when no complete source identity is provided; reject partial source identities.
- **Rationale:** A unique index is only a trustworthy idempotency boundary when callers cannot forge a different key for the same source identity or attach arbitrary keys to unrelated records.
- **Consequences:** All writes, including Desk/API writes outside the ingestion endpoint, use the same canonical identity. The source-event fields remain hidden/read-only in Desk, but the server remains authoritative.
- **Sources:** [CRM Signal controller](../crm_signals/crm_signals/doctype/crm_signal/crm_signal.py), [Settings and reliability spec](../specs/2026-11-01-settings-and-core-reliability.md).


## ADR-033 — Generate scheduled digests under each recipient's permissions

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Never compute one privileged, site-wide digest and send it to multiple users. Generate each digest while running source queries under that recipient's Frappe user context, use permission-aware `frappe.get_list` calls, and send a separate message per user. Missing read access/source configuration is shown as unavailable, not as zero.
- **Rationale:** Scheduled tasks run with elevated context; sending `frappe.get_all` / `frappe.db.count` results to all Sales Managers can reveal rows outside an individual's role or User Permission scope.
- **Consequences:** Track queued recipients by site-local date so a failed recipient can be retried without resending to users whose emails were already queued. Concurrent scheduler execution still needs an explicit lock/unique delivery record and remains a tracked follow-up.
- **Sources:** [Daily digest spec](../specs/2026-11-01-crm-signals-daily-digest.md), [Digest implementation](../crm_signals/tasks.py), [Deferred follow-ups](FOLLOW_UPS.md).

## ADR-034 — Realtime recipients must be able to read the linked party

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Before publishing a CRM Signal notification, verify that each resolved owner or active assignee has Frappe read permission on the linked Lead/Customer and on the CRM Signal document itself. If either permission check fails or errors, exclude that recipient. Do not send the message or party reference merely because a user owns or is assigned to the parent record.
- **Rationale:** A realtime message contains the signal message and linked party references. A notification is not an authorization grant; sending it to a user who cannot read either the parent or the CRM Signal can disclose business information before the user opens the record.
- **Consequences:** Recipient resolution fails closed and is tested for denied and allowed users. Signal creation remains independent of whether any recipient qualifies.
- **Sources:** [Events and notifications specification](../specs/2026-11-01-crm-signals-events-and-notifications.md), [Notification implementation](../crm_signals/notifications.py), [Notification tests](../tests/test_notifications.py).

## ADR-035 — Linked signal list access must match parent and document read permissions

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** The CRM Signal list query may include an owner-based clause only for unlinked signals. Linked signals are included only through owned/assigned Lead or Customer names returned by permission-aware `frappe.get_list`. The direct-document permission hook remains authoritative for each record.
- **Rationale:** An unconditional `owner = current_user` list clause can expose a linked signal even when User Permissions prevent its owner from reading the linked Lead/Customer. Hiding the form after the list query is too late; list and direct access must agree.
- **Consequences:** Linked-signal visibility requires a readable relationship, while an unlinked signal remains visible to its owner. Unit and Bench-backed tests cover a Sales User with a User Permission that excludes the linked Lead.
- **Sources:** [Core/access specification](../specs/2026-11-01-crm-signals-core-and-access.md), [Permission implementation](../crm_signals/permissions.py), [Bench permission tests](../crm_signals/tests/test_notification_permissions.py).

## ADR-036 — CRM Signals and external ingestion are disabled on fresh installation

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Default the CRM Signals master switch and external ingestion switch to off, including the safe fallback used when the Settings singleton is not yet available. A System Manager must review site-specific configuration and explicitly enable the feature. External ingestion remains a separate opt-in.
- **Rationale:** Installing an app must not silently start business notifications, scheduled digests or an authenticated write endpoint before the site owner confirms currency, workflows, timezone, recipients and integration access.
- **Consequences:** Starter presets configure business rules but do not activate the app. The administrator guide and deployment runbook require an explicit activation step after preflight.
- **Sources:** [Settings implementation](../crm_signals/settings.py), [Settings DocType](../crm_signals/crm_signals/doctype/crm_signals_settings/crm_signals_settings.json), [Administrator guide](ADMIN_GUIDE.md).

## ADR-037 — Bound the daily digest quotation list

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Fetch at most 101 expiring Quotations, display at most 100, and render `100+` with an explicit notice when additional rows exist.
- **Rationale:** An unlimited query can produce an unbounded email body and impose avoidable database, worker and mail-queue load on sites with many Quotations expiring on one date.
- **Consequences:** The digest remains concise and honest about truncation; users must open ERPNext for the full list. The count is a lower-bound indicator only when the cap is reached.
- **Sources:** [Daily digest specification](../specs/2026-11-01-crm-signals-daily-digest.md), [Digest implementation](../crm_signals/tasks.py), [Digest tests](../tests/test_digest_rendering.py).


## ADR-038 — Use Frappe's supported formatted naming expression for CRM Signals

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Define CRM Signal autoname as `format:SIG-{YYYY}-{#####}`, using Frappe's brace-delimited format tokens.
- **Rationale:** The previous dotted expression was persisted literally as `SIG-.YYYY.-.#####` in Bench v15/v16, causing every inserted CRM Signal to collide on the same primary key. This is a real installation/runtime defect, not a test-only issue.
- **Consequences:** Fresh installs and schema syncs use a date-prefixed sequence. Validate upgrade/sync behavior on existing sites and ensure the naming series advances correctly after deployment.
- **Sources:** [CRM Signal DocType](../crm_signals/crm_signals/doctype/crm_signal/crm_signal.json), [Bench CI failure](https://github.com/MitMike/crm_signals/actions).


## ADR-039 — Keep CRM Signal row permissions compatible with Frappe v15 and v16

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Context:** Bench v16 exposed that the row-level permission hook used the v15 `permission_type` argument and returned `None` for manager/create and other paths. Frappe v16 passes `ptype` and requires an explicit boolean result. That made valid Sales User create/read permissions fail in the integration and recipient paths.
- **Decision:** Accept both `permission_type` and `ptype` hook arguments. For every operation, first enforce the CRM Signal DocType's role-level permission; then apply row/relationship restrictions to read, write and delete. Return an explicit boolean for all hook calls. Keep the endpoint's normal permission check enabled; do not bypass DocType permissions.
- **Rationale:** Framework compatibility must not weaken the security model. Role-level permissions remain the baseline, while linked records still require a readable owned/assigned parent and unlinked records remain owner-scoped.
- **Consequences:** Bench tests exercise both hook signatures, Sales User create permission, parent/signal read restrictions and recipient routing on v15/v16.
- **Sources:** [Frappe v16 migration guide](https://github.com/frappe/frappe/wiki/Migrating-to-version-16), [Permission implementation](../crm_signals/permissions.py), [Permission integration tests](../crm_signals/tests/test_notification_permissions.py).


## ADR-040 — Synchronize browser login and settings-control changes in E2E

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Context:** Frappe v16 E2E demonstrated that the session cookie becomes available before the login page's redirect to Desk has completed. The tests started further API calls/navigation during that redirect, producing aborted navigations, destroyed execution contexts and CSRF token errors. The settings preset E2E also changed an integer input without committing the control's blur/change event, while the custom-preset handler did not await the resulting model update.
- **Decision:** Make the shared Playwright login helper wait for a Desk URL after the authenticated session is established. Commit the settings input before asserting custom-preset state, and await the preset change in the DocType field handler.
- **Rationale:** The test must synchronize on the application state that subsequent actions depend on, not merely on the existence of a session cookie. The UI handler should expose completion of the form-model update.
- **Consequences:** Browser coverage now tests the post-login Desk state and the form-model transition rather than racing navigation and browser input events.
- **Evidence:** `e2e/sahdev-dashboard.spec.ts`; `crm_signals/public/js/crm_signals_settings.js`.


## ADR-041 — Prove DocType schema upgrades with historical CRM Signal rows

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Decision:** Add a Bench migration rehearsal that starts with the pre-source-event-identity CRM Signal table and DocField metadata, retains historical rows, then runs the current `bench migrate` and verifies that the current fields and unique source-event key are restored without losing or rewriting legacy records.
- **Rationale:** Fresh-install CI does not prove that Frappe can upgrade an existing site's DocType metadata and physical table safely. The relevant compatibility boundary is the old schema plus real historical rows, not whether `patches.txt` contains a file.
- **Consequences:** Do not add a patch solely because `patches.txt` is empty. Add a patch only if the supported Frappe migration path demonstrably cannot perform the required schema transition. The rehearsal is a CI compatibility test; target-site backup/restore and upgrade acceptance remain separate production gates.
- **Sources:** [CRM Signal DocType](../crm_signals/crm_signals/doctype/crm_signal/crm_signal.json), [Upgrade fixture](../crm_signals/ci.py), [Bench workflow](../.github/workflows/bench-e2e.yml), [Production readiness audit](PRODUCTION_READINESS_AUDIT.md).


## ADR-042 — Model the historical DocType migration hash in upgrade rehearsal

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Context:** The first legacy-schema rehearsal removed the four source-event columns and their DocField rows, then rewound `tabDocType.modified`. Frappe v15 and v16 still skipped the DocType import because their importer also checks the stored `migration_hash`; a matching hash short-circuits the import regardless of the timestamp.
- **Decision:** The disposable CI fixture clears the CRM Signal DocType's `migration_hash` as well as rewinding its modified timestamp before running `bench migrate`.
- **Rationale:** The fixture must represent an older installed DocType definition, not merely a damaged table paired with a current-schema migration hash. Clearing the hash makes Frappe re-import the current JSON through its normal migration path.
- **Consequences:** Keep the upgrade rehearsal failing until both supported Frappe versions demonstrate restoration of the fields and preservation of historical rows. Do not replace the rehearsal with a direct `reload_doc` call, which would bypass the migration path being tested.
- **Evidence:** Frappe v15 and v16 `frappe/modules/import_file.py`; CI jobs [v15](https://github.com/MitMike/crm_signals/actions/runs/41291789841/job/124804365910) and [v16](https://github.com/MitMike/crm_signals/actions/runs/41291789841/job/124804366016).

## ADR-043 — Test API idempotency with independent concurrent database connections

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Context:** Existing webhook integration coverage proved sequential retries and a mocked unique-key collision, but neither exercised two real transactions that both observe the event key as absent before attempting insertion.
- **Decision:** Add a Bench-backed concurrency regression test that invokes the authenticated API handler from two worker threads, each with its own Frappe database connection and user context. Synchronize the initial identity reads so both transactions reach the insert race, then assert one persisted CRM Signal, one non-deduplicated response, one deduplicated response and exactly one notification dispatch.
- **Rationale:** A deterministic race test is more reliable than timing-dependent load tests for proving the exact read-before-insert failure mode. Running against the Bench MariaDB database exercises the unique constraint and locking-read recovery used in production.
- **Consequences:** The regression test is required on both supported Frappe v15 and v16 Bench lanes. It covers the API handler and database race, not HTTP gateway throughput or production webhook rate limiting.
- **Evidence:** Merged in PR #23 as `d75b7f3`; [Bench v15/v16 + Playwright](https://github.com/MitMike/crm_signals/actions/runs/41300667892), [Quality](https://github.com/MitMike/crm_signals/actions/runs/41300667996) and [Security](https://github.com/MitMike/crm_signals/actions/runs/41300667997) passed on head `7ed0860`.


## ADR-044 — Serialize digest recipient claims across scheduler workers

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Context:** The digest previously read the queued-recipient marker without locking, then queued mail and updated the marker. Two scheduler workers could both observe a recipient/date as pending and enqueue duplicate messages before either transaction committed.
- **Decision:** Acquire a row lock on the CRM Signals Settings singleton before reading the marker. Re-acquire the lock and re-read the marker before each recipient queue operation because per-recipient commits release the lock and allow another worker to make progress. Write system-owned digest status fields with `Document.db_set` so the update does not rerun unrelated Settings validation; keep that write in the same transaction as the Email Queue insert.
- **Rationale:** Use the database as the serialization point across processes and workers. An in-process mutex would not protect multiple Frappe workers or hosts.
- **Consequences:** The two-connection Bench test synchronizes two workers before the lock and proves a single queue request for the same recipient/date. This does not prove delivery after the Email Queue is created or replace target-site scheduler/mail testing.
- **Evidence:** Merged in PR #23 as `d75b7f3`; [Bench v15/v16 + Playwright](https://github.com/MitMike/crm_signals/actions/runs/41300667892), [Quality](https://github.com/MitMike/crm_signals/actions/runs/41300667996) and [Security](https://github.com/MitMike/crm_signals/actions/runs/41300667997) passed.


## ADR-046 — Run release readiness as an evidence-gated sprint

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Context:** The core feature set and concurrency hardening are merged, while target-site acceptance and reliability/roadmap work remain open. A transactional outbox implementation is already under review in PR #26 and has failed its latest Frappe v15/v16 Bench validation.
- **Decision:** Sequence work by release risk: (1) repair and validate PR #26 before merge; (2) prepare a target-site acceptance kit and execute all source-independent release checks; (3) collect target-site evidence for configuration, permissions, financial reconciliation, scheduler/mail, integration credentials and backup/restore; (4) then implement D3 and complete H under their documented source/privacy gates; (5) defer E, V and A until their dependencies are approved. Do not duplicate work already present in an open PR.
- **Rationale:** Durable event persistence and correct retry behavior are more important to release confidence than starting additional dashboard surfaces. Site-specific values and policies must be observed, not guessed.
- **Consequences:** PR #26 remains unmergeable until Frappe v15 and v16 Bench suites pass. Target-site sign-off remains blocked until actual installation and business evidence is recorded. Realtime notification retry is tracked separately from the source-event outbox.
- **Evidence:** PR #26 check runs on head `a63b3b60f909ebc0e62d5bfde383aa6224ba36b2`; latest failures include `test_two_workers_enqueue_the_same_source_event_once` (MariaDB lock wait timeout), `test_two_workers_process_one_outbox_event_once` (missing source-event key in fixture), and `test_worker_filters_future_retries_before_applying_batch_limit` (missing source-event key in fixture).


## ADR-047 — Defer outbox delivery until after the source transaction commits

- **Status:** Accepted
- **Recorded:** 2026-11-01
- **Context:** PR #26's two-connection enqueue race consistently timed out while the winning request attempted signal delivery before committing its outbox row. A competing request waited on the unique source-event key while the first transaction still performed delivery work.
- **Decision:** Persist the outbox row in the source transaction, register immediate background delivery with `frappe.enqueue(..., enqueue_after_commit=True)`, and retain the once-per-minute pending-outbox scheduler as recovery if queue submission or delivery fails. Do not run signal materialization synchronously inside the source transaction.
- **Rationale:** Keep the source event and outbox row atomic while moving nonessential delivery work outside the transaction. This should shorten unique-key lock duration and prevent delivery latency from holding competing idempotent inserts. Queue failure must not lose the durable row; the scheduler remains the fallback.
- **Validation:** PR #26 passed Quality Checks, Security Scanning and Bench Integration/E2E on synchronized final head `222e70ec71164dab4448f7319525042323a357b4`; Frappe v15/v16 race tests verified one outbox row, one CRM Signal and one notification dispatch. All three workflows passed before squash merge `b0364a74affa823977af74d1907781d1533e60c0`.


## ADR-048 — Use standard Frappe Helpdesk as the initial D3 source

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** The project owner confirmed the support system is Frappe Helpdesk and that its standard/default configuration is in use. The initial SLA working-week assumption is Monday–Saturday.
- **Decision:** Implement D3 against the standard HD Ticket and HD Service Level Agreement DocTypes. Use HD Ticket.status_category for Open/Paused/Resolved lifecycle aggregation, resolution_date and native resolution_time for resolution measures, and native agreement_status values Fulfilled/Failed for SLA compliance. Check runtime metadata and independent ticket/SLA read permissions. Return aggregate-only data. Scope created/resolved/SLA outcomes to the rolling 30-day cohort; keep current backlog unbounded by date.
- **Calendar rule:** Monday–Saturday is the agreed initial business-week assumption, but do not overwrite Helpdesk configuration or recalculate deadlines. The active SLA's configured working-hours rows, holiday list and timezone are authoritative. A target-site mismatch must be recorded and resolved during acceptance.
- **Rationale:** This delivers a useful adapter without fabricating SLA results or bypassing Helpdesk's own calendar and lifecycle engine.
- **Consequences:** Sites without the Helpdesk DocTypes or required fields receive unavailable metrics. Tickets without an applicable SLA are counted separately and excluded from compliance. Paused, First Response Due and Resolution Due are excluded from the fulfilled/failed denominator. Target-site version, permissions and calendar validation remain mandatory.

## ADR-049 — Treat Frappe v16.5 as the target-site compatibility baseline

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** The deployment owner confirmed the target instance runs Frappe v16.5. The repository's automated compatibility matrix covers Frappe v15 and v16, but generic v16 coverage does not by itself prove the exact target site's installed apps, patches, customizations, permissions or configuration.
- **Decision:** Use Frappe v16.5 as the primary target for configuration guidance, API/schema compatibility review and acceptance instructions. Retain v15 coverage as a supported compatibility matrix unless a separate product decision removes it. Do not claim live-site acceptance from CI; capture the observed Frappe, ERPNext and Helpdesk app versions before configuration and explicitly label every site-dependent check.
- **Rationale:** A confirmed target version is stronger evidence than a generic supported-major assumption. Targeting the exact v16.5 baseline reduces ambiguity in the operator guide while preserving the existing cross-version support commitment.
- **Consequences:** The operator guide will identify Frappe v16.5 as the expected target, request the exact patch/build string printed by `bench version` and the ERPNext/Helpdesk app versions, and distinguish framework compatibility from site-specific acceptance. No production sign-off is implied.

## ADR-050 — Provide an audited System Manager replay for terminal outbox failures

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** The transactional signal outbox retries transient delivery failures with bounded backoff, but exhausted events remain in a terminal Failed state. Operators could inspect those rows but could not safely replay them without direct database intervention.
- **Decision:** Add a POST-only System Manager form action that also requires read permission on CRM Signal Outbox. Lock the row and allow replay only from Failed. Atomically return it to Pending, clear the retry gate, preserve the original attempt count and last error, increment replay count, record the latest actor/time, add a document Comment for each replay, and enqueue the existing idempotent worker after commit. Require explicit UI confirmation; do not expose direct status editing.
- **Rationale:** Manual recovery must be explicit, attributable and use the same idempotent delivery path as automatic retries. It must not erase evidence or permit a second replay while the row is Pending/Completed.
- **Consequences:** A failed enqueue leaves a durable Pending row for the scheduled worker. The stable source-event key prevents duplicate CRM Signals. Realtime notification delivery remains a separate reliability concern.
- **Validation:** Bench tests cover non-System-Manager denial, missing outbox read permission, replay state, preserved attempt history, audit metadata/comment and after-commit enqueue. Required Frappe v15/v16 CI remains the merge gate.

## ADR-052 — Treat Helpdesk field-level permissions as metric availability gates

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** Standard Frappe Helpdesk places `status_category`, `resolution_date`, `resolution_time` and `sla` at permlevel 7, and `agreement_status` at permlevel 8. Frappe v15/v16 `get_list` filters fields the current user cannot read instead of necessarily failing the query. A DocType-level read check alone can therefore turn hidden lifecycle fields into misleading zero/empty aggregates.
- **Decision:** Before each D3 aggregate, inspect the current user's permitted HD Ticket field names at read permission level. Compute backlog, resolution and SLA metrics only when every field required by that measure is readable. Keep independent metrics available when their fields are permitted; otherwise return the measure as unavailable (`null`/availability false), never as zero. Do not automatically grant Helpdesk permlevels to Sales roles.
- **Rationale:** Availability must reflect the data the current user is authorized to read. Silent field removal is not evidence of zero tickets, and granting permlevel 7/8 broadly may expose additional Helpdesk fields outside the aggregate dashboard.
- **Consequences:** The operator guide must explicitly test HD Ticket field-level access for Sales User/Manager. A site may show ticket creation counts while backlog, resolution or SLA measures remain unavailable until an authorized least-privilege policy is approved.
- **Evidence:** [Frappe v16 permitted-field filtering](https://github.com/frappe/frappe/blob/version-16/frappe/model/db_query.py) and [Frappe Helpdesk HD Ticket field permlevels](https://github.com/frappe/helpdesk/blob/main/helpdesk/helpdesk/doctype/hd_ticket/hd_ticket.json).

## ADR-055 — Pin an exact Frappe v16.5.0 + Helpdesk compatibility lane

- **Status:** Accepted
- **Date:** 2026-11-02
- **Context:** The deployment owner confirmed Frappe v16.5 as the target. The existing CI matrix uses the moving 'version-16' branch, which verifies major-version compatibility but not the exact v16.5 patch or the installed Helpdesk schema. D3 depends on standard HD Ticket and HD Service Level Agreement metadata and Helpdesk field permlevels.
- **Evidence:** Frappe tag [v16.5.0](https://github.com/frappe/frappe/tree/v16.5.0) requires Python >=3.14,<3.15; ERPNext tag [v16.5.0](https://github.com/frappe/erpnext/tree/v16.5.0) supports Frappe >=16.0.0,<17.0.0; Helpdesk [v1.31.1](https://github.com/frappe/helpdesk/tree/v1.31.1) supports Frappe >=15.123.1,<17.0.0 and declares Telephony as a required app; Telephony commit [9447577500a25d242088398157b72c654fa34b20](https://github.com/frappe/telephony/commit/9447577500a25d242088398157b72c654fa34b20) supports Frappe through the v16 line. Helpdesk v1.31.1 defines status_category, resolution_date, resolution_time and sla at permlevel 7, and agreement_status at permlevel 8.
- **Decision:** Add a dedicated Bench matrix lane pinned to Frappe v16.5.0, ERPNext v16.5.0, Helpdesk v1.31.1 and the exact Telephony commit above. Keep the moving v15/v16 jobs. The pinned lane must install the real Helpdesk app and verify required DocTypes, field permlevels and Frappe's permitted-field API without reading ticket/customer records.
- **Consequences:** The exact lane provides reproducible framework/app compatibility evidence and catches Helpdesk schema or permission-level drift before merge. It is not proof that the pilot site uses these exact app versions or has the required Sales-role permissions, SLA calendar, timezone or customizations; record the site's observed versions and run the live acceptance checklist separately.

