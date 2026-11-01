# CRM Signals — Settings and core reliability

**Status:** Core settings and reliability hardening merged in PR #19 and PR #23. Transactional signal outbox implementation is under review in PR #26.
**Scope:** Singleton configuration, starter presets, event identity, external ingestion deduplication and digest delivery safety.

## Goals

- Move business defaults from source constants into a validated System Manager-only singleton.
- Provide starter profiles that administrators can apply and then customise.
- Never assume the Company's currency is INR.
- Generate source-event identities that remain stable across retries.
- Ensure repeated webhook requests do not create duplicate signal records when an event ID is supplied.
- Make daily digest timing and recipients configurable and avoid duplicate queuing for one site-local date.
- Keep failures in ancillary notification delivery from breaking Quotation/Opportunity saves.

## Settings contract

The singleton is `CRM Signals Settings`. It includes a master switch, external ingestion switch, Quotation signal switch and threshold/currency, Opportunity signal switch and exact trigger statuses, digest switch/time/stale window, optional additional enabled System User recipients, and last-queued diagnostics.

The master switch and external ingestion switch default to disabled on fresh installation and when the singleton is unavailable. Administrators must complete site preflight and explicitly enable the feature; enabling the master switch does not enable external ingestion.

The preset profiles are Balanced, Sales Focused and Executive. They populate a defined set of starter values only. Selecting a preset does not override later edits unless an administrator selects another preset. Any manual change sets the visible preset label to Custom.

The threshold is interpreted in one site-wide threshold currency. Quotation events compare the Quotation's base total against that threshold and display the Quotation transaction currency. Multi-company sites with different base currencies are not considered supported for a single global threshold; this must be solved with per-company settings before enabling those events across such companies.

## Event identity and deduplication

A source event is identified by source DocType/type, source document/integration identity and a stable source event ID. CRM Signal DocType validation normalizes those values and derives the SHA-256 key itself; it never trusts a caller-supplied hash. A unique field enforces the key. A repeated event returns the existing signal and does not publish another notification. Partial identities are rejected; a key without identity is cleared.

External API callers may provide a source event ID. When source metadata is omitted, the server namespaces the event by the authenticated integration user. When callers supply source DocType and source name, those caller-provided values form the namespace and must be stable and unique across integrations. Retries must reuse the same integration identity, source namespace and event ID. Without an ID, the endpoint retains legacy non-idempotent behavior.

Quotation submit identity includes the source document and its submission modification timestamp. Opportunity transition identity includes source document, previous/next status and modification timestamp.

## Transactional signal outbox

Quotation and Opportunity events are written to the CRM Signal Outbox in the same database transaction as the source document. A stable source-event key is unique. If the outbox row cannot be persisted or recovered after a duplicate-key race, the hook raises a dedicated persistence error and the source document transaction must roll back. This is required for the transactional-outbox guarantee (ADR-045).

After the outbox row exists, CRM Signal materialization is attempted immediately inside a savepoint. A materialization failure rolls back only the signal attempt, increments the failure count and leaves the outbox Pending. The scheduler checks every minute, selects only rows whose retry time is due, and processes at most 100 per batch. Backoff is 1, 2, 4, 8, 16, 32 and then at most 60 minutes. The tenth failed attempt moves the row to Failed. Only System Managers can inspect outbox records. Realtime notification delivery remains separate and is not retried by this outbox.

## Digest contract

The scheduled checker runs every minute. It compares the configured time with the timezone in System Settings and uses the site-local calendar date as its idempotency boundary. A recipient is marked queued only after their separate `frappe.sendmail` request succeeds; the Email Queue row and recipient marker are committed together. PR #23 locks the Settings singleton and rechecks the marker before every recipient claim, so overlapping workers cannot both queue the same recipient/date. System-owned marker fields use `Document.db_set` to avoid rerunning unrelated admin settings validation. The two-worker regression test passed on Frappe v15 and v16.

Recipients are enabled System Users holding the Sales Manager role plus explicitly configured additional System User email addresses. Settings validation rejects unknown, disabled or Website User addresses; the task still filters recipients to enabled System Users and never sends to Guest or arbitrary external recipients. Generate each message while impersonating that recipient and use permission-aware `frappe.get_list` queries for Lead counts and expiring Quotations. Send one digest per user; never share a system-wide result across recipients.

## Failure behavior

Notification delivery to one recipient is isolated from other recipients and the source transaction. Errors are logged without rolling back the saved Quotation, Opportunity or CRM Signal. A failed signal-creation hook is logged and does not block the source business document; repeated source events remain safe because identity is unique.

## Acceptance criteria

- Settings are System Manager-only; configuration validates ranges, time, currencies, statuses and recipient addresses. Additional addresses must resolve to registered, enabled System Users (not Website Users).
- Preset selection fills values; manual changes switch the profile indicator to Custom.
- The event handler uses configured thresholds/statuses and no hard-coded currency symbol.
- The API requires Guest rejection, honors the ingestion switch, validates optional source identity and deduplicates stable IDs.
- DocType validation recomputes source-event keys and rejects partial identities regardless of whether records arrive through hooks, the ingestion endpoint, Desk or another API.
- Repeated source event IDs return the original CRM Signal without duplicate notification.
- Quotation/Opportunity outbox persistence failure aborts the source transaction; CRM Signal materialization failure after outbox persistence leaves a retryable Pending row.
- Outbox worker excludes future-dated rows before applying its batch limit, and concurrent workers materialize one CRM Signal for a single outbox event.
- Outbox retries stop after ten attempts and expose a terminal Failed state to System Managers.
- Digest schedule respects the System Settings timezone and sends at most one queued digest per recipient/date, including across overlapping scheduler workers; the v15/v16 Bench proof passed in PR #23.
- Digest labels the stale Lead condition as not modified, formats each Quote in its transaction currency and filters recipients to enabled System Users.
- Unit, Bench and E2E tests cover the settings schema, identity uniqueness, scheduler date boundary, retries and user-visible settings.

## Deferred acceptance

- Audited operator replay for terminal Failed outbox rows.
- Automatic retry of realtime notification dispatch failures.

- Live-site confirmation of Company currency, Opportunity statuses, timezone, recipient policy and role matrix.
- Multi-company threshold policy for installations whose companies use different base currencies.
- Production webhook TLS/rate limiting/secret rotation and deployment rollback.
