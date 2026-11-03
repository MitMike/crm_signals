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
- **Consequences:** The operator guide will identify Frappe v16.5 as the expected target, request the exact patch build and ERPNext/Helpdesk app versions, and distinguish framework compatibility from site-specific acceptance. No production sign-off is implied.

## ADR-050 — Provide an audited System Manager replay for terminal outbox failures

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** The transactional signal outbox retries transient delivery failures with bounded backoff, but exhausted events remain in a terminal Failed state. Operators could inspect those rows but could not safely replay them without direct database intervention.
- **Decision:** Add a POST-only System Manager form action that also requires read permission on CRM Signal Outbox. Lock the row and allow replay only from Failed. Atomically return it to Pending, clear the retry gate, preserve the original attempt count and last error, increment replay count, record the latest actor/time, add a document Comment for each replay, and enqueue the existing idempotent worker after commit. Require explicit UI confirmation; do not expose direct status editing.
- **Rationale:** Manual recovery must be explicit, attributable and use the same idempotent delivery path as automatic retries. It must not erase evidence or permit a second replay while the row is Pending/Completed.
- **Consequences:** A failed enqueue leaves a durable Pending row for the scheduled worker. The stable source-event key prevents duplicate CRM Signals. Realtime notification delivery remains a separate reliability concern.
- **Validation:** Bench tests cover non-System-Manager denial, missing outbox read permission, replay state, preserved attempt history, audit metadata/comment and after-commit enqueue. Required Frappe v15/v16 CI remains the merge gate.


## ADR-051 — Support explicit per-company quotation alert thresholds

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** The first settings version applies one site-wide quotation threshold in the default Company's currency. Multi-company sites may have different base currencies and different materiality thresholds; comparing base totals against one currency's threshold is invalid.
- **Decision:** Add an optional Company Threshold child table. Each row is keyed by Company, requires an explicitly entered non-negative threshold (including explicit zero), and derives its currency from that Company's configured default currency. Do not silently inherit the site-wide numeric amount into a new Company row. Evaluate the Quotation's base total against the matching Company row. For companies without an override, retain the legacy site-wide threshold only when its currency exactly matches the Company's base currency. Never convert currencies implicitly.
- **Rationale:** Company-specific thresholds avoid false positives/negatives without introducing an unapproved exchange-rate source or conversion policy.
- **Consequences:** Existing single-company configurations continue to work. Multi-company administrators should configure an override for every Company that needs a threshold distinct from the legacy site-wide value. If a Company's base currency changes, reject the stale row until the administrator removes/re-adds it and enters a newly approved amount; do not silently reinterpret the same number in a different currency.
- **Validation:** Unit coverage verifies company-specific currency derivation and threshold selection, rejects mismatched override currencies, and preserves the exact-currency fallback. Bench migration and v15/v16 validation are the merge gate.

