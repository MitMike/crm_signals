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
