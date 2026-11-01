# Project Progress

**Last reviewed:** 2026-11-01  
**Repository:** [MitMike/crm_signals](https://github.com/MitMike/crm_signals)  
**Main baseline:** [f51fbce](https://github.com/MitMike/crm_signals/commit/f51fbce19b7d1e84cfa6f3ab26118f2977a8fe40)  
**Active delivery branch:** `feat/settings-and-core-reliability` — configurable settings, presets, source-event idempotency and digest safety. Changes are not merged until GitHub reports the PR merged.

This file is the operational source of truth. [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) is the roadmap, [DECISIONS.md](DECISIONS.md) is the durable decision register, [FOLLOW_UPS.md](FOLLOW_UPS.md) tracks deferred issues, and [specs/](../specs/) holds feature contracts.

## Current status

| Workstream | Status | Evidence / next action |
|---|---|---|
| CRM Signals core | Baseline implemented | Settings and reliability hardening in active branch; target-site permission/deployment checks remain |
| Signals Console | Implemented | Validate actual target-site roles and list/form/report/export/API behavior |
| D1 Sales Compass | Implemented; correctness fix merged | PR #17 merged as `fed496f`; target-site workflow/status validation remains |
| D2 Billing Realization | Implemented; safety fix merged | PR #17 requires `is_return` for return-sensitive measures; target-site financial reconciliation remains |
| File/function standards | Merged | PR #18 merged as `f51fbce`; limits, checker, pre-commit and CI enforcement are on main |
| Settings + presets | Implemented on active branch | Settings singleton, validation, Balanced/Sales Focused/Executive presets and guide; CI/merge pending |
| Event identity/idempotency | Implemented on active branch | Unique SHA-256 source-event key, API event ID support and duplicate-safe notification; CI/merge pending |
| Digest hardening | Implemented on active branch | Site-timezone schedule, per-recipient permission-aware emails, recipient queue tracking, configurable stale window/time/recipients and currency-code formatting; CI/merge pending |
| Notification failure isolation | Implemented on active branch | Recipient failures are logged and do not block other recipients or source-document saves; automated retry/outbox remains deferred |
| D3 Service Resolution/SLA | Specified; not implemented | Discover target-site support/SLA application and source semantics before adapter implementation |
| H Highlights | Partial/planned | Finish idempotent events, recipient controls, verified proposal tracking and privacy approval |
| E Explorer | Planned | Inventory installed activity integrations and implement only verified source adapters |
| V Vault | Planned | Approve metric registry, source visibility and retention before enabling snapshots |
| A Analysis | Planned | Approved metric registry and constrained server-owned queries; no model-generated SQL |
| Repository security/CI | Merged | PR #11 security/dependency hardening; PR #18 maintainability guardrails; main ruleset active |

## Merged repository foundation

- [PR #11](https://github.com/MitMike/crm_signals/pull/11) — dependency security monitoring, lockfile, pip/npm audits, Dependabot and tooling remediation.
- [PR #16](https://github.com/MitMike/crm_signals/pull/16) — complete specifications, decision register, delivery plan and feature roadmap.
- [PR #17](https://github.com/MitMike/crm_signals/pull/17) — D1/D2 correctness safeguards for missing Lead/Opportunity status metadata and Sales Invoice return metadata. Merge commit: [fed496f](https://github.com/MitMike/crm_signals/commit/fed496f230f5ca88af25d663bc61fe4d748f5f83).
- [PR #18](https://github.com/MitMike/crm_signals/pull/18) — graduated file/function size and complexity rules. Merge commit: [f51fbce](https://github.com/MitMike/crm_signals/commit/f51fbce19b7d1e84cfa6f3ab26118f2977a8fe40).

## Repository governance

GitHub ruleset [Protect main](https://github.com/MitMike/crm_signals/rules/26282133) is active on `refs/heads/main`.

- Pull requests required; direct main updates, deletion and force pushes are blocked.
- Eight strict required contexts cover lint/static checks, Python 3.10/3.11/3.12/3.14, Semgrep and Bench v15/v16.
- Review threads must be resolved. Required approving review count is zero to avoid deadlocking a single-maintainer repository.
- No bypass actors are configured. Emergency recovery requires an authorized administrator to temporarily edit and then restore the ruleset.
- Dependency Security Audit is active, but is not one of the eight required branch contexts.

[Issue #12](https://github.com/MitMike/crm_signals/issues/12) was closed after ruleset verification.

## Stage 1 — release readiness and core hardening

### Completed in merged code
- D1 active Lead/Opportunity counts, stages and active pipeline become unavailable when status metadata is missing rather than incorrectly counting all rows as active.
- D2 Sales Invoice metrics that exclude returns require `is_return`; no return-sensitive aggregation runs without that filter.
- Payment Entry receipt metrics remain independent of Sales Invoice return metadata.
- Branch protection and file/function size standards are merged.

### On the active implementation branch; not yet merged
- Add System Manager-only CRM Signals Settings singleton and editable Balanced, Sales Focused and Executive presets.
- Configure master/external-ingestion/Quotation/Opportunity/digest switches, Company-currency threshold, Opportunity status list, stale-day window, digest time and extra recipients validated against registered enabled System Users.
- Add source-event metadata and a unique hash-based identity for CRM Signals.
- Make webhook retries idempotent when the caller supplies a stable `source_event_id`.
- Schedule the digest at the configured System Settings timezone, query CRM rows under each recipient's user context, send separate permission-filtered emails and record each queued recipient in the same transaction as that email-queue request.
- Remove hard-coded INR formatting and isolate realtime notification errors by recipient.
- Filter realtime recipients by the linked Lead/Customer read permission before sending signal content; denied/failed permission checks are excluded (ADR-034).
- Also require CRM Signal document read permission; add a real FrappeTestCase for both checks and run it with `bench run-tests --app crm_signals` on v15 and v16.
- Align list-query access with direct-document access: owner-only visibility is restricted to unlinked signals; linked signals require a permission-readable owned/assigned parent (ADR-035).
- Add a generic deployment/rollback runbook; actual target-site backup/restore rehearsal remains a P0 acceptance gate.
- Record a production-readiness audit with fixed findings, outstanding P0/P1 risks and an explicit not-ready-for-sign-off decision in docs/PRODUCTION_READINESS_AUDIT.md.
- Default the master switch and external ingestion to disabled, including missing-settings fallback, until System Manager explicitly activates the reviewed configuration (ADR-036).
- Bound daily digest quotation output to 100 rows with an explicit truncation notice to prevent unbounded email payloads (ADR-037).
- Add Bench-backed webhook and database tests for same-user duplicate POSTs, one notification per event, per-user namespaces, unique-key enforcement and multiple legacy null keys; concurrent insert and true pre-feature upgrade migration remain open.
- CI follow-up (2026-11-01): Bench v15/v16 exposed an invalid CRM Signal autoname expression that persisted the literal `SIG-.YYYY.-.#####`; corrected to Frappe's brace-delimited `format:SIG-{YYYY}-{#####}` (ADR-038). The API integration test now sets request form data after switching users because the user-context switch clears the local request form.
- CI follow-up (2026-11-01): Bench v16 exposed the changed document-permission hook contract: it passes `ptype` and requires an explicit boolean. Updated the hook to accept both v15/v16 argument names and preserve role-level DocType permissions before row-level restrictions (ADR-039). Corrected duplicate-key recovery to handle Frappe's `UniqueValidationError` using a locking read, added a race-recovery regression test, and changed notification idempotency coverage to count one dispatch rather than assume one realtime recipient. Prettier formatting was corrected and its temporary diagnostic step removed. Both Bench matrices and required CI checks must pass on the final head before merge.
- CI follow-up (2026-11-01): The v15/v16 Bench integration suites passed. The first v16 Playwright run then exposed a login race: the session cookie existed before Frappe completed the redirect, causing subsequent API/navigation actions to overlap with that redirect and trigger aborted requests and CSRF errors. The shared login helper now waits for the Desk URL; the settings custom-preset handler awaits its form-model update and the E2E test blurs the integer field before asserting. See ADR-040. Re-run the complete v15/v16 Bench and browser matrix on the final head before merge.
- Add an admin guide, settings/reliability spec and configuration/identity/digest tests.

### Target-site acceptance — still required
- [ ] Run Frappe Pilot import on the intended site and record installed Frappe/ERPNext versions and applications.
- [ ] Confirm Company default currency and verify quotation threshold behavior for every enabled Company.
- [ ] Confirm Opportunity status values and terminal Lead statuses from actual workflows.
- [ ] Confirm site timezone, digest time and recipients.
- [ ] Validate Sales User, Sales Manager, System Manager and non-sales roles in list, direct form, API, report, export and print paths.
- [ ] Reconcile D2 invoice, Payment Entry receipt, POS receipt and receivable figures against native ERPNext reports, by currency.
- [ ] Configure a dedicated integration user, API credentials, TLS, gateway rate limiting, monitoring and secret rotation.
- [ ] Exercise scheduler, mail queue, realtime notifications, migration, backup and rollback on the intended site.

## Explicitly deferred

See [FOLLOW_UPS.md](FOLLOW_UPS.md) for issues that should not be silently treated as complete:
- Retryable outbox/reconciliation for signal-creation failures. Current hooks log failures and preserve the source transaction; they do not yet guarantee automatic retry after a transient database failure.
- Per-company quotation thresholds for multi-company sites with different base currencies.
- D3 source discovery, H privacy/consent decisions, E integration inventory, V retention and A metric-registry work.

## CI and release evidence

The merged baseline has passed the existing Quality Checks, Bench Integration/E2E (Frappe/ERPNext v15 and v16), Security Scanning and Dependency Security Audit workflows on the corresponding PR heads. The active settings/reliability branch must pass current CI on its final head and be merged before this code is treated as delivered.

CI is necessary, not production acceptance. Never mark a target-site gate complete based only on a mocked unit test or the existence of source code.

## Update protocol

For each change:
1. Update the relevant spec before or alongside implementation.
2. Record material data, security, compatibility and delivery choices in [DECISIONS.md](DECISIONS.md).
3. Add tests for the acceptance criteria.
4. Update [CHANGELOG.md](../CHANGELOG.md) for user-visible or operationally significant changes.
5. Reconcile this file after merge and attach commit/CI evidence.
6. Put blocked or intentionally deferred work in [FOLLOW_UPS.md](FOLLOW_UPS.md), with an owner/trigger and reason.