## ADR-052 — Treat Helpdesk field-level permissions as metric availability gates

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** Standard Frappe Helpdesk places `status_category`, `resolution_date`, `resolution_time` and `sla` at permlevel 7, and `agreement_status` at permlevel 8. Frappe v15/v16 `get_list` filters fields the current user cannot read instead of necessarily failing the query. A DocType-level read check alone can therefore turn hidden lifecycle fields into misleading zero/empty aggregates.
- **Decision:** Before each D3 aggregate, inspect the current user's permitted HD Ticket field names at read permission level. Compute backlog, resolution and SLA metrics only when every field required by that measure is readable. Keep independent metrics available when their fields are permitted; otherwise return the measure as unavailable (`null`/availability false), never as zero. Do not automatically grant Helpdesk permlevels to Sales roles.
- **Rationale:** Availability must reflect the data the current user is authorized to read. Silent field removal is not evidence of zero tickets, and granting permlevel 7/8 broadly may expose additional Helpdesk fields outside the aggregate dashboard.
- **Consequences:** The operator guide must explicitly test HD Ticket field-level access for Sales User/Manager. A site may show ticket creation counts while backlog, resolution or SLA measures remain unavailable until an authorized least-privilege policy is approved.
- **Evidence:** [Frappe v16 permitted-field filtering](https://github.com/frappe/frappe/blob/version-16/frappe/model/db_query.py) and [Frappe Helpdesk HD Ticket field permlevels](https://github.com/frappe/helpdesk/blob/main/helpdesk/helpdesk/doctype/hd_ticket/hd_ticket.json).

## ADR-053 — Do not treat Frappe realtime queueing as delivery confirmation

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** Frappe v16 `publish_realtime(after_commit=True)` queues a callback and returns before Redis publication. The after-commit flush calls `emit_via_redis`, which suppresses `redis.exceptions.ConnectionError`. The current CRM Signals try/except therefore cannot detect a Redis outage, and its `sent` count represents a queued callback rather than confirmed publication or user receipt.
- **Decision:** Do not add retry logic by merely wrapping `frappe.publish_realtime` in another try/except, and do not describe a queued event as delivered. Keep realtime as best-effort until a durable per-recipient delivery boundary is implemented. Any future retry must persist a stable delivery ID, re-check recipient permissions, use bounded at-least-once attempts and client-side duplicate suppression, and distinguish published/attempted from human-delivered.
- **Rationale:** A retry without a stable idempotency boundary can duplicate toasts; a retry that trusts the current API's return/exception behavior can silently lose events while claiming success.
- **Consequences:** Superseded by ADR-058. PR #54 implements the durable per-recipient ledger, stable delivery IDs, bounded retries, permission rechecks and active-session duplicate suppression; required CI and target-site Redis/worker recovery tests remain open. Do not promise guaranteed human receipt without client acknowledgement.
- **Evidence:** [Frappe v16 realtime implementation](https://github.com/frappe/frappe/blob/v16.5.0/frappe/realtime.py).

## ADR-054 — Require source-document read access before realtime signal delivery

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** CRM Signal notifications include a message derived from the originating Quotation/Opportunity. The existing recipient filter checked read access to the linked Lead/Customer and CRM Signal, but did not check the source document. A user could therefore receive a message containing source-derived values without permission to read the source record.
- **Decision:** A realtime recipient must be a related owner/assignee, an enabled System User, and have read access to the CRM Signal, every linked Lead/Customer, and the originating source document when present. If source DocType/name is partially populated, fail closed. Do not send a partial message that may still contain source data.
- **Rationale:** A notification is not an authorization grant. Requiring access to every record that can contribute content is safer than sending to a user who can read only one related record.
- **Consequences:** Users who can read a Lead but not its source Quotation/Opportunity will not receive that source-derived notification. Manual signals without a source link continue to use the linked party and CRM Signal permissions. Target-site permission parity must include source DocTypes.
- **Validation:** Regression tests cover a parent reader without source-document read permission and malformed partial source identity; Frappe v15/v16 CI is the merge gate.

## ADR-055 — Pin an exact Frappe v16.5.0 + Helpdesk compatibility lane

- **Status:** Superseded by ADR-056
- **Date:** 2026-11-02
- **Context:** The deployment owner confirmed Frappe v16.5 as the target. The existing CI matrix uses the moving 'version-16' branch, which verifies major-version compatibility but not the exact v16.5 patch or the installed Helpdesk schema. D3 depends on standard HD Ticket and HD Service Level Agreement metadata and Helpdesk field permlevels.
- **Evidence:** Frappe tag [v16.5.0](https://github.com/frappe/frappe/tree/v16.5.0) requires Python >=3.14,<3.15; ERPNext tag [v16.5.0](https://github.com/frappe/erpnext/tree/v16.5.0) supports Frappe >=16.0.0,<17.0.0; Helpdesk [v1.31.1](https://github.com/frappe/helpdesk/tree/v1.31.1) supports Frappe >=15.123.1,<17.0.0 and declares Telephony as a required app; Telephony commit [9447577500a25d242088398157b72c654fa34b20](https://github.com/frappe/telephony/commit/9447577500a25d242088398157b72c654fa34b20) supports Frappe through the v16 line. Helpdesk v1.31.1 defines status_category, resolution_date, resolution_time and sla at permlevel 7, and agreement_status at permlevel 8.
- **Decision:** Add a separate path-filtered Bench workflow pinned to Frappe v16.5.0, ERPNext v16.5.0, Helpdesk v1.31.1 and the exact Telephony commit above. Run it for application/test changes and manual dispatch, not docs-only changes. Keep the existing v15/v16 workflow and required-check contexts unchanged. The pinned workflow must install the real Helpdesk app and verify required DocTypes, field permlevels, Frappe's permitted-field API and default read-role boundaries at each relevant permlevel without reading ticket/customer records.
- **Consequences:** The exact lane provides reproducible framework/app compatibility evidence and catches Helpdesk schema or permission-level drift on code changes without adding the installation cost to docs-only pull requests. Existing v15/v16 required-check contexts remain unchanged. It is not proof that the pilot site uses these exact app versions or has the required Sales-role permissions, SLA calendar, timezone or customizations; record the site's observed versions and run the live acceptance checklist separately.


## ADR-056 — Pin the Helpdesk release that installs on Frappe v16.5.0

- **Status:** Superseded by ADR-057
- **Recorded:** 2026-11-02
- **Context:** The first exact-stack workflow failed before CRM Signals tests ran. Installing Helpdesk v1.31.1 on Frappe v16.5.0 reaches `helpdesk.setup.install.after_install`, then `setup_comments_and_notifications` / `add_notification_types`, which calls `frappe.get_doc({"doctype": "Notification Type", ...})`. Frappe v16.5.0 does not ship that DocType/controller, so controller resolution raises `ImportError: No module named 'frappe.core.doctype.notification_type'`. The newer moving Frappe `version-16` branch contains Notification Type under `frappe.desk`, but that is not evidence for the exact v16.5.0 tag. Helpdesk v1.30.2 does not run this post-install Notification Type setup and its standard HD Ticket/SLA schema contains the D3 fields.
- **Evidence:** Failed job [41360465445](https://github.com/MitMike/crm_signals/actions/runs/41360465445) log shows the full install stack and missing module. Frappe [v16.5.0 tree](https://github.com/frappe/frappe/tree/v16.5.0) lacks the Notification Type controller. Helpdesk [v1.30.2 setup](https://github.com/frappe/helpdesk/tree/v1.30.2/helpdesk/setup) installs without that step. Its HD Ticket fields `status_category`, `resolution_date`, `resolution_time`, `sla` and `agreement_status` are at permlevel 0; read roles are System Manager, Agent, Agent Manager, HD Customer and HD Customer Manager. HD Service Level Agreement read roles are System Manager and Agent Manager. Frappe v16.5.0 includes `Meta.get_permitted_fieldnames`.
- **Decision:** Keep the exact Frappe/ERPNext v16.5.0 lane, but pin Helpdesk v1.30.2 and verify its actual field/role contract. Do not patch the framework, monkey-patch Helpdesk, skip its post-install step, or weaken the real install check to force v1.31.1 through. Keep the D3 adapter permission-aware: on v1.30.2 the fields are permlevel 0, while the adapter must continue to honor whichever field permissions the installed Helpdesk version actually defines.
- **Rationale:** A reproducible installable stack is more useful than a nominal dependency range that fails in the real install path. The target-site operator must still capture the installed Helpdesk version; if the pilot has v1.31.1, treat it as a separate compatibility issue and do not assume the v1.30.2 lane proves it.
- **Consequences:** The pinned lane proves compatibility for Frappe/ERPNext v16.5.0 + Helpdesk v1.30.2 only. It does not prove the pilot site's Helpdesk version, permissions or SLA configuration. Revisit if Frappe v16.5.x patch versions or Helpdesk releases change the Notification Type dependency.

## ADR-057 — Pin the Helpdesk v16.5.0 reference below the framework UI dependency boundary

- **Status:** Accepted
- **Date:** 2026-11-02
- **Context:** The exact Frappe v16.5.0 tag does not contain the frappe/ui package directory. The inspected Helpdesk v1.29.0/v1.30.2/v1.31.1 desk packages link @framework/ui to ../../frappe/ui, but the unmodified Frappe v16.5.0 tag lacks that package directory. The exact v1.30.2 reference run fails when Helpdesk's after-migrate asset build resolves vite.config.js; v1.29.0 and v1.31.1 were not separately run. Helpdesk v1.31.1 also adds an install-time Notification Type dependency absent from the tag. The v1.28.0 Helpdesk tag retains all D3-required HD Ticket fields and SLA metadata at permlevel 0, supports Frappe >=15.109.0,<17.0.0, requires Telephony, and does not import @framework/ui in its desk build.
- **Decision:** Pin the exact Frappe v16.5.0 + ERPNext v16.5.0 compatibility workflow to Helpdesk v1.28.0 and the pinned Telephony commit. Do not patch upstream app code or skip Helpdesk asset hooks to make a mismatched stack pass. Keep the existing moving v15/v16 matrix and make the pilot operator record the exact installed patch/app versions.
- **Consequences:** The v1.28.0 reference validates the D3 adapter against a real compatible Helpdesk schema. If the pilot uses Helpdesk v1.29.0 or newer, verify that its exact Frappe build supplies the frappe/ui package; if it uses v1.31.1, also verify the Notification Type DocType/controller. Otherwise stop and resolve the upstream version compatibility before installing. The adapter continues to inspect actual field permissions rather than hard-code permlevels.
- **Evidence:** [Frappe v16.5.0 tree](https://github.com/frappe/frappe/tree/v16.5.0), [Helpdesk v1.28.0 desk package](https://github.com/frappe/helpdesk/blob/v1.28.0/desk/package.json), [Helpdesk v1.28.0 hooks](https://github.com/frappe/helpdesk/blob/v1.28.0/helpdesk/hooks.py), [Helpdesk v1.28.0 HD Ticket metadata](https://github.com/frappe/helpdesk/blob/v1.28.0/helpdesk/helpdesk/doctype/hd_ticket/hd_ticket.json), [Helpdesk v1.30.2 desk package](https://github.com/frappe/helpdesk/blob/v1.30.2/desk/package.json), [Helpdesk v1.31.1 install notification setup](https://github.com/frappe/helpdesk/blob/v1.31.1/helpdesk/setup/comments.py).


## ADR-058 — Persist recipient-scoped realtime notification attempts

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** Frappe v16 queues `publish_realtime(after_commit=True)` before Redis publication and suppresses Redis connection errors in the after-commit emitter. A synchronous try/except cannot detect those failures. Retrying without a stable identity can produce duplicate toasts, while marking a queued callback as delivered overstates the evidence.
- **Decision:** Persist one `CRM Signal Notification Delivery` row per signal/recipient pair, keyed by a deterministic SHA-256 ID. Store only the signal link, recipient and operational delivery state; do not copy message/source content. Re-resolve the eligible recipient set and re-check the existing CRM Signal, linked-party and source-document permissions before every publish attempt. Use bounded at-least-once retries with exponential backoff. Include the stable ID in the realtime payload and suppress duplicate IDs in the active Desk session. The `Attempted` state means only that Frappe accepted the after-commit publish callback; it is not proof of Redis delivery, browser receipt or human acknowledgement.
- **Rationale:** A durable per-recipient ledger makes unobservable Redis failures and worker restarts retryable without creating a second logical delivery. Permission revocation must stop later attempts.
- **Consequences:** Delivery may be attempted more than once. Client deduplication applies within the active browser session; it does not provide exactly-once or cross-device human delivery. The scheduler retries at most ten times with a 60-minute delay cap; exhausted rows become Failed, and rows whose recipient is no longer eligible become Cancelled.
- **Validation:** Bench tests cover stable identity, retry, publish failure/backoff, permission revocation and payload minimization; Playwright verifies duplicate-toast suppression. Pilot acceptance must still inject Redis unavailability and worker restart on the target site.


## ADR-059 — Ship Explorer first with verified core ERPNext adapters only

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** The Explorer specification calls for a Lead/Customer-centered timeline with explicit source adapters, stable event identity, deterministic pagination and source-record permission checks. The target site's installed Communication, Event, call and WhatsApp providers have not yet been inventoried. Guessing their DocTypes or fields would create false availability and could expose content outside the source application's permissions.
- **Decision:** Implement the first backend slice for the app's own CRM Signal plus standard ERPNext Quotation and Opportunity records. Support Lead, Customer, Opportunity and CRM Signal contexts; treat a High-Value Quote CRM Signal as the current Highlight context until H has a separate data model. Do not add Communication, Event, ToDo, call or WhatsApp adapters until their installed/configured providers and exact schemas are recorded from the target site. Use permission-aware `frappe.get_list` reads, check the linked party and each source record, and omit rows/links the current user cannot read. Return only metadata and short status/type summaries; never copy message bodies, amounts, recordings or attachments. Use source DocType + source document name as the stable event identity, order by creation then source/event ID, and use a bounded snapshot cursor with per-source offsets. Keep the API read-only and compatible with Frappe v15/v16.
- **Rationale:** The three initial sources are part of the already-supported CRM/ERPNext contract and can be tested on both supported framework lines without assuming optional integrations. A source that is absent or unreadable must remain visibly not connected/unavailable, not silently appear as an empty timeline.
- **Consequences:** This decision defines the core adapter/API scope. The Desk entry points and initial Lead-context Playwright flow are merged in PR #59; all-context browser coverage is tracked in PR #61. Optional activity integrations and target-site source inventory remain separate follow-ups. The cursor is bound to the context, page size and current user; it stabilizes ordering against new inserts but does not freeze source updates, deletions or permission changes. Every page re-resolves context and rechecks source permissions.
- **Revisit criteria:** Add an optional adapter only after the pilot operator records the installed app/provider, exact version, DocType, required fields, stable event ID, relationship mapping and permission contract in the target-site discovery record.


## ADR-060 — Enforce field-level read access in Explorer adapters

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** Frappe v15/v16 permission-aware `get_list` reads can silently omit fields that the current user cannot read at their configured permlevel. A DocType-level read check therefore does not prove that an Explorer adapter may use its relationship, filter or summary fields. ADR-052 established the same fail-closed rule for D3 Helpdesk metrics.
- **Decision:** Before resolving a context or querying a source adapter, inspect `Meta.get_permitted_fieldnames(user=frappe.session.user, permission_type="read")`. Every field used for context resolution, filters, source selection or summaries must be readable. If a context field is not readable, reject the context as unavailable; if a source field is not readable, mark only that source unavailable. Never use Administrator/system reads or infer a missing value. The CRM Signal adapter checks only the Lead or Customer relation field used by the current timeline, plus signal type and priority.
- **Rationale:** A field silently removed by Frappe is not a valid empty value. Explicit checks prevent misleading summaries and hidden-field inference while preserving independent sources the user can read.
- **Consequences:** A user may see a timeline with one source unavailable while other sources remain available. The target site's Sales User/Manager field-permission matrix remains a pilot acceptance requirement; no permission level is granted automatically.
- **Validation:** Bench tests cover unreadable Opportunity relationship fields, the High-Value Quote filter field, unreadable CRM Signal summary fields and party-specific relation selection. Retain the Frappe v15/v16 matrix and exact v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 reference lane.

## ADR-061 — Keep VIP escalation semantics and proposal tracking behind explicit approvals

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** The H specification defines a high-value Quotation alert, an admin-managed VIP Customer allowlist, escalation recipients and tracked proposal-link opens. The current product behavior implements the Company-currency quotation alert and the existing permission-filtered Lead/Customer owner and active-assignee recipients. It does not define whether VIP membership changes the threshold, creates an alert for every activity, changes recipients, or only scopes proposal-link tracking. Adding fields or routing rules without resolving this would silently invent business policy. Proposal-link tracking also introduces personal-data processing and retention obligations.
- **Decision:** Keep the current high-value Quotation behavior unchanged. Do not add a VIP allowlist or escalation-recipient field until the product owner approves (1) which events the VIP rule applies to, (2) whether VIP membership affects threshold or priority, (3) who receives escalation and whether it replaces or supplements current recipients, and (4) the cooldown/deduplication behavior. Do not implement or enable proposal-link tracking until the site owner/security/privacy approvers record the privacy notice, lawful basis/consent requirement, retained event fields, retention period, deletion process and scanner-classification policy. Never infer human intent from ambiguous or automated opens.
- **Rationale:** Alert routing is business behavior, and link tracking is privacy-sensitive. Safe code cannot compensate for missing policy decisions.
- **Consequences:** High-value Quotation alerts remain an independent implemented slice. VIP escalation and proposal-link tracking stay explicitly open; no extra Settings fields or link/event DocTypes are created prematurely.
- **Revisit criteria:** A signed product decision for VIP triggers and recipient routing, and an approved privacy/retention record for proposal tracking.


## ADR-062 — Keep Explorer authorization in the server API

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** The Explorer Desk page is visible only to the configured Sales User, Sales Manager and System Manager roles, but a whitelisted method can be called directly without opening that page. Hiding a page or button is not an authorization boundary. The timeline contains links and metadata derived from CRM Signal, Quotation and Opportunity records.
- **Decision:** Treat the Desk page role list as navigation and usability control only. The GET API remains the authorization boundary: authenticate the caller, resolve the context through permission-aware reads, require read access to every context/filter/summary field, and re-check permission on each source row before returning its metadata or link. Keep the API read-only; do not trust client-supplied source routes or use Administrator/system reads to fill gaps. The UI must escape every displayed value and navigate only using the authorized source DocType/name returned by the server.
- **Rationale:** A user can invoke a whitelisted endpoint independently of Desk navigation. Authorization must therefore be enforced on every request and every source record, not inferred from the page's role metadata.
- **Consequences:** Page-role visibility improves discoverability but does not replace DocType, field-level or row-level checks. Target-site Sales User/Manager and non-sales API tests remain required; no role or field permission is granted automatically.
- **Validation:** The API's context/source permission tests and the v15/v16 Bench plus pinned v16.5 reference lanes remain merge gates. The UI's escaped rendering, GET-only paging and source drill-down are covered by Playwright.


## ADR-063 — Gate Analysis and Vault on accepted metric and retention policy

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** Analysis (A) depends on a versioned registry derived from D1/D2/D3/H definitions, and its specification requires D1/D2 target-site reconciliation before the first catalog is exposed. Vault (V) depends on stable D1/D2 definitions plus an approved source-visibility and retention policy. CI fixtures prove code behavior on reference stacks; they do not establish the pilot site's finance semantics, reporting population or retention obligations.
- **Decision:** Do not expose Analysis query intents or enable Vault snapshot scheduling until D1/D2 definitions are reconciled against native ERPNext reports and signed by Sales/Finance, with currency basis, date windows, filters, groupings and source permissions recorded. Vault additionally requires an approved reporting population/source-visibility policy, explicit retention period, deletion/pruning owner, audit requirements and a tested dry-run boundary. After sign-off, build a versioned server-owned metric registry and deterministic intent templates; arbitrary generated SQL/Python remains prohibited. Register D3/H metrics only after their own source contracts are accepted.
- **Rationale:** A technically correct aggregate can still be semantically wrong for a site's accounting setup or expose data outside the approved reporting population. Retention is a policy decision, not a safe default.
- **Consequences:** A and V remain planned/blocked; no new query endpoint, snapshot DocType or scheduled capture is enabled by this decision. The existing D1/D2 dashboards remain independently usable subject to target-site acceptance.
- **Revisit criteria:** Attach signed D1/D2 metric definitions and native-report variance evidence, the approved source DocType/field permission matrix, currency/timezone semantics, and (for Vault) the retention/deletion schedule, responsible owner, audit record and dry-run pruning results.


## ADR-064 — Exercise D1/D2 aggregate query compatibility in Bench CI

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** D1/D2 unit coverage uses mocked Frappe APIs. The supported-version Bench workflow installs ERPNext on Frappe v15/v16, but did not explicitly execute the Sales Compass D1/D2 aggregate query path. The pinned v16.5.0 lane called the dashboard API only to assert D3 Helpdesk metrics, leaving ERPNext D1/D2 query compatibility implicit.
- **Decision:** Add a read-only CI smoke check that runs `get_sales_compass_data()` as Administrator after ERPNext installation on Frappe v15/v16 and the pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 lane. Assert that the Lead, Opportunity, Sales Invoice and Payment Entry metric sections and their required response shapes are available. Create no business records and perform no writes.
- **Rationale:** Real metadata and database aggregation queries catch schema/API incompatibilities that mocked tests cannot. Avoiding synthetic accounting documents keeps this check independent of company/account/customer setup and prevents it from being mistaken for a financial reconciliation.
- **Consequences:** This proves query-path compatibility on reference stacks only. It does not verify metric values, Sales User/Manager row or field visibility, custom workflows, currency conventions, or native-report reconciliation. Those remain target-site acceptance gates. A separate synthetic financial fixture may be added only when it can create valid, isolated ERPNext accounting records on both supported framework lines.
- **Revisit criteria:** Revisit when a reusable test fixture can provision an isolated Company, chart of accounts, Customer, Item, submitted Sales Invoice and Payment Entry on Frappe v15/v16 without depending on the target site's accounting setup. Then assert invoice/POS/receipt/receivable/overdue aggregation deltas and permission behavior; keep live financial reconciliation separate.


## ADR-065 — Avoid duplicate Bench runs on feature-branch pushes

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** The Bench matrix ran for both `push` and `pull_request` events on the same feature-branch commit. The duplicate runs competed under separate concurrency groups; repeated branch updates produced cancelled or stale required Bench contexts, as previously observed during Explorer integration and again while validating PR #63.
- **Decision:** Restrict the Bench Integration and E2E workflow's `push` trigger to `main`. Continue running it for every pull request and allow explicit `workflow_dispatch` on other refs. The pinned Frappe v16.5.0 workflow remains pull-request/path filtered and manually dispatchable.
- **Rationale:** One authoritative Bench run per PR head avoids duplicate database/app installs, reduces runner contention and prevents a push-triggered duplicate from cancelling the required PR context. Main still receives a Bench run after merge.
- **Consequences:** Feature-branch pushes no longer start a second Bench matrix; PR checks remain the merge gate. This changes CI scheduling only, not supported-version coverage.
- **Revisit criteria:** Revisit only if a separate branch-push validation requirement is introduced that is not already satisfied by pull-request checks or main-branch pushes.


## ADR-066 — Keep D2 source permissions independent

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** The D2 specification requires independent read-permission checks for Sales Invoice and Payment Entry. `_get_sales_billing_data()` returned as soon as Sales Invoice metadata/read access was unavailable, suppressing customer receipts even when the requesting user had Payment Entry read access. This contradicted the source contract and the UI's independently rendered metric cards.
- **Decision:** Evaluate Sales Invoice metrics and Payment Entry customer receipts independently. A denied or unavailable Sales Invoice source must leave invoice, POS, receivable and overdue measures unavailable, but must not prevent a permission-aware Payment Entry receipt query. If a Sales Invoice query raises `PermissionError`, clear any partial invoice results and continue with Payment Entry. Preserve the existing `billing.available` flag as the Sales Invoice source-availability indicator for compatibility; `customer_receipts_available` remains the receipt-card authority.
- **Rationale:** The two DocTypes are distinct sources with distinct permissions and currency semantics. Suppressing a permitted Payment Entry aggregate because a different source is denied hides authorized data; bypassing either source's permission checks would be unsafe.
- **Consequences:** A user may see customer receipts while invoice-related D2 cards show unavailable. No roles are granted, no cross-source join is added, and no financial calculation changes. Unit regression coverage runs in the supported Frappe v15/v16 test matrix.
- **Revisit criteria:** Revisit only if the D2 response schema or source model changes. Target-site Sales User/Manager permissions and native-report reconciliation remain separate pilot acceptance.

## ADR-067 — Verify D1/D2 aggregate values and source permissions with disposable Bench records

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** ADR-064's read-only query smoke proved D1/D2 schema compatibility but did not prove aggregate deltas, transaction-currency versus party-account-currency grouping, overdue selection, POS receipt filters or the independent Sales Invoice/Payment Entry permission contract. The earlier revisit condition is now addressable on disposable Bench sites: the CI workflow can complete the ERPNext setup wizard and provision a Company, chart of accounts, Customer, Item and submitted accounting documents on Frappe v15/v16 and the pinned v16.5.0 stack.
- **Decision:** Add a Bench-only synthetic fixture that runs the real D1/D2 API before and after creating one Lead, active and terminal Opportunities in two currencies, submitted Sales Invoices, an allocated Payment Entry and a POS-shaped invoice row. Assert exact aggregate deltas, currency groups, party-account-currency receivables, overdue drill-down and a dedicated user who can read Payment Entry but not Sales Invoice. Commit only the one-time ERPNext setup baseline; roll back every synthetic record and permission change. Model the POS aggregate fields directly and explicitly do not claim to test POS settlement or the accounting workflow.
- **Rationale:** Real DocTypes, MariaDB aggregation and Frappe permission checks provide stronger evidence than mocks while keeping all business records isolated from a target site. A USD invoice against the Company's INR receivable account verifies that invoice value and outstanding balance use different currency bases.
- **Consequences:** The fixture runs in the Frappe v15/v16 Bench matrix and the exact Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 lane. It is CI evidence for query values and DocType-level source permissions only; it is not a native-report reconciliation, POS workflow test, Sales User/Manager role approval or pilot sign-off.
- **Revisit criteria:** Revisit if supported ERPNext versions change the Sales Invoice/Payment Entry lifecycle, if the disposable setup cannot be rolled back cleanly, or if the D1/D2 response contract changes. Keep target-site finance reconciliation and role/field-permission acceptance open.

## ADR-068 — Provide a non-whitelisted, read-only target-site preflight report

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** The v16.5 operator kit requires a repeatable inventory of installed app versions, Company currencies and thresholds, workflow statuses, support DocTypes/fields, and static role permissions. The existing D3 worksheet script discovers support metadata but leaves most of the release preflight manual. The repository has no authorized target-site session, so no live configuration or permission result can be inferred here.
- **Decision:** Add a bench-execute-only diagnostic function that returns a bounded metadata/configuration report. It must not be whitelisted as an HTTP method, create/update/delete records, read Lead/Customer/ticket/invoice/payment rows, include API credentials or recipient email addresses, or change settings. Include installed app versions when importable, Company base currencies and configured threshold source/amount/currency, site timezone, configured Opportunity statuses and relevant DocType/field/permlevel metadata. Show static DocPerm role grants separately from effective user access; never present them as permission-parity proof.
- **Rationale:** A reproducible, metadata-only report reduces operator transcription errors without granting a new remote data-export surface or guessing site-specific policy. Explicitly separating static role grants from effective user checks prevents the report from being mistaken for acceptance evidence.
- **Consequences:** The command is available only to a Bench operator with server-side access. The output is an inventory aid, not a pass/fail certification; an authorized operator must still run the target-site persona matrix, native-report reconciliation, SLA calendar checks and operational rehearsal. The report exposes Company names and configured threshold amounts to the operator, so it must be reviewed and shared only through the site's approved channel.
- **Revisit criteria:** Revisit if a whitelisted self-service diagnostics endpoint is requested, if new data categories are proposed, or if the Frappe/ERPNext metadata APIs change. Any remote endpoint or expansion into transactional/customer data requires a separate security and privacy decision.

## ADR-069 — Expose High-Value Quote source links only after field and document permission checks

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** H-AC11 requires the CRM Signals Console to open the originating Quotation for a High-Value Quote signal. The current dashboard API returns only the signal and party context, so the Console cannot navigate to the source. Returning source names without checking the user's source-document access would disclose identifiers and could create a misleading link.
- **Decision:** Include source_doctype/source_name in the dashboard's recent-signal payload only when both CRM Signal source fields are readable by the current user, the row is a High-Value Quote sourced from Quotation, and the current user has read permission on that exact Quotation. Restrict this link behavior to Quotation; suppress source metadata for all other source types and on any permission/metadata error. The Desk client opens the Quotation through the normal Form route. If the source is not readable, retain the existing Lead/Customer/CRM Signal navigation fallback.
- **Rationale:** A source link is useful only when it points to the authoritative record the user is allowed to open. Fail-closed field and record checks avoid leaking source identifiers and preserve the existing party/Signal fallback.
- **Consequences:** No permissions are granted and no source content is copied into the dashboard payload. The server returns only the authorized Quotation DocType/name; Desk still enforces normal form permissions. Unit tests cover field and document permission denial; Playwright covers the user-visible source drill-down.
- **Revisit criteria:** Revisit if additional source DocTypes are approved for dashboard navigation, or if the CRM Signal source fields/permission model changes. Each new source type requires its own permission and navigation tests.


## ADR-070 — Exercise ERPNext POS settlement in the disposable D2 fixture

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** PR #67's POS-shaped invoice set persisted POS/payment totals directly. That proves the D2 aggregate filter but does not prove ERPNext's POS Profile, Mode of Payment, Sales Invoice submission and payment-allocation lifecycle.
- **Decision:** Extend the disposable Bench fixture with a real POS Profile and a company-specific Mode of Payment, then insert and submit an `is_pos` Sales Invoice through ERPNext's normal document lifecycle. Assert that ERPNext persists the invoice as submitted and that its calculated `paid_amount` settles `grand_total`. Keep all fixture setup and records inside the existing rollback boundary. Use a non-stock item and disable POS stock updates to isolate accounting/payment behavior.
- **Rationale:** Exercise the ERPNext accounting path that produces the aggregate fields rather than manufacturing those fields in test data.
- **Consequences:** Run the scenario on Frappe/ERPNext v15 and v16 and the pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 lane. This covers the POS invoice settlement lifecycle only; it does not simulate browser checkout, POS Opening/Closing sessions, cash drawers, inventory movements or target-site native-report reconciliation.
- **Revisit criteria:** Revisit if supported ERPNext versions change POS Profile, Mode of Payment or Sales Invoice payment allocation behavior, if fixture rollback is not complete, or if the D2 POS aggregate contract changes. Pilot reconciliation and real-user permission acceptance remain separate gates.


## ADR-071 — Stop speculative Playwright formatting retries after repeated CI failures

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** PR #71's new Playwright test failed the same Prettier check on three final-head attempts: `cbe8898` (Quality run `41441149766`), `007fcd4` (Quality run `41442386611`) and `047a903` (Quality run `41443643807`, failed job `125271378491`). Each failure names only `e2e/sahdev-dashboard.spec.ts`; JavaScript lint, Python unit tests and Semgrep checks passed on the failed heads. Two manual formatting revisions did not satisfy the formatter.
- **Decision:** Do not make further speculative formatting edits, bypass the Quality check or merge PR #71 while the required check fails. Keep H-AC11 code-complete but not CI-verified. Revisit only when the exact Prettier output can be obtained by running `npx prettier --write e2e/sahdev-dashboard.spec.ts` in a CI-equivalent environment or by retrieving an exact formatter-generated diff from CI. Apply that diff without unrelated changes, then rerun every required final-head context and the pinned v16.5.0 lane.
- **Rationale:** Repeated manual guesses have not made progress; a formatter-generated diff is the next evidence-bearing action.
- **Consequences:** The source link remains unmerged and unavailable on main until CI passes. Target-site Sales User/Manager/non-sales permission acceptance remains separate.
- **Revisit criteria:** An environment with the repository's locked Prettier 3.2.5 and Node version is available, or CI can expose the exact formatted file/diff. If neither is available, leave the PR blocked and continue with independent work.


## ADR-072 — Print exact formatter diffs when Quality formatting fails

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** PR #71's H-AC11 Playwright test failed Prettier on three source heads under Prettier 3.2.5. PR #15 then upgraded the locked development dependency to Prettier 3.9.10 and merged as `5fc32b0`; PR #71 was synchronized with that main commit as `966b833`, but Quality still reported only `e2e/sahdev-dashboard.spec.ts` as unformatted (runs `41448226026` and duplicate `41448219829`). The current environment has no network access to install the locked npm package, and the existing CI log does not include the formatter output.
- **Decision:** Keep `npm run format:check` as a blocking required check. Add a failure-only step to Quality that runs the same locally installed, lockfile-pinned Prettier against the checked tooling/E2E files and prints a unified diff for each mismatch. The diagnostic must not write or auto-fix files, change the required-check result, or bypass formatting. Apply the exact emitted diff to the source branch, then rerun every required final-head context and the pinned Frappe v16.5.0 lane.
- **Rationale:** The formatter itself is the source of truth. A deterministic diff from the exact installed package removes guesswork while preserving the existing merge gate.
- **Consequences:** Formatting failures become directly actionable in CI logs. H-AC11 remains code-complete but not CI-verified until the formatted source passes all final-head checks. This diagnostic does not imply pilot verification.
- **Revisit criteria:** Apply the diff from the first successful diagnostic run. Keep the formatter check blocking. If logs still omit the diff, inspect the diagnostic step's failure and use an artifact or CI-equivalent formatter environment; do not make manual formatting guesses.
- **Implementation update (2026-11-02):** The diagnostic ran on head `75d7ae9` and emitted exactly three Prettier 3.9.10 wrapping changes in `e2e/sahdev-dashboard.spec.ts`; the exact output was applied in commit `91fc89c`. PR #71 was synchronized with PR #14's globals update (`567f458`) as `09d49f3`, then passed all final-head Quality, Security, Python 3.10/3.11/3.12/3.14, Bench v15/v16 including Playwright, and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 checks. PR #71 merged as `c5720bf`.


## ADR-073 — Close duplicate POS/preflight documentation after consolidation

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** PR #72 proposed a docs-only reconciliation for PR #69 POS settlement and PR #70 preflight evidence. The same evidence was already carried in PR #71's documentation update, alongside the H-AC11 source-link decision. PR #72's ADR-069 number collided with the H-AC11 ADR-069.
- **Decision:** Keep the merged, consolidated documentation in PR #71. Preserve ADR-069 for High-Value Quote source-link authorization, ADR-070 for POS settlement, and ADR-068 for the read-only preflight report. Close PR #72 as superseded after PR #71 merges.
- **Consequences:** No POS/preflight evidence is dropped; the decision register remains uniquely numbered and the progress/follow-up records have one authoritative update.


## ADR-074 — Pin every target-site deployment to an approved commit

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** The administrator guide's first-install command cloned the moving `main` branch even though its later instructions required a pinned release revision. That inconsistency could make an installation differ from the revision reviewed by CI or recorded for rollback.
- **Decision:** First installations may clone the repository, but must immediately detach to the exact approved 40-character commit SHA, verify `rev-parse HEAD`, and run `bench setup requirements` against that pinned tree before `install-app` or migration. Upgrades must fetch the approved source, detach to the same kind of immutable SHA, verify `rev-parse HEAD`, and reconcile Python/Node requirements from the pinned tree before migration. Never deploy a target site from a moving branch.
- **Rationale:** A deployment must be reproducible, auditable and restorable to the exact source revision that passed the release gate.
- **Consequences:** The operator guide and deployment runbook now make commit pinning and SHA verification explicit. The target-site acceptance record must retain the verified CRM Signals SHA alongside exact Frappe/ERPNext/Helpdesk versions. This documentation change does not claim a target-site deployment or pilot verification.
- **Revisit criteria:** Revisit only when release automation publishes and verifies immutable, signed release tags; until then, use the approved full commit SHA.
- **Implementation gap identified (2026-11-02):** The merged first-install example still invokes `bench get-app` before checking out the approved SHA. Upstream Bench's `get-app` clones and immediately installs the editable Python package, runs `yarn install`, syncs app state and builds assets; a later checkout cannot undo those pre-pin side effects. Bench also names the clone remote `upstream` by default, while the merged upgrade command fetches `origin`; that remote name may not exist. Correct the sequence to clone directly into `apps/crm_signals` with `--origin upstream`, fetch through `upstream`, detach to the approved SHA, verify `rev-parse HEAD`, then run `bench setup requirements` and `bench build --app crm_signals`. Existing installations must inspect `git remote -v` and fetch from the actual configured remote. Bench's requirements setup discovers Frappe apps under `apps/` and installs from their checked-out trees. Do not treat the current first-install snippet as safe until this sequence is tested on the pinned v16.5 stack and supported v15/v16 lanes. Evidence reviewed: [Bench get-app/install implementation](https://github.com/frappe/bench/blob/develop/bench/app.py) and [Bench app discovery/requirements implementation](https://github.com/frappe/bench/blob/develop/bench/bench.py).


## ADR-075 — Make change-aware CI selection fail closed

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** PR #76 introduces path-aware test execution so documentation-only changes can avoid creating Frappe sites and workspace-only changes can avoid unrelated Python unit execution while retaining Bench validation for workspace metadata. A review of the initial workflow found that a failed path-detection job could leave an empty output, skip test execution and also skip the required gate's failure step. The initial Bench/pinned filters also omitted package manifests and packaging/configuration inputs that can affect asset builds or app installation. A second path audit found that CI workflow definitions, workspace metadata, and patch/fixture manifests also needed explicit coverage. A final-head run also showed Quality starting twice for the same feature-branch SHA: push run 41477934545 and pull-request run 41477940227.
- **Decision:** Preserve the existing required check names; run full Quality on main pushes and path-aware Quality on every PR, with the Quality push trigger restricted to main. Run the full Bench v15/v16 matrix on main pushes and manual dispatch. On PRs, run Python tests for Python/test/script/packaging changes, including MANIFEST.in and requirements files. Run Bench and the pinned Frappe v16.5.0 / ERPNext / Helpdesk lane for backend, DocType/Page/workspace JSON, public assets, tests, package manifests/lockfiles, requirements, app config, module metadata, patch/fixture manifests, and any .github/workflows/** change. If the path detector fails, the static lint job and every affected required Python/Bench gate must fail closed rather than treating an empty output as proof that tests are unnecessary. Keep Security scanning required on every PR.
- **Rationale:** Test selection may reduce redundant work, but uncertainty about changed paths must never reduce required coverage.
- **Consequences:** Docs-only changes may skip expensive execution only after a successful path scan. Workspace JSON, DocType/Page metadata, patch/fixture manifests, packaging inputs and every workflow-definition change retain the appropriate Bench and pinned-stack coverage; workflow changes also force the Python and JavaScript quality suites. Restricting Quality push events to main removes the duplicate full run on feature branches while preserving pull-request validation and full main validation. PR #76's initial head 0637298 passed its four workflows with Python/Bench execution skipped for its workflow/docs-only diff. Temporary PR #77's runtime-path head 96d0d56 ran and passed Python 3.10/3.11/3.12/3.14, Bench v15/v16 including v16 Playwright, and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0; PR #77 was closed unmerged after validation. The initial correction head 7e5e36b passed all four workflows, but a subsequent review found that only the first Python gate and first Bench gate explicitly failed on detector failure. PR #76 now adds the detector-failure condition to every Python and Bench required gate. The expanded selector set also forces all relevant suites when workflow definitions change and runs Bench/pinned validation for workspace and migration/fixture metadata. Fresh final-head CI is required before PR #76 can merge.
- **Revisit criteria:** Revisit if a runtime-sensitive path is omitted, detector failure does not fail the required context, skipped contexts remain pending, or measured lead time does not improve. Never remove required checks or bypass branch protection.


- **Implementation update (2026-11-02):** A second path audit found workflow definitions, workspace JSON and patch/fixture metadata were omitted from the selectors. PR #76 now includes `.github/workflows/**` in Quality Python/JavaScript, Bench and pinned selectors; includes workspace/JSON/patch/fixture metadata in Bench and pinned selectors; and includes MANIFEST.in/requirements in the Python selector. This deliberately runs the relevant full matrices for CI-definition changes. Static regression tests in `tests/test_static_contracts.py` now assert all four Python required gates and both Bench required gates fail closed, the workflow/packaging selectors are present, Frappe workspace/patch/fixture paths reach Bench and pinned CI, and full main/manual Bench execution remains configured. Final-head CI for this expanded selector set is pending. PR #85 merged the GME workspace label together with `tests/test_static_contracts.py`; all four workflows passed on final head `b09a0cb`. Because the PR changed both a Python/test path and workspace JSON, Python and Bench executed. This verifies the combined runtime/metadata route but does not prove the Python skip path. PR #89 is docs-only and is the clean validation case for confirming successful path detection skips Python/Bench execution while stable required contexts pass; workspace JSON must continue to trigger Bench and pinned validation.


- **Duplicate-run correction (2026-11-02):** On PR #76 head `473e372`, GitHub ran Quality twice for the same SHA: push run `41477934545` on `ci/change-aware-fast-gates` and pull-request run `41477940227`. The Quality workflow now triggers push only on `main`; pull_request remains enabled for all PRs. A static contract test asserts this trigger scope. The redundant in-flight push run could not be cancelled through the available repository actions; future feature-branch pushes will not start it.


## ADR-076 — Use GME CRM Signals as the workspace display name

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** The requested Desk workspace branding is GME CRM Signals, while the existing Frappe workspace displayed CRM Signals.
- **Decision:** Change only the workspace label and title to GME CRM Signals. Preserve the technical workspace/module/page identifiers, routes, icon, links and shortcuts; do not claim this creates or fixes a separate app-launcher tile.
- **Rationale:** The user-facing label can change without migrating identifiers or breaking existing navigation.
- **Consequences:** The workspace JSON and static contract test require both label and title to equal GME CRM Signals. The change does not alter application permissions, data or navigation targets. PR #85 final head `b09a0cb` passed Quality, Security, Bench v15/v16 and pinned Frappe v16.5.0; it merged as `5cc4308`.
- **Revisit criteria:** Revisit only if a separate launcher-tile requirement or a further branding change is approved.


## ADR-077 — Pin CRM Signals before Bench installs its dependencies

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** ADR-074 required a full approved commit SHA, but its first-install example called `bench get-app` before checking out that SHA. Bench's `get_app` implementation clones and immediately calls `App.install`; that installation performs an editable Python package install, installs Node dependencies, synchronizes Bench app state and normally builds assets before `get-app` returns. The later checkout therefore cannot make the initial install reproducible. Bench-created clones also use the remote name `upstream`, while the prior upgrade example assumed `origin`.
- **Decision:** For first installs, clone CRM Signals directly into `apps/crm_signals` with `--origin upstream`, fetch tags, detach to the approved full SHA and verify `rev-parse HEAD` before running `bench setup requirements crm_signals`, site installation, migration or asset build. The explicit app argument installs the editable package and Node dependencies from the pinned tree and synchronizes Bench app state. For upgrades, inspect the actual `upstream` remote, verify its repository URL, fetch tags, detach/verify the approved SHA, then run the same requirements command before migration/build. Do not use `bench get-app crm_signals` in this pinned procedure.
- **Rationale:** The first Python/Node install and asset build must use the same immutable source revision that passed review and CI; checking out a commit after Bench has already installed the moving branch is not sufficient.
- **Consequences:** The administrator guide, deployment runbook and target-site acceptance kit use the corrected order. Both supported-version Bench workflows now clone the checked-out CI revision locally, detach/verify `GITHUB_SHA`, and run `bench setup requirements crm_signals` before site install/migration. A static contract test protects the documentation and workflow order. This is CI procedure coverage, not a target-site deployment or pilot acceptance.
- **Sources:** [Bench app installation](https://github.com/frappe/bench/blob/develop/bench/app.py), [Bench get-app command](https://github.com/frappe/bench/blob/develop/bench/commands/make.py).
- **Revisit criteria:** Re-audit if the supported Bench versions change the `get-app` install sequence, remote naming, or `setup requirements <app>` behavior. Keep the v15, v16 and pinned v16.5.0 sequence tests passing; never restore a post-install SHA checkout.


## ADR-078 — Merge dependency updates only from current, fully verified heads

- **Status:** Accepted
- **Recorded:** 2026-11-02
- **Context:** Dependency PRs can retain green checks while their base branch advances. A green result on an old head does not prove that the proposed update integrates with current workflows, supported Frappe/ERPNext lines or the pinned Frappe v16.5.0 stack.
- **Decision:** Refresh and review dependency PRs one at a time. Merge only after inspecting the exact diff, confirming the PR is based on current `main`, and verifying every required Quality, Security, dependency-audit, supported-version Bench and pinned-target check on the final head. Keep packaging-tool range changes separate from GitHub Action version bumps and require package build/install evidence for them.
- **Rationale:** Isolated updates make regressions attributable and prevent stale CI evidence from being treated as current compatibility proof.
- **Consequences:** PR #7's `setup-uv@v7` update merged as `331492c` after all 18 final-head checks passed. PRs #8/#10 require a fresh base and checks; PR #9 additionally requires packaging compatibility validation. No failing or pending check is bypassed.
- **Revisit criteria:** Revisit if repository branch protection or the required check matrix changes. Do not relax final-head verification to reduce maintenance effort.


## ADR-080 — Refresh remaining maintenance work after setup-python merge

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** PR #94 merged to main as `926619b`, advancing the base while the flit-core and documentation reconciliation PRs were open.
- **Decision:** Recreate the isolated flit-core change against the new main head as PR #96 and rerun checks. Treat PR #93 as superseded. Refresh the maintenance status documentation against the same base. Require direct package wheel/sdist build and installation evidence for the build-system range change.
- **Rationale:** Checks on a stale base do not establish compatibility with current main. Package metadata changes require package-specific validation.
- **Consequences:** PR #8 and #94 are merged. PR #96 is pending final-head CI and packaging evidence. Target-site acceptance and dashboard visual UAT remain separate release gates.
- **Revisit criteria:** Main advances, checks fail or are cancelled, the diff changes, or packaging evidence identifies a compatibility issue.


## ADR-081 — Verify flit-core v4 package artifacts on supported Python boundaries

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** PR #96 widens the PEP 517 build requirement from `flit_core >=3.4,<4` to `>=3.4,<5`. The existing editable-install and Bench checks passed on the earlier PR head, but they did not explicitly prove that both distributable artifact formats build and install with the v4 backend.
- **Decision:** Keep the isolated dependency-range change and add a Quality workflow gate that installs flit-core v4, builds both wheel and sdist without build isolation, then installs each artifact in a clean virtual environment and imports `crm_signals`. Run this explicit artifact check on the minimum supported Python 3.10 and current matrix boundary Python 3.14. Retain the full Frappe v15/v16 Bench + Playwright matrix and the pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 lane.
- **Rationale:** Editable installation alone does not prove that wheel and source distributions contain an installable package. Testing both artifact forms with the intended backend on both Python boundaries closes that gap without changing runtime dependencies or Frappe compatibility policy.
- **Consequences:** PR #96 includes the package-artifact gate and the build-system range change. Only the refreshed final-head workflow results are valid merge evidence; prior PR #96 and superseded PR #93 checks are stale. Target-site and pilot acceptance remain separate.
- **Revisit criteria:** Revisit if flit-core v4 changes artifact layout/build behavior, the supported Python floor/ceiling changes, package metadata gains runtime dependencies, or either artifact fails to build/install/import on a supported lane.


## ADR-082 — Accept flit-core v4 after artifact and full-stack CI verification

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** PR #96 widened the build-system constraint to `flit_core >=3.4,<5` and added explicit v4 wheel/source-distribution compatibility tests. The change was isolated and refreshed onto main `b18f504` before final validation.
- **Decision:** Merge PR #96 only after every final-head check passed and the head remained current with main. The merge was performed with expected head `349bf71b0687c77e830fb8b054cedacabb16f61b`; GitHub confirmed merge commit `d0ab24b6a50184af99f4af638ae64ddd9a22d08a`.
- **Evidence:** All 20 final-head check runs succeeded: Quality lint/static and Python 3.10/3.11/3.12/3.14; Security/Semgrep; Python and npm dependency audits; Frappe v15/v16 Bench integration including v16 Playwright; pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. The explicit flit-core v4 wheel and sdist build/install/import checks passed on Python 3.10 and 3.14.
- **Consequences:** The package build-system range is CI-verified for both supported Python boundaries and the supported Frappe reference matrix. This does not establish target-site deployment or pilot acceptance. The open PR queue was empty immediately after merge.
- **Revisit criteria:** Revisit if the supported Python floor/ceiling, flit-core major version, package metadata/runtime dependencies, or supported Frappe/ERPNext matrix changes, or if downstream packaging/install evidence fails.


## ADR-083 — Protect dashboard horizontal inset with a browser regression test

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** BUG-2026-001 / FIX-2026-001 restored the CRM Signals dashboard's 24px desktop horizontal inset and retained a 12px mobile inset. The existing browser suite exercised dashboard data and navigation but did not assert the rendered wrapper geometry, leaving the specific regression unprotected.
- **Decision:** Add a Playwright test against the rendered `/app/crm-signals-dashboard` page. Assert computed left/right padding is 24px at a 1440px viewport and 12px at a 390px viewport. Keep the test on the existing Frappe v16 browser lane; do not create a separate visual snapshot baseline.
- **Rationale:** The regression is a deterministic CSS contract. Computed-style assertions directly fail if either horizontal inset is removed or changed, without introducing brittle screenshot diffs or requiring site-specific visual assets.
- **Consequences:** The browser suite now protects the exact desktop/mobile inset values. CI verification is separate from manual staging UAT; BUG-2026-001 / FIX-2026-001 remain UAT-pending until the approved site assets are rebuilt and screenshots are reviewed.
- **Revisit criteria:** Update the expected values only after an intentional layout change is approved and the desktop/mobile design is revalidated. Do not treat this automated check as pilot acceptance.


## ADR-084 — Route browser E2E changes through Bench validation

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** PR #100 added a Playwright regression test under `e2e/`. Review of the first PR check run found that the change-aware Bench selector covered `tests/**` and app paths but omitted `e2e/**` and `playwright.config.ts`. An E2E-only change could therefore pass lint/format checks while skipping the workflow that actually executes Playwright.
- **Decision:** Add `e2e/**` and `playwright.config.ts` to the Bench integration-change selector. Add static contract assertions that both paths remain covered. The existing Frappe v16 matrix continues to execute Playwright; the v15 job remains a non-browser integration lane. Keep the pinned v16.5.0 workflow scoped to application/runtime compatibility paths.
- **Rationale:** Browser tests must execute when browser tests or their runner configuration change. Formatting/linting alone does not prove the test runs or passes.
- **Consequences:** PR #100 made its own Playwright change trigger the v15/v16 Bench workflow, including the v16 browser suite. This path-selection correction is independently protected by a static contract test. Final head 50759954b8801fb8edd7194fea354c3521b457f1 passed all 18 check runs, including the v16 Playwright assertion, Bench v15/v16, Python 3.10/3.11/3.12/3.14, Semgrep and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation. PR #100 merged as 9c4febf8180ef295b48ea18b1ac5fddc164ff34f. This is reference-stack CI evidence, not staging visual UAT or pilot acceptance.
- **Revisit criteria:** Revisit if the browser suite moves, Playwright configuration changes location, or Bench job selection is redesigned. Any selector change must preserve a successful E2E-only trigger.


## ADR-085 — Prioritize staging acceptance over unapproved downstream feature expansion

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** The current application slices (D1/D2, D3, H-AC11 and Explorer) and the Frappe v16.5 reference stack have implementation and CI evidence. PR #100 closes the remaining automated dashboard-inset regression gap. The remaining release gates depend on an authorized target site: visual asset UAT, exact installed versions, effective permissions, finance reconciliation, Helpdesk SLA policy, operational recovery and rollback. Vault/Analysis, VIP escalation, proposal tracking and optional Explorer adapters also lack one or more approved business, privacy, retention or source contracts.
- **Decision:** Treat staging visual UAT and P0 target-site acceptance as the next highest-value work. Do not invent target-site values or expand downstream product slices until their documented metric, source, permission, privacy and retention prerequisites are approved. Continue only source-independent work that has a testable contract and does not require guessing site configuration.
- **Rationale:** More code cannot resolve unknown business semantics, permissions, data reconciliation or operational ownership. Keeping those gates explicit prevents reference CI from being misrepresented as pilot evidence and avoids enabling metrics or tracking without approved contracts.
- **Consequences:** The dashboard visual UAT procedure is documented in TARGET_SITE_ACCEPTANCE.md §11. Code and reference CI remain complete for the merged slices; pilot verification remains open. No target-site evidence is asserted by this ADR.
- **Revisit criteria:** Resume site acceptance when an authorized Frappe v16.5 staging window, named technical/business owners, approved full app SHA and test accounts are available. Resume a deferred feature only when its specific signed metric/source/permission/privacy/retention inputs are recorded and its product owner approves the contract.

## ADR-086 — Include the deployed CRM Signals source revision in read-only preflight

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** The target-site acceptance kit requires the exact deployed 40-character CRM Signals SHA. Operators currently have to run a separate Git command and transcribe its result, even though the read-only preflight already inventories installed app versions and site configuration. A branch name or package version is not an adequate deployment identity.
- **Decision:** Extend the server-side, non-whitelisted preflight to run the fixed read-only commands `git status --porcelain --untracked-files=all` and, only when the checkout is clean, `git rev-parse --verify HEAD` from the imported CRM Signals package directory. Bound each command with a five-second timeout. Report only a validated 40-character hexadecimal commit ID from a clean working tree. If Git, the checkout, or the revision is unavailable, or tracked/untracked changes exist, return an explicit non-success reason; never infer a SHA from a branch, tag, package version or CI baseline. Do not expose paths, stderr, environment variables or arbitrary command execution.
- **Rationale:** The deployed source revision is a release-critical acceptance datum. Capturing it in the same report reduces manual transcription and makes comparison with the approved release SHA deterministic without reading business rows or adding an HTTP endpoint.
- **Consequences:** The preflight report gains `framework.crm_signals_source`. Operators must stop the release check if the revision is unavailable or the checkout is dirty, and use the documented manual Git commands to diagnose the checkout. The report remains read-only and does not prove the revision is approved, deployed assets are current, or the site is pilot-accepted.
- **Revisit criteria:** Revisit if CRM Signals is distributed without a Git checkout, if the Bench app layout changes, or if Git is unavailable on a supported deployment. Any replacement must still return an exact, independently verifiable source revision without executing user-controlled commands.

## ADR-087 — Verify the preflight Git root belongs to CRM Signals

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** ADR-086 captures the deployed CRM Signals revision by running Git from the imported package directory. Git searches parent directories for a repository, so a clean Bench checkout nested inside another Git repository could otherwise report the parent repository's SHA as if it identified CRM Signals. That would make a syntactically valid but incorrect deployment identity.
- **Decision:** Before checking cleanliness or reading `HEAD`, run the fixed read-only command `git rev-parse --show-toplevel` from the imported package directory. Require the resolved Git top-level directory to equal the CRM Signals repository root derived from the imported package path. If it differs, report `repository_root_mismatch` and do not report a SHA. Retain the existing five-second timeout, fixed argument arrays, clean tracked/untracked status check, full 40-character SHA validation and non-disclosure behavior.
- **Rationale:** A release identity must identify the CRM Signals checkout itself, not merely any enclosing Git repository. Explicit root equality makes the preflight fail closed in nested or incorrectly installed layouts.
- **Consequences:** The preflight uses one additional bounded, read-only Git query. Tests cover a matching root and a parent-repository mismatch. The administrator guide explains the check and the new unavailable reason. This does not change supported Frappe versions or replace target-site acceptance.
- **Revisit criteria:** Revisit if the package moves to a different repository layout (for example, a `src/` layout), is installed without a Git checkout, or Bench app layout changes. Update the expected repository-root derivation and tests together; never accept an ancestor repository's SHA.
- **Verification:** PR #105 merged as `db958124bca6a6704a75f606629c22444716f5b9` from final head `fd2161dc933fbaf74fd5a50a5261e5f1501b283e`. All 19 final-head check runs passed, including Quality/Python 3.10–3.14, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. This is reference-stack CI evidence, not target-site or pilot verification.


## ADR-088 — Exercise enclosing Git repository rejection with a real repository

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** ADR-087's parent-repository regression test mocked the output of `git rev-parse --show-toplevel`. That proves the diagnostic rejects a mismatched root string, but it does not exercise Git's actual upward repository discovery from a nested app directory.
- **Decision:** Add a focused Python test that creates a temporary parent Git repository, creates a nested Bench-style `apps/crm_signals/crm_signals` package path without its own `.git` directory, makes an empty parent commit, and calls the real `_source_revision()` Git commands. Require `repository_root_mismatch` and no parent SHA. Retain the existing mocked tests for deterministic timeout, missing-Git, dirty-tree and malformed-output branches.
- **Rationale:** The risk is specifically Git's real parent-directory discovery behavior. A temporary repository test validates that behavior directly while remaining isolated, read-only with respect to the project checkout, and independent of any Frappe site.
- **Consequences:** The test adds no runtime behavior or external dependencies; Git is already present in the CI checkout environment and is a runtime prerequisite of this preflight feature. Python and Bench CI execute the regression on the supported matrix. This strengthens reference CI only; it does not establish target-site deployment or pilot acceptance.
- **Revisit criteria:** Revisit if the CI environment no longer includes Git, the Bench app/package layout changes, or the preflight stops invoking Git from the imported package directory. Preserve a real nested-parent test whenever root-discovery behavior changes.


- **Verification (PR #107):** merged as `a472f1981f758ce7b6233d95fc0682fe69d7a304` from final head `a47c3975eebe52dccb918a1056cf30d818cdcae4`. All 19 final-head check runs passed: Quality/Python 3.10–3.14, Security/Semgrep, Bench v15/v16 including v16 Playwright, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. The real temporary parent-repository regression executed in the supported Python/Bench CI. This is reference-stack CI evidence, not target-site or pilot verification.


## ADR-089 — Exercise real clean and untracked-dirty Git checkout states

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** ADR-086/087's source identity preflight is guarded by mocked clean and dirty status tests, while ADR-088 adds a real-Git parent-root mismatch test. The exact clean-SHA and untracked-file status behavior should also be exercised against Git itself, not only mocked subprocess output.
- **Decision:** Add a temporary-repository integration test that commits the CRM Signals package file, invokes the real `_source_revision()` helper and verifies the returned SHA equals Git's actual `HEAD`. Then add an untracked Python override and require `working_tree_dirty`; assert the dirty path runs root and status checks only and does not query `HEAD`.
- **Rationale:** The release identity is trustworthy only if real Git reports both the expected repository root and actual working-tree state. This closes the test gap around the production `--untracked-files=all` behavior without introducing runtime dependencies or site-specific assumptions.
- **Consequences:** Test-only change using Git already required by the preflight and available in the supported CI checkout. No application behavior, supported Frappe versions or target-site configuration changes.
- **Revisit criteria:** Revisit if the preflight command sequence, package layout or Git prerequisite changes. Preserve real clean, dirty-untracked and enclosing-parent repository tests whenever source identity logic changes.
- **Verification:** PR #109 merged as [`94d14f56a526670d2c0ecb150ab9f08b4f034389`](https://github.com/MitMike/crm_signals/commit/94d14f56a526670d2c0ecb150ab9f08b4f034389) from final head `d8b65eedc45c05947409f9781a9caaee848aa4ba`. All 18 final-head check runs passed: Quality/lint, Python 3.10–3.14, Security/Semgrep, Bench v15/v16 + Playwright, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. The real clean-SHA and untracked-dirty tests executed in the supported Python/Bench lanes. This is reference-stack CI evidence, not target-site or pilot verification.


## ADR-090 — Keep the README first-install procedure pinned before Bench setup

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** The root README still instructed operators to run `bench get-app ... --branch main`. That conflicts with the Administrator Guide and Deployment Runbook, which require the approved full commit SHA to be checked out before Bench installs the editable package, Node dependencies or builds assets. A later checkout cannot make an earlier mutable-branch install reproducible.
- **Decision:** Replace the README's moving-branch `bench get-app` example with the same first-install sequence used by the operator guide: clone directly into `apps/crm_signals` with the verified `upstream` remote, fetch, detach at the approved 40-character SHA, verify `HEAD`, and only then run `bench setup requirements crm_signals`, site installation, migration, asset build and restart. Link existing-install upgrades to the Administrator Guide and Deployment Runbook.
- **Rationale:** The repository's top-level quick-start must not contradict the release-safe procedure. Pinning before dependency setup prevents an unreviewed moving branch from being installed or built before the release SHA is checked.
- **Consequences:** README first-install guidance is deterministic and consistent with the detailed operator instructions. No runtime code, app behavior, dependencies or supported Frappe versions change. Extend the static operator-installation contract test to protect the README sequence. The actual sequence still requires a staging rehearsal.
- **Revisit criteria:** Revisit only if a supported Bench version provides a verified mechanism to pin the exact app revision before any dependency installation or asset build, or if the app distribution model changes. Test the replacement against the target Bench version and update README, Administrator Guide and Deployment Runbook together. Do not restore a moving-branch first-install example.
- **Verification:** PR #112 merged as [`d2e1d873a8f257545596379e179aeb3e4de40dd4`](https://github.com/MitMike/crm_signals/commit/d2e1d873a8f257545596379e179aeb3e4de40dd4) from final head `f68939ba5e2977ed62698e2a78084277fa091479`. All 18 final-head checks passed, including Quality, Python 3.10/3.11/3.12/3.14, Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. This is reference-stack evidence only; the target-site first-install/upgrade rehearsal remains required.


## ADR-091 — Describe the implemented standard Helpdesk adapter accurately

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** The beginner-friendly Support & SLA setup guide still told operators that CRM Signals would build a small adapter after they returned the discovery worksheet. The standard Frappe Helpdesk `HD Ticket` / `HD Service Level Agreement` adapter is already implemented and reference-stack tested. The discovery guide's custom-DocType FAQ also implied a custom adapter could be designed without explicitly requiring approval.
- **Decision:** Update the setup guide to state that the standard adapter already exists. Update the discovery FAQ to say custom/different ticket DocTypes are outside the standard adapter and remain unavailable until support, security and business owners approve a separate adapter scope, mapping and KPI semantics. Operators must compare installed versions, required fields, effective Sales field permissions, active SLA schedule, holidays, timezone and pause/resume semantics with the supported contract. If they match, configure and test the existing adapter on staging.
- **Rationale:** Operators should not believe D3 implementation is outstanding for standard Helpdesk or assume an arbitrary custom ticket source is automatically supported. This keeps implementation status distinct from target-site configuration and pilot acceptance.
- **Consequences:** Documentation and static-test change only; no runtime behavior, dependencies, schema or site settings change. D3 remains not pilot-verified until live role permissions, SLA calendar and metric outcomes pass.
- **Revisit criteria:** Revisit only when target-site metadata shows a different/custom ticket DocType or material schema/permission divergence, and support, security and business owners approve the mapping and KPI semantics. Do not promise a new adapter based on a DocType name alone.
- **Verification:** PR #117 merged as 93e7e16271d727476618b4981498ad901835bad4 from final head 2d7463f5e73bec3741ef9fb68d9b707b9bb1afc6. All 35 final-head checks passed, including Python 3.10–3.14, Quality, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation. This is reference-stack evidence only, not pilot verification.


- **ADR-091 CI triage:** the first final-head run exposed a second stale sentence in the setup guide's workflow list ("We build a small adapter for the support app actually installed") and an incorrect footer label. Python 3.11 and 3.12 each had 1 failure, 125 passes and 36 skips. The guide now describes validating/configuring the existing standard adapter, keeps custom sources behind separate approval, and uses the correct footer; the static test rejects both stale statements. Require a fresh full final-head matrix before merge.


- **ADR-091 second CI triage:** the next head's Python 3.11, 3.12 and 3.14 jobs each reported 1 failed, 125 passed and 36 skipped. The guide wording was correct; the static test still expected the obsolete phrase `separately scoped adapter change`. Update the assertion to the approved phrase `custom sources require separate approval and scope`; rerun the full matrix before merge. This was a test expectation mismatch, not a runtime defect.


- **ADR-091 final status:** the two early static-test failures were corrected and all 35 checks on PR #117's final head passed. The D3 setup/discovery guides and static regressions are merged; no runtime or site configuration changed. Keep custom ticket sources unavailable until separately approved. Target-site D3 acceptance remains required.


## ADR-092 — Add an optional effective-user permission probe to target-site preflight

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** The read-only target-site preflight reports static DocPerm rows and field permlevels, but those rows do not prove that the actual Sales User, Sales Manager, System Manager or non-sales test accounts are active, carry the intended role boundary, or can read the fields required by CRM Signals. The operator acceptance matrix still required manual inspection before running record-level checks.
- **Decision:** Add an optional `test_users` mapping to `get_site_preflight_report`, keyed only by the aliases `sales_user`, `sales_manager`, `system_manager` and `non_sales`. Require active, distinct, non-Administrator accounts and validate the expected role boundary. For each installed preflight DocType, use Frappe's `has_permission(..., user=..., throw=False)` and `Meta.get_permitted_fieldnames(user=...)` APIs to report DocType read access and the required fields' read access. Return aliases and boolean outcomes only; never return User names, email addresses, credentials or error text. If no mapping is supplied, report the matrix as unavailable rather than passing it.
- **Rationale:** The probe turns the static inventory into a useful, repeatable DocType/field-level check using Frappe's own permission APIs while avoiding disclosure of test identities. The signatures and field-permission methods exist on both supported Frappe v15 and v16 lines.
- **Consequences:** The report remains server-side, non-whitelisted and read-only. It does not inspect business-document rows and does not prove row-level User Permissions, ownership, document shares, list filters, API/report/export behavior or actual dashboard visibility; the controlled-record acceptance matrix remains mandatory. Dedicated synthetic accounts are supplied explicitly by the authorized operator, not discovered or selected automatically.
- **Revisit criteria:** Revisit if Frappe v15/v16 changes the `has_permission` or `get_permitted_fieldnames` contract, if the required profile/role policy changes, or if a security review identifies identity leakage. Keep row-level and end-to-end permission acceptance separate even if the API evolves.
- **Verification status:** PR #120 merged as `a778c47b5078ac69dd89bdcd3ecab41de09b8072` from final head `e95efccec019df3fbadd1703f34c5682340b7f58`; all 18 final-head checks passed, including Python 3.10–3.14, Quality, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. The optional probe remains code-complete and reference-stack CI-verified, not pilot-verified.


## ADR-093 — Exercise the effective-user preflight on real supported Frappe stacks

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** ADR-092's new permission probe had unit coverage using a mocked Frappe module. The existing Bench workflows installed real Frappe v15/v16 and the pinned v16.5.0 stack, but did not invoke the new optional probe with real User records. A mocked API signature cannot establish that the user-aware permission methods work on the supported runtime versions.
- **Decision:** Add a CI-only Bench helper guarded by `allow_tests`. It creates four disposable synthetic System Users with Sales User, Sales Manager, System Manager and Employee roles, calls the production `get_site_preflight_report(test_users=...)`, and asserts active accounts, role boundaries, complete boolean DocType/required-field outcomes for installed DocTypes, unavailable outcomes for absent DocTypes, no permission API errors and no User-identity disclosure. Invoke it in the Frappe v15/v16 Bench matrix and the pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 workflow.
- **Rationale:** This directly exercises the actual `frappe.has_permission(..., user=...)` and `Meta.get_permitted_fieldnames(user=...)` contracts on the runtime versions the project supports. The fixture uses only disposable CI sites and random throwaway passwords; it does not read or create business records.
- **Consequences:** CI now validates that the optional preflight can execute against real Frappe metadata and synthetic Users. The CI helper refuses to run unless `allow_tests` is enabled. The helper's test Users remain in the disposable CI site; no test accounts are added to a real deployment. This does not prove target-site row-level permissions, shares, list/API/report/export/dashboard visibility, business-role expectations or pilot acceptance.
- **Revisit criteria:** Revisit if Frappe changes either permission API, the CI site bootstrap changes, or `allow_tests` semantics change. Keep the helper isolated to disposable sites and retain the explicit guard. Do not use this smoke test as a substitute for authorized target-site acceptance.
- **Verification:** PR #120 merged as `a778c47b5078ac69dd89bdcd3ecab41de09b8072` after all 18 final-head checks passed. The real-Frappe helper ran successfully on Bench v15, Bench v16 and pinned Frappe v16.5.0. This validates API compatibility and output shape only; it does not establish target-site business-role expectations or row-level permission acceptance.


### ADR-093 CI triage — complexity guard

The first implementation head `51c8e6d` failed Quality lint with Ruff C901: `verify_effective_user_preflight` complexity 19 exceeded the configured maximum 15. The validation logic was split into profile-level and report-level helpers; the complexity rule was not weakened or suppressed. A fresh final-head matrix is required before merge.


### ADR-092 input-validation clarification

Only `None` or an empty dictionary represents an omitted optional user mapping. Falsey non-mapping inputs (for example an empty list or empty string) are rejected with `ValueError` rather than silently reported as “not supplied”; a regression test protects this fail-closed input contract.


### ADR-092 account-type boundary clarification

The optional permission probe now requires each supplied test account to be an enabled Frappe System User, not merely an enabled User with a matching role. Website Users are rejected before DocType checks because they do not have Desk access; the result reports `system_user` as a boolean and `user_type_not_system` without exposing account identity.



## ADR-094 — Add bounded synthetic-record list-visibility checks to preflight

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** ADR-092/093 verifies that explicit synthetic System Users are active, correctly profiled and have DocType/required-field read access. It does not exercise Frappe's row-filtered list query for a representative record, leaving the first row-level permission step to manual staging checks.
- **Decision:** Add an optional \`test_records\` mapping keyed by an already supplied profile alias, supported preflight DocType and non-sensitive label, with the exact synthetic record name as the input value. For each validated user, temporarily switch the Frappe session user and call \`frappe.get_list\` with an exact \`name in [...] \` filter, \`fields=["name"]\` and a bounded page size. Return only labels and visibility booleans. Missing and inaccessible records are indistinguishable and both return false. Restore the original session user in \`finally\`.
- **Safety limits:** accept only the known preflight business DocTypes (not the SLA policy DocType), labels matching lowercase snake case, at most 50 records per profile and 100 total. Never return record names, field values, raw exceptions or user identities. Skip queries when DocType read is denied or unavailable; report only exception type on query/session failure. The probe remains non-whitelisted and read-only.
- **Rationale:** this exercises Frappe's actual permission-filtered list API, including the DocType's configured User Permission/share/permission-query filters, without exposing business data or allowing arbitrary queries. It reduces manual setup work but does not replace direct form, REST API, report, export, print or dashboard acceptance.
- **Consequences:** operators must create dedicated synthetic records with known expected visibility and pass their names explicitly. The command can report actual list visibility, but the operator still compares it to the approved role/record matrix. A false result can mean either missing or denied; verify synthetic fixture existence through the controlled setup record. The real-Frappe CI fixture validates one System Manager-visible CRM Signal and rolls it back; it is compatibility evidence only.
- **Revisit criteria:** revisit if Frappe v15/v16 changes \`frappe.get_list\` permission behavior or \`frappe.set_user\` session semantics, if the preflight DocType allowlist changes, or if security review finds a data-exposure or session-restoration issue. Keep input bounds and identity/name non-disclosure tests.
- **Verification status:** PR #122 merged as `de16ead6ed2f155e83189196755048a264c2ec74` from final head `5339d7135ff87902974dc2d038051e101434389e`. All four final-head workflows passed: Quality/Python (41603744414), Security/Semgrep (41603744435), Bench v15/v16 + Playwright (41603744404), and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 (41603744511). The optional probe is code-complete and reference-stack CI-verified, not pilot-verified.


### ADR-094 CI triage — initial validator signature failure
The first Python matrix run found five failures in the new record-visibility tests because _validate_test_record_doctypes retained a stale total_records parameter after the count-accounting refactor. The call site had already moved to the return-value form. The helper signature was corrected; the failing head remains unmergeable until a fresh full final-head matrix passes.



### ADR-094 review hardening — restore after a partially failed user switch
A focused code review found that the first implementation returned immediately when `frappe.set_user(test_user)` raised. If that API mutated the session before raising, the original Bench command session could remain switched because the early return bypassed the restoration `finally` block.

- **Decision:** route both successful and failed user switches through one restoration `finally`; never return from the switch-error handler. If switching fails, mark every requested record as `session_switch_failed`, disclose only the exception type, and still attempt to restore the original session user.
- **Implementation:** add a regression where the fake `set_user` mutates `frappe.session.user` and then raises. Assert the original user is set again, no list query runs, the result is partial/fail-closed and neither record names nor exception messages are disclosed.
- **Revisit:** if restoration itself fails, keep the report partial with `session_restore` exception type and stop operator acceptance; do not fall back to direct mutation of Frappe's session object.
- **Verification:** the corrected final head `5339d7135ff87902974dc2d038051e101434389e` passed all four final-head workflows; PR #122 merged as `de16ead6ed2f155e83189196755048a264c2ec74`. The mutate-then-raise regression passed in the Python and real-Frappe Bench/pinned lanes. This remains reference-stack evidence, not pilot verification.


### ADR-094 final-head CI and merge record

- Quality/Python run `41603744414`: configured Python 3.10, 3.11, 3.12 and 3.14 test jobs plus lint/static checks passed.
- Security/Semgrep run `41603744435`: passed.
- Bench Integration and E2E run `41603744404`: Frappe v15/v16 integration passed; v16 Playwright passed.
- Pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 run `41603744511`: synthetic record visibility, D1/D2, D3, upgrade, assets and Bench tests passed.
- PR #122 merged as `de16ead6ed2f155e83189196755048a264c2ec74`. No target-site or pilot acceptance is implied.


## ADR-095 — Exercise Sales User record filtering through the preflight on real Frappe

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** PR #122's disposable real-Frappe fixture verifies that System Manager can list one synthetic CRM Signal through the new preflight. It does not invoke the preflight list probe for a Sales User whose linked-party visibility is restricted by a Frappe User Permission. The existing Bench permission test already creates the relevant Lead/User Permission/CRM Signal fixture and directly proves the underlying query boundary.
- **Decision:** Extend that existing Frappe integration test to call `get_site_preflight_report` with the Sales User and two synthetic CRM Signal records: one linked to a Lead excluded by the user's Lead User Permission, and one unlinked signal owned by that user. Assert the preflight reports the linked record as not visible and the unlinked record as visible, returns a definitive checked status, restores the original session user and discloses neither record names nor user identity.
- **Rationale:** This exercises the actual preflight code path against Frappe's `frappe.get_list` permission filtering and CRM Signals' `permission_query_conditions` hook on the supported runtime matrix. It closes the gap between the existing direct list-query test and the new operator probe without introducing a new fixture or weakening the expected access boundary.
- **Consequences:** Integration-test-only. No runtime, schema, dependency, metric or site configuration changes. Final-head Bench v15/v16 and pinned v16.5.0 workflows must execute the test before merge. The test remains reference-stack evidence, not pilot acceptance.
- **Revisit criteria:** If Frappe v15/v16 changes User Permission or `frappe.get_list` behavior, inspect the actual query hook and permission API. Do not substitute `frappe.get_all`, remove the denied linked-record assertion or infer target-site role behavior from CI.
- **Verification status:** PR #124 merged as [af94b14](https://github.com/MitMike/crm_signals/commit/af94b14038250b75ebc849e424779432d57dee98) from final head [0c7a6bf](https://github.com/MitMike/crm_signals/commit/0c7a6bfc77c3ee9df7189007c0326491906aca76). All four final-head workflows passed: Quality Checks (run 41614477641, configured Python 3.10/3.11/3.12/3.14 jobs and lint/static checks), Security Scanning/Semgrep (41614477907), Bench Integration and E2E (41614477805; Frappe v15 and v16 integration passed, with v16 Playwright passed), and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation (41614477749). The real-Frappe Sales User fixture confirmed a linked CRM Signal excluded by the Lead User Permission is not visible while an unlinked signal owned by the same user remains visible. The report returned checked status, restored the original session user and disclosed neither user nor record names. The test is reference-stack evidence only; it is not pilot verification.


## ADR-096 — Verify Frappe single-document and list API permission wrappers

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** PR #124 exercises the preflight's `frappe.get_list` path against a real Sales User User Permission, but target-site acceptance separately requires direct API reads. The supported Frappe v15/v16 `frappe.client.get` wrapper loads a document, calls `doc.check_permission()` and applies field-level read permissions; `frappe.client.get_list` delegates to permission-aware `frappe.get_list`.
- **Decision:** Reuse the existing disposable Sales User fixture with a Lead User Permission that allows one synthetic Lead and excludes another. As that user, invoke `frappe.client.get` for the CRM Signal linked to the restricted Lead and require `frappe.PermissionError`; invoke it for the unlinked owned signal and require a document result; invoke `frappe.client.get_list` for both names and require only the unlinked signal. Restore the original session user in `finally`.
- **Rationale:** Exercise Frappe's actual API method wrappers and the CRM Signal document/list permission hooks on the supported runtime matrix without introducing a separate fixture or using privileged `get_all` queries.
- **Consequences:** Integration-test only. The CI test calls the whitelisted Python functions directly; it does not validate HTTP authentication, cookies, routing, reverse-proxy behavior or browser form loading. Those remain staging checks. No runtime, schema, dependency, metric or site configuration changes.
- **Revisit criteria:** If Frappe v15/v16 changes the `frappe.client.get` or `get_list` wrapper contracts, inspect the exact versioned implementation and update the regression without weakening the denied/allowed record boundary. Do not replace the API wrappers with `get_all` or use Administrator credentials.
- **Verification status:** corrected final head `24d12acb50613c25f71fc2d809b464e311ba7f3e` passed all four required workflows and PR #126 merged as `812aa1eb76fbabc0e7f73a664caa72a1e208feb6`. Quality/Python `41634012616`, Security/Semgrep `41634012907`, Bench v15/v16 + Playwright `41634012673`, pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 `41634012853`. The initial session switch is inside `try/finally`; all linked-denied/unlinked-allowed assertions passed. Reference-stack CI-verified, not pilot-verified.


### ADR-096 CI triage — Ruff import ordering

The first Quality lint run on head `a5998ec` failed only on Ruff `I001` for a local `frappe.client` import. Move `get`/`get_list` imports into the module's existing guarded Frappe import block so non-Bench unit environments still skip the integration class cleanly. Keep Ruff enforcement unchanged and rerun the full final-head matrix. If the import issue recurs, apply Ruff's exact import ordering; if the real-Frappe API methods differ, inspect v15/v16 implementations without weakening the expected denied/allowed boundary.


### ADR-096 CI triage — second Ruff import-order failure

The first correction moved aliased API imports into the guarded Frappe import block but Quality Checks on head `97ac553` still failed Ruff `I001` at that block. Replace the aliases with `import frappe.client` and call the module functions directly. Preserve the `ModuleNotFoundError` fallback and Ruff enforcement. If the rule still fails, obtain the exact Ruff 0.8.1 `--fix` diff rather than guessing a third import arrangement.


### PR #126 review correction — restore session when the initial user switch raises

- **Finding:** final-head CI passed, but review found the API helper called `frappe.set_user(test_user)` immediately before its `try`. If that call changed session state and then raised, the `finally` restoration would not run.
- **Decision:** move the initial user switch inside the existing `try`, so every attempted switch is covered by restoration. Keep the original user captured before the switch and retain the denied/allowed API assertions.
- **Status:** the prior head `30a3890a994a3402b4efdf15732843f86a62b789` passed all four workflows (Quality/Python, Semgrep, Bench v15/v16 + Playwright, pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0). This correction creates a new head and requires a fresh complete matrix before merge.
- **Revisit criteria:** if the new matrix fails, inspect the exact v15/v16 API wrapper and session behavior. Do not move the switch back outside the `try`, bypass permissions, or weaken the linked-denied/unlinked-allowed assertions.


### ADR-096 final-head CI and merge record (2026-11-03)

- Corrected final head: `24d12acb50613c25f71fc2d809b464e311ba7f3e`.
- Quality Checks `41634012616`: lint/static and Python 3.10/3.11/3.12/3.14 passed.
- Security/Semgrep `41634012907`: passed.
- Bench Integration and E2E `41634012673`: Frappe v15/v16 integration passed and v16 Playwright E2E passed.
- Pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 `41634012853`: installation, effective-user permission checks, D1/D2, Helpdesk schema/read-role, D3 aggregate, upgrade, assets, Python and Frappe integration steps passed.
- PR #126 merged as `812aa1eb76fbabc0e7f73a664caa72a1e208feb6`. The merge commit has no separate combined-status entries; verification is the four completed PR final-head workflows.
- Scope remains integration-test and operator-documentation coverage. Direct HTTP authentication/routing and browser form acceptance remain staging checks; no pilot verification is implied.


## ADR-097 — Make authenticated Sales User HTTP permission acceptance reproducible

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** ADR-096 and PR #126 exercise Frappe's Python method wrappers under a real Sales User in Bench CI. The target-site checklist named the HTTP GET endpoints but did not provide complete query parameters, credential-identity validation, exact expected statuses or secret-safe evidence handling.
- **Decision:** document a copy/paste Bash/curl/Python standard-library smoke check for the canonical HTTPS staging URL. Before permission assertions, call `frappe.auth.get_logged_user` and require the returned identity to match the explicitly supplied dedicated synthetic Sales User; reject Administrator. Call `frappe.client.get` for the linked restricted signal and require HTTP 403; call it for the unlinked owned signal and require HTTP 200 with the exact synthetic document name; call `frappe.client.get_list` for both and require a 200 response containing only the unlinked record.
- **Safety:** read API credentials without echo; write the Authorization header only to a mode-0600 temporary curl config; do not follow redirects; keep response bodies in a mode-0600 temporary directory; remove secrets and response files on exit; print only identity-match and pass/fail outcomes, never names, raw response bodies or secrets.
- **Consequences:** documentation-only. The procedure verifies HTTP authentication/routing and method response behavior only when actually run against the authorized target site. It does not prove browser form, REST resource, report/export/print/dashboard or broader pilot acceptance. No runtime, schema, dependency or site configuration changes.
- **Revisit criteria:** if the pinned Frappe build returns a different documented status or response shape, capture sanitized status/error class and exact build, inspect the versioned wrapper/authentication behavior, and revise the procedure without Administrator credentials or weaker permission expectations.


### ADR-097 documentation verification — PR #128 merged (2026-11-03)

- PR #128 merged as `85c492ea2c84444d7cc45c0d61706736fa972a83`.
- Quality Checks `41639851748`: Python 3.10/3.11/3.12/3.14 and lint/static checks passed.
- Security/Semgrep `41639851870`: passed.
- Bench Integration/E2E `41639851663`: path selectors passed; Bench runtime was correctly skipped for documentation-only changes. No pinned Frappe workflow was triggered.
- The embedded Bash procedure passed `bash -n`. ShellCheck was not installed; no ShellCheck result is claimed.
- A local fake-curl harness exercised the script's control flow and request arguments: authenticated identity 200, linked restricted get 403, unlinked owned get 200, and list containing only the unlinked record all passed. This is a transport mock only; it does not establish real HTTP/Frappe behavior.
- This verifies documentation syntax, a local mocked execution and repository checks only. The HTTP procedure has not been executed against a target site; not pilot-verified.


## ADR-098 — Exercise Sales User record permissions through browser-session HTTP on the pinned target

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** ADR-096's Bench test calls `frappe.client.get` / `get_list` Python wrappers directly; ADR-097 documents a separate API-token HTTP check for operators. The existing Playwright suite only checked dashboard access and did not prove these permission boundaries over a real browser session cookie. The pinned Frappe 16.5.0 workflow did not run Playwright.
- **Decision:** extend the disposable E2E site bootstrap to create two Leads (one allowed by a Sales User Lead User Permission, one restricted), a linked CRM Signal owned by the Sales User and an unlinked CRM Signal owned by the same user. Verify the fixture's permission-filtered list result before browser tests. In Playwright, discover the synthetic records as Administrator, switch to the dedicated Sales User, then call `frappe.client.get` and `frappe.client.get_list` through same-origin `fetch` with browser session credentials. Require linked get HTTP 403, unlinked get HTTP 200 with the expected name, and list output containing exactly the unlinked signal. Run the same E2E suite on Frappe v16 and pinned Frappe 16.5.0.
- **Rationale:** this tests actual HTTP routing, session-cookie authentication and method response mapping without placing API secrets in CI or weakening the linked-party permission boundary. The fixture is disposable and test-only.
- **Consequences:** test/workflow-only. No runtime, schema, dependency or site configuration changes. It does not test API-token authentication, reverse-proxy behavior on a target site, browser form rendering, REST resource endpoints, reports/exports/print/dashboard or production acceptance.
- **Revisit criteria:** if the restricted record returns anything other than 403 or appears in list results, inspect the exact Frappe build's User Permission and CRM Signal query conditions; do not use Administrator for Sales User assertions. If pinned E2E exceeds 60 minutes, profile setup, install and browser steps before extending the timeout.


### ADR-098 implementation review note (2026-11-03)

The first Quality run flagged `_prepare_e2e_sales_user_permission_fixture` at 102 non-blank lines against the repository's 100-line hard limit. The setup was split into `_ensure_e2e_lead`, `_ensure_e2e_signal` and the smaller fixture coordinator. The next Quality run passed Ruff/code standards and Python but failed Prettier formatting in `e2e/sahdev-dashboard.spec.ts`; the exact formatter diff was applied. No threshold or formatter check was changed or suppressed; corrected final-head checks are required before merge.


### ADR-098 workflow reproducibility correction (2026-11-03)

- **Finding:** the new pinned-target Playwright step installed the repository's locked Node dependencies with `npm install`, while Stage 0 and Quality Checks require lockfile-enforced `npm ci`. This made the new integration lane less reproducible than the existing validation policy.
- **Decision:** use `npm ci --ignore-scripts --no-audit --no-fund` before the explicit `npx playwright install --with-deps chromium` step. Preserve script suppression and the committed package-lock; do not relax the repository's deterministic-install rule.
- **Documentation cleanup:** remove the duplicated ADR-098 decision block, retaining one canonical decision and its implementation/verification notes.
- **Regression guard:** add a static contract test requiring the pinned workflow to use `npm ci` before the explicit Playwright browser installation and rejecting `npm install` in that workflow.
- **Verification:** the prior PR head `7bd1837e39b994daae04158eff5a1559fe48f4d8` had Quality and Security passed while Bench v15/v16 and pinned v16.5.0 were still running. This workflow correction creates a new head; all four final-head workflows must pass again before merge. Not pilot-verified.
- **Revisit criteria:** if `npm ci` reports a package/lock mismatch, repair and commit the lockfile in a separate focused change; do not revert to an unlocked install. If the pinned browser job exceeds the documented 60-minute threshold, inspect job-step durations and logs before changing timeouts.


### ADR-098 ephemeral E2E credential masking correction (2026-11-03)

- **Finding:** the pinned workflow generated random Sales User and Employee passwords and passed them as step outputs, but did not register the values with the GitHub Actions log masker.
- **Decision:** generate each value once, issue `::add-mask::` for both values before writing either to `GITHUB_OUTPUT`, then pass them only through the existing step/job environment. Keep the credentials ephemeral and do not print them.
- **Regression guard:** the static workflow contract now checks that both generated credentials are masked before their step outputs are written, in addition to requiring lockfile-enforced `npm ci`.
- **Verification:** this creates a new PR head and requires fresh Quality/Python, Security, Bench v15/v16 + Playwright and pinned v16.5 Playwright checks. Not pilot-verified.
- **Revisit criteria:** if workflow structure changes, keep masking before output propagation; never log credentials or move them into repository variables/secrets.


### ADR-098 static-test formatting triage (2026-11-03)

The first final-head Quality run after adding the workflow regression guard is expected to enforce the repository's 88-character Python line limit. A newly added split expression was 92 characters; it has been wrapped without changing assertions. Keep Ruff enforcement unchanged and require a fresh final-head Quality run.


## ADR-099 — Accept both Frappe login POST routes in Playwright

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** PR #130's first final-head matrix passed Quality Checks, Security/Semgrep and the Frappe v15/v16 Bench + Playwright workflow, but the pinned Frappe 16.5.0 workflow failed its focused Playwright test before reaching the permission assertions. The trace shows the login form submitted POST /login and successfully established an Administrator session; the shared Playwright helper waited only for POST /api/method/login, so it timed out despite the successful login.
- **Decision:** identify the login response by POST method and accept either /login or /api/method/login. Parse the response URL pathname rather than matching an arbitrary substring. Preserve the existing response-success, authenticated-session-cookie and post-login navigation assertions.
- **Rationale:** Frappe v16.5's observed login route differs from the route used by the supported moving v16 lane. The test helper must model both supported routes without weakening authentication or permission assertions.
- **Regression guard:** add a static contract test requiring both exact pathnames and the POST-method check.
- **Scope:** Playwright test harness and static regression only; no production runtime, schema, dependency or site configuration change.
- **Evidence:** workflow run 41643473834, job 125943109815, failed only at the focused Playwright login wait after site setup, migration, preflight, D1/D2, Helpdesk, Python and Frappe integration steps passed. The trace network log records POST http://test.local:8000/login with HTTP 200; no matching /api/method/login response occurred.
- **Revisit criteria:** if the new test still times out, inspect the next final-head Playwright trace and verify the exact POST pathname and status. Do not remove the response wait, bypass login, reuse Administrator for Sales User assertions, or weaken the expected linked-denied/unlinked-allowed results. Require all four final-head workflows before merge.



## ADR-100 — Verify the authenticated Sales User identity with the stable session endpoint

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** The corrected PR #130 head b6128589c40d3b2c7bedf639cc62d1ab3bd16f77 passed Quality/Python, Security/Semgrep and the supported Frappe v15/v16 Bench + Playwright workflow. The pinned Frappe 16.5.0 job completed site setup, preflight, D1/D2, Helpdesk, schema upgrade, E2E fixture creation, asset build, Python tests, Frappe integration tests, browser installation and server startup, then failed before the permission assertions at expect(roles).toContain("Sales User"). The helper queried frappe.core.doctype.user.user.get_current_user_roles and received an empty array on the pinned build. This was not a login failure or a linked-record permission assertion.
- **Decision:** remove the version-sensitive role lookup from the browser test. During server-side E2E fixture preparation, explicitly require Sales User in frappe.get_roles(sales_user). After browser login, call frappe.auth.get_logged_user through the same-origin session and require its exact result to equal the configured synthetic Sales User email before issuing the restricted/allowed document and list requests.
- **Rationale:** the fixture owns role assignment and can validate it directly using Frappe's permission/user API. The browser assertion should validate the authenticated session identity using the same endpoint already used by the operator's HTTP acceptance procedure, avoiding a second role-discovery endpoint whose response differed on Frappe 16.5.
- **Scope:** CI fixture and Playwright test only. No production runtime, schema, dependency or site configuration changes.
- **Revisit criteria:** if the server-side role check fails, inspect the fixture's User role rows and frappe.get_roles result on the exact Frappe build. If the browser identity endpoint fails or returns another user, inspect login response, session cookie and request routing; do not remove the identity assertion, use Administrator for Sales User permission requests, or weaken the linked-denied/unlinked-allowed/list-only-unlinked expectations. Require all four final-head workflows before merge.
- **Verification status:** correction committed on PR #130; fresh Quality/Python, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 Playwright workflows are required. Not pilot-verified.



### ADR-100 CI triage — stale non-sales role helper reference

The first correction removed the version-sensitive currentUserRoles helper and changed the Sales User test to verify frappe.auth.get_logged_user. Quality's Python 3.12 run 41663119127 then failed the new static contract because the new HTTP permission test and the existing non-sales dashboard test still referenced the removed helper. The first broad replacement had updated the earlier Sales User dashboard test rather than the new HTTP test; follow-up converted the Employee test, and final review found one remaining reference in the new HTTP test. The failure occurred in tests/test_static_contracts.py:448; 141 tests passed and 36 were skipped. No browser permission assertion ran in this Python failure.

- **Decision:** use the same authenticated identity endpoint in the non-sales browser test and assert the exact configured Employee email. Enforce the fixture's Employee-only role boundary server-side with frappe.get_roles; also reject Sales Manager/System Manager roles on the Sales User fixture.
- **Revisit:** if fixture role validation fails, inspect the User role rows on the exact Frappe build. If identity validation fails, inspect the session cookie and frappe.auth.get_logged_user response. Keep the identity assertion and the 403/200/list-only-unlinked permission checks; do not use Administrator for Sales User requests.
- **Status:** corrected code and regression tests committed; all four final-head workflows must rerun. Not pilot-verified.



### ADR-100 final code review — remaining HTTP-test role lookup removed

After the static regression exposed stale currentUserRoles references, a full-file inspection found one remaining call in the new Sales User HTTP permission test. The earlier replacement had changed the separate Sales User dashboard test; the Employee test was converted in the follow-up, but the new HTTP test still needed the same identity assertion. Replaced that final call with frappe.auth.get_logged_user and exact synthetic Sales User email equality. The server-side Sales User/Employee role guards remain authoritative for fixture role boundaries. Fresh final-head checks are required.

## ADR-101 — Use a deterministic CI-only non-sales Desk role

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** PR #130's final-head Quality and Security checks passed on head `7525c1521835e93245faf5840c0af1c47f9d590b`, but the pinned Frappe 16.5.0 job `41663853279` and supported Frappe v16 Bench job in run `41663853266` both failed during `prepare_e2e_site` at the assertion that the synthetic Employee account had an active Employee role. All earlier setup, permission preflight, D1/D2, Helpdesk and schema-upgrade steps passed. The logs did not emit the effective role set, so the exact role-removal mechanism is not claimed.
- **Decision:** create or normalize a dedicated CI-only Role named `CRM Signals E2E Non-Sales` with `desk_access=1`, `is_custom=1` and `disabled=0`; assign it to the synthetic non-sales System User and require that role in `frappe.get_roles`, while rejecting Sales User, Sales Manager and System Manager. Keep the account's browser identity assertion and all Sales User permission outcomes unchanged.
- **Rationale:** a custom role under test ownership is deterministic across the supported v15/v16 and pinned v16.5 reference stacks; a built-in ERPNext Employee role may be affected by installed-app/domain configuration and is not necessary to prove that a non-sales Desk user cannot access the Sales-only dashboard.
- **Scope:** disposable CI fixture and static regression only. No production runtime, schema, dependency, permission, metric or site configuration changes. The operator's target-site non-sales account remains site-approved and is not required to use this CI-only role name.
- **Revisit criteria:** if the custom role is not present in the effective role list, inspect the exact Role metadata and Has Role rows on each failing version, including disabled and Desk-access flags. Do not replace the non-sales account with Administrator, remove the role assertion, or weaken the linked-record denial / unlinked-record access / filtered-list checks.
- **Verification status:** correction committed as `eb55ca526811673f46466ea55a90136fa1c97010` and static guard as `1e7c911dbf9f28efec87ed933630217336b5486c`. Fresh final-head Quality/Python, Security, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 checks are required. Not pilot-verified.

### ADR-101 verification — PR #130 merged (2026-11-03)

PR #130 merged as `2b697b4d37a12b2e339bcf680ff808f23b97850f` from final tested head `42f8a38e751977e21168869c4010fcce901309ac`. Quality/Python `41668745943`, Security/Semgrep `41668745937`, Bench v15/v16 + Playwright `41668746054`, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 `41668745681` all passed. The deterministic non-sales role fixture and the Sales User linked-denied/unlinked-allowed/list-only-unlinked browser assertions passed in the final-head matrix. Reference-stack CI verification only; not pilot verification.

## ADR-102 — Verify direct CRM Signal form loading under Sales User permissions

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** PR #130 verifies `frappe.client.get` and `frappe.client.get_list` over an authenticated browser session. The Desk form uses a separate loader: on Frappe v16, `frappe.model.with_doc` issues GET `frappe.desk.form.load.getdoc`; the server loads the document, calls `doc.check_permission("read")` and applies field-level read permissions before adding the document to the response. This path was not covered by the previous browser test.
- **Decision:** navigate as the synthetic Sales User to the direct CRM Signal route `/app/crm-signal/<name>`. For the CRM Signal linked to a Lead excluded by the user's Lead User Permission, require the form-loader GET to return 403 and the restricted message not to appear in the response. For the unlinked CRM Signal owned by the same user, require 200 and verify the expected message is present in the loaded document. Run the test in the supported v16 Playwright lane and the pinned Frappe 16.5.0 lane.
- **Rationale:** exercise the actual browser route and Frappe form-loader permission boundary rather than inferring form behavior from the generic document API wrapper or the Desk shell response.
- **Consequences:** disposable CI fixture and operator-guide coverage only. No production runtime, schema, dependency or site configuration changes. API-token authentication, report/export/print/dashboard and target-site acceptance remain separate.
- **Revisit criteria:** if the route or loader method changes on supported v15/v16, inspect the exact Frappe router and loader implementation and retain the linked-denied/unlinked-allowed assertions. Never treat the Desk shell's HTTP response as proof that the document loaded, and never use Administrator for the Sales User assertions.
- **Verification status:** PR #131 merged as `08f269cdfaedc58fd4ce396c823d589e7dd3481b` from final head `a72ebffbae116adf06830473bb15d764a169651b`; all four required workflows passed. The direct form-loader test passed in the supported v16 18-test Playwright suite and pinned v16.5 three-test Playwright selection. Reference-stack CI-verified, not pilot-verified.

## ADR-103 — Enforce lockfile-based npm installation in every Bench E2E lane

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** PR #130 corrected the pinned Frappe 16.5.0 workflow to use `npm ci`, but review of the supported Frappe v15/v16 `bench-e2e.yml` lane found it still used `npm install`. That allowed the two browser-test lanes to resolve different dependency trees despite sharing the same committed package lock.
- **Decision:** use `npm ci --ignore-scripts --no-audit --no-fund` before Playwright browser installation in both supported v15/v16 and pinned Frappe 16.5.0 workflows. Extend static regression coverage to require the lockfile command, reject `npm install`, and verify generated Sales User/Employee passwords are masked before being written to GitHub step outputs in both workflows.
- **Rationale:** the browser tests should execute against the exact committed dependency graph on every supported reference lane. This removes lane-specific npm resolution drift without changing package versions or the lockfile.
- **Scope:** CI workflow and static-test only. No runtime dependency, package manifest, lockfile, schema or site configuration changes.
- **Revisit criteria:** if `npm ci` reports a lockfile mismatch, update the lockfile deliberately in a separate dependency change and rerun dependency audits; do not fall back to `npm install` or suppress the static contract.
- **Verification status:** PR #131 merged as `08f269cdfaedc58fd4ce396c823d589e7dd3481b`; final head `a72ebffbae116adf06830473bb15d764a169651b` passed Quality/Python, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0. Both E2E lanes used lockfile-enforced `npm ci`; generated passwords were masked before step-output propagation. No package versions or lockfile changed. Reference-stack CI-verified, not pilot-verified.

### ADR-102 CI triage — static contract matched the full endpoint path (2026-11-03)

The first Quality/Python run on the PR #131 head failed one Python 3.11 static assertion (143 passed, 36 skipped, 1 failed). The spec correctly matches the full `/api/method/frappe.desk.form.load.getdoc` URL pathname; the new guard incorrectly searched for a quoted bare method name. Correct the guard to assert the full path. No browser test or permission assertion ran in the failed job; the direct-form test and 403/200 expectations are unchanged. Require a fresh complete final-head matrix.

### ADR-102 second CI triage — match the actual template-literal route and Prettier output

Quality run `41675975692` found a second static assertion mismatch: the route is authored as a template literal (`/app/crm-signal/`), not a double-quoted string. Its lint job `126056667745` reported exactly two Prettier changes: remove one extra blank line before `openCrmSignalForm` and keep the short test callback signature on one line. Apply those source-aligned corrections only. No browser or Frappe permission assertion ran in the failed jobs; fresh final-head CI is required.


### ADR-102/103 verification — PR #131 merged (2026-11-03)

PR #131 merged as [08f269c](https://github.com/MitMike/crm_signals/commit/08f269cdfaedc58fd4ce396c823d589e7dd3481b) from final tested head [a72ebff](https://github.com/MitMike/crm_signals/commit/a72ebffbae116adf06830473bb15d764a169651b).

All four final-head workflows passed:
- Quality Checks run [41676858036](https://github.com/MitMike/crm_signals/actions/runs/41676858036): lint/static checks and Python 3.10, 3.11, 3.12 and 3.14.
- Security/Semgrep run [41676862616](https://github.com/MitMike/crm_signals/actions/runs/41676862616).
- Bench Integration/E2E run [41676858619](https://github.com/MitMike/crm_signals/actions/runs/41676858619): Frappe v15 integration passed; Frappe v16 integration and the complete 18-test Playwright suite passed.
- Pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 run [41676858020](https://github.com/MitMike/crm_signals/actions/runs/41676858020): the focused three-test Playwright selection passed after site installation, preflight, D1/D2, Helpdesk, schema upgrade, Python and Frappe integration checks.

The direct Desk form test observed GET `frappe.desk.form.load.getdoc`: linked-restricted CRM Signal returned 403 without its message; unlinked-owned signal returned 200 with the expected message. The same-head browser-session HTTP API tests also passed. The supported v15 lane passed Bench integration; the v16 lane ran the full Playwright suite. No failing head was merged.

**Classification:** code-complete and reference-stack CI-verified on Frappe v16 and pinned v16.5.0; not pilot-verified. Authorized target-site API-token authentication, live direct-form and other permission paths, D1/D2 finance reconciliation, D3 SLA, deployment/rollback, operational recovery and visual UAT remain open.


## ADR-104 — Verify Sales User API-token permissions without session-cookie fallback

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** PR #130 and PR #131 cover browser-session HTTP methods and direct Desk form loading. The operator acceptance kit contains a token-authenticated HTTP smoke, but the reference CI did not prove token authentication or prevent a request from succeeding via the Administrator browser session.
- **Decision:** create a dedicated API key/secret for the synthetic Sales User using Frappe's `frappe.core.doctype.user.user.generate_keys` on the disposable Bench site. Write credentials only to a runner temp file with mode 0600; have Bench return only a non-sensitive success marker; mask both values before writing step outputs; remove the file with an EXIT trap. Exercise `frappe.auth.get_logged_user`, `frappe.client.get` and `frappe.client.get_list` using Node native `fetch` with an explicit `Authorization: token key:secret` header and manual redirect handling. Node fetch is outside the Playwright page trace; no browser cookie jar is used.
- **Expected results:** exact synthetic Sales User identity; linked-restricted CRM Signal 403 whose complete response body (JSON or non-JSON text) does not contain the restricted signal message; unlinked-owned CRM Signal 200 whose parsed response contains the expected record name and message; filtered list contains only the unlinked signal. Any redirect, identity mismatch or response-content mismatch fails.
- **Rationale:** this separates API-token authentication from the already-tested browser-session path and avoids recording the Authorization header in Playwright traces/artifacts.
- **Scope:** disposable CI fixture/workflow and operator-guide coverage only. No production runtime, schema, package, permission or site configuration change. Keep Frappe v15 Bench integration; run token E2E on supported v16 and pinned Frappe 16.5.0.
- **Verification:** code head `b9f72471d7cd7102023454cfef3ca491e950d5af` passed Quality/Python (run `41684113964`), Security/Semgrep (`41684114053`), Bench v15/v16 + Playwright (`41684114043`; 19 Playwright tests passed on v16) and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 (`41684113965`; 4 Playwright tests passed). Reference-stack CI-verified; not pilot-verified.
- **Revisit criteria:** inspect the exact versioned `generate_keys` and API token authentication behavior if either supported lane fails. Do not use Administrator credentials, browser cookies or automatic redirects as fallbacks. If credential exposure is suspected, discard the ephemeral site and fix masking/trace handling before rerun.
- **Verification status:** PR #133 merged as [`b2f1d07db7fdf8b6cafdaced7b0aaeefc74f9397`](https://github.com/MitMike/crm_signals/commit/b2f1d07db7fdf8b6cafdaced7b0aaeefc74f9397) from final PR head [`9a1a19c207e9bdff6cfb8df445bacb390d9478b6`](https://github.com/MitMike/crm_signals/commit/9a1a19c207e9bdff6cfb8df445bacb390d9478b6). Code head `b9f72471d7cd7102023454cfef3ca491e950d5af` passed Quality/Python (`41684113964`), Security/Semgrep (`41684114053`), Bench v15/v16 + Playwright (`41684114043`; 19 Playwright tests on v16) and pinned Frappe 16.5.0 (`41684113965`; 4 Playwright tests). The exact final PR head also passed fresh Quality/Python (`41685961000`), Security/Semgrep (`41685960990`), Bench v15/v16 + Playwright (`41685961276`) and pinned Frappe 16.5.0 (`41685961014`). Reference-stack CI-verified; not pilot-verified.

## ADR-105 — Verify Sales User token permissions on the standard REST resource API

- **Status:** Accepted
- **Recorded:** 2026-11-03
- **Context:** PR #133 verifies token-authenticated RPC methods `frappe.client.get` and `frappe.client.get_list`. Frappe's standard REST resource API uses separate single-document and collection routes at `/api/resource/{doctype}/{name}` and `/api/resource/{doctype}`; neither route was exercised by the API-token E2E.
- **Decision:** use the same disposable Sales User API key/secret with Node native fetch, outside the Playwright page and without a browser cookie jar. Send an explicit Authorization token header and `Accept: application/json`; disable automatic redirects and preserve non-JSON response text. Verify token identity first, then linked-restricted resource GET 403 with no restricted message, unlinked-owned resource GET 200 with exact name/message, and collection GET containing only the unlinked record.
- **Rationale:** resource reads are a separate Frappe v1 HTTP route from whitelisted RPC methods; testing both prevents a false assumption that RPC permission evidence proves resource API behavior.
- **Scope:** CI fixture/E2E and operator guide only. Supported Frappe v16 and pinned v16.5.0 run the token resource test; Frappe v15 Bench integration coverage remains. No production runtime, schema, package, permission or site configuration change.
- **Verification:** PR #137 merged as `9b2af7f90652927ca8497777e099cd3e742ce2f2` from final head `a7d1f48626ae0116a300a7b89404921bdda5552b`. Quality/Python `41698694186`, Security `41698694333` and `41698685514`, Bench v15/v16 `41698694301`, and pinned Frappe 16.5.0 `41698694356` all passed. v15 and v16 Bench each ran 157 tests; v16 Playwright ran 21 tests; pinned v16.5.0 ran 157 tests and 6 Playwright tests. Exact Frappe v15 and v16.5.0 source both use the read-or-print gate. Reference-stack CI-verified; not pilot-verified.
- **Revisit criteria:** if the resource route redirects, inspect the exact Frappe API URL map and trailing-slash behavior; never follow the redirect. If the response envelope differs, inspect the installed v1 resource handler and update only parsing/assertions. Do not weaken linked-denied/unlinked-allowed/list-only-unlinked expectations.

### ADR-105 verification — PR #135 merged (2026-11-04)

PR #135 merged as [81d70410f0f81124ae468c1d929caefd1610fd9e](https://github.com/MitMike/crm_signals/commit/81d70410f0f81124ae468c1d929caefd1610fd9e) from final tested head [ae6b7e408664a3b6f885c1c18ba9fc3d18c73890](https://github.com/MitMike/crm_signals/commit/ae6b7e408664a3b6f885c1c18ba9fc3d18c73890). All four final-head workflows passed: Quality/Python `41690041480`, Security/Semgrep `41690041431`, Bench v15/v16 + Playwright `41690041398`, and pinned Frappe 16.5.0 `41690041432`. REST resource single-document and collection E2E are reference-stack CI-verified. Authorized target-site token transport and role acceptance remain open; not pilot-verified.

## ADR-106 — Require row-level read visibility for CRM Signal print

- **Status:** Accepted
- **Recorded:** 2026-11-04
- **Context:** Frappe v15 and exact Frappe v16.5.0 `frappe.www.printview.validate_print_permission` both accept a document when either `read` or `print` permission succeeds. The CRM Signal permission hook previously enforced linked Lead/Customer visibility for `read` but returned true for `print` whenever the role-level DocType grant existed. Since Sales User has a role-level CRM Signal print grant, this allowed printing a linked-restricted signal despite direct read denial.
- **Decision:** keep the role-level DocType permission check for `print` and additionally require the same row-level readable relationship used by `read`. Manager role behavior remains unchanged. Unlinked signals remain printable only by their owner under the existing row policy.
- **Rationale:** print output discloses the full CRM Signal document and must not be a side door around the linked-party read boundary. Frappe's read-or-print print gate means role-only print permission is insufficient for this DocType.
- **Scope:** CRM Signal permission hook, unit/E2E regression tests and operator acceptance documentation. No schema, role, dependency or site-configuration changes.
- **Verification target:** Quality/Python, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 must all pass on the exact final PR head. Not pilot-verified.
- **Revisit criteria:** if installed Frappe v15/v16 print permission behavior differs, inspect the exact `validate_print_permission` implementation. Preserve both role-level print permission and row-level read visibility; do not accept a role-only grant for linked-restricted records.


## ADR-107 — Verify Sales User Report View and CSV export row filtering

- **Status:** Accepted
- **Recorded:** 2026-11-04
- **Context:** CRM Signal grants Sales User role-level Report and Export permissions. Earlier tests verify permission-filtered list calls, direct document/form loading, token-authenticated RPC and REST resource reads, and print-view denial. They did not exercise the standard Report View list route or the CSV export route with a Sales User whose User Permission excludes a linked Lead.
- **Decision:** add one cookie-independent API-token Playwright regression using the existing disposable Sales User and synthetic linked-restricted/unlinked-owned CRM Signals. First verify token identity. Then call `frappe.desk.reportview.get_list` with both names and require only the unlinked owned record. Call `frappe.desk.reportview.export_query` as CSV with the same filter; require the allowed name/message and prohibit the restricted name/message from the complete response body. Run the test in supported Frappe v16 and pinned Frappe 16.5.0.
- **Rationale:** Report View and export are distinct endpoints from `frappe.client.get_list` and `/api/resource`. Frappe's report-view query and export path use `DatabaseQuery`; the test proves the CRM Signal permission query remains in force through both user-facing paths. Role-level Export permission is retained; no new role grants or runtime permission changes are justified unless this regression fails.
- **Scope:** E2E/static tests and operator acceptance documentation only. Keep Frappe v15 Bench integration coverage. No production runtime, DocType permission, schema, dependency or site-configuration change.
- **Verification:** pending fresh final-head Quality/Python, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 workflows. Code-complete is not CI-verified or pilot-verified.
- **Revisit criteria:** if the Report View response or CSV contains the linked-restricted record, inspect exact installed Frappe `reportview.get_list`, `reportview.export_query` and `DatabaseQuery.execute` permission handling. If CSV response shape/status differs, adjust only request/response parsing after confirming the v16.5 route. Never use Administrator credentials, a browser-cookie fallback, `get_all`, a share or a weakened linked-denied/unlinked-allowed expectation.