# Project Progress

**Last reviewed:** 2026-11-02  
**Repository:** [MitMike/crm_signals](https://github.com/MitMike/crm_signals)  
**Main baseline:** [0a7de96](https://github.com/MitMike/crm_signals/commit/0a7de966ea0639c86a59d7df28dbad343fa13488)  
**Completed implementation:** PR #19 delivered settings/presets and core idempotency; PR #21 validated the legacy-schema migration; PR #23 closed concurrent API-idempotency and digest-queue races; PR #26 merged the transactional signal outbox; PR #32 merged the standard Frappe Helpdesk D3 adapter; PR #38 merged audited Failed-row replay; PR #42 merged D3 field-level permission hardening; PR #44 merged source-document notification authorization; PR #45 merged per-Company quotation thresholds; PR #49 corrected Company-currency display/fetch; PR #50 fixed the D3 system creation-column guard and added the exact Frappe v16.5.0 / Helpdesk v1.28.0 compatibility lane; PR #51 merged the Frappe v16.5 pilot operator kit; PR #53 merged the D3 aggregate fixture; PR #54 merged durable per-recipient realtime retry; PR #55 merged the staging realtime-recovery acceptance checks; PR #56 merged the pilot-status reconciliation as `704997e88a52071c15f95e5985703dc00bc10f03`; PR #57 merged the Explorer core API as `ba6317204784868a39d7c91ead01959663c9a33a`; PR #59 merged the Explorer Desk UI as `6b381fe4c7164c099cbd841086bf79566cb72ed1`; PR #61 merged five-context browser coverage and operator-runbook hardening as `6ef9642b63c24053fb437f67d9d4fb47e360c80a`; PR #63 merged read-only D1/D2 query-contract Bench smoke coverage as `0a7de966ea0639c86a59d7df28dbad343fa13488`; PR #62 reconciled post-Explorer status/decision records as `aeea9599b11f17bff0ef5bbd7904f44f23567e3e`  
**Next acceptance:** complete the target-site Frappe v16.5 pilot: exact app versions, per-Company threshold amounts/currencies, the custom read-only Helpdesk role, D1/D2 reconciliation, Helpdesk SLA calendar, scheduler/mail/realtime, and backup/restore/rollback. CI-verified work is not pilot-verified.

This file is the operational source of truth. [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) is the roadmap, [DECISIONS.md](DECISIONS.md) is the durable decision register, [FOLLOW_UPS.md](FOLLOW_UPS.md) tracks deferred issues, and [specs/](../specs/) holds feature contracts.

## Current status

**D1/D2 Bench query-contract coverage — PR #63 merged (2026-11-02):** The real Sales Compass API now runs read-only in the Frappe v15/v16 Bench matrix and the pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 lane. The PR's final-head Quality, Security, Semgrep, Python, Bench v15/v16 and pinned-target checks passed. This verifies query/schema compatibility only; it does not establish financial totals, role-specific target-site visibility or native-report reconciliation. Merge commit: `0a7de966`.

**D1/D2 Bench query contract — PR #63 (code complete; CI pending):** The previous Sales Compass coverage exercised mocked Frappe APIs, while the Bench matrix installed ERPNext without explicitly executing the D1/D2 aggregate path. PR #63 adds a read-only query-contract smoke to Frappe v15/v16 and the pinned v16.5.0 reference lane. It also restricts Bench push runs to `main` so feature branches use one authoritative pull-request run instead of duplicate push/PR matrices. It creates no business records and checks source availability/response shape only; it does not verify financial totals, Sales-role visibility or target-site reconciliation.


**PR #56 merged — 2026-11-02:** The post-PR55 pilot acceptance status, production-readiness and follow-up records are reconciled on main as `704997e`. The Dependabot note no longer names a stale base SHA. All three PR checks passed; no target-site pilot evidence was added or inferred.

**Explorer backend merged — PR #57 (`ba631720`):** ADR-059 limits the first read-only timeline API to CRM Signal, Quotation and Opportunity. It resolves Lead/Customer/Opportunity/Signal/High-Value Quote contexts, uses permission-aware reads and bounded snapshot pagination, and returns metadata-only summaries. The final head `dda6eb88c0e8735645018de60275d9cf55d2d99d` passed Quality Checks, Security Scanning, the Frappe v15/v16 Bench + Playwright matrix and the pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 lane before squash merge. ADR-060 requires explicit `Meta.get_permitted_fieldnames` checks because Frappe can silently omit fields hidden by field-level permissions. Tests cover hidden Opportunity relation fields, the High-Value Quote filter, hidden CRM Signal summary fields and party-specific relation selection.

**Explorer Desk UI and browser acceptance — PR #59/#61:** PR #59 merged the role-restricted timeline page, Lead/Customer/Opportunity/CRM Signal form actions, Highlight routing, GET cursor paging, safe summaries/source links, source states and stale-response protection as `6b381fe`. Its final head `4bc7893513253d40ee60bb3a00b7c70827041eb9` passed all eight required ruleset contexts and the pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 lane. PR #61 merged as `6ef9642`; final head `902b38e4dd4713461acfb12dc837f5b2b84da7d8` passed Quality Checks, Security Scanning, all eight required contexts (Python 3.10/3.11/3.12/3.14, lint/static, Semgrep, Bench v15/v16), and the pinned Frappe v16.5.0 lane. It adds Lead/Customer/Opportunity/CRM Signal/Highlight route coverage, a late-response regression, static documentation contracts, and corrects the deployment runbook's Company-threshold and Explorer smoke-test instructions. This is code-complete and CI-verified, not pilot-verified. Target-site role/field-permission acceptance and optional-provider inventory remain open.

**H Highlights quote contract — PR #60:** The high-value Quotation hook and Company-currency threshold behavior already exist. PR #60 adds direct regression coverage for the `>=` boundary, below-threshold behavior, foreign-currency display using the Company base total, and fail-closed behavior when neither a base total nor matching transaction currency is available. ADR-061 records that VIP escalation semantics and proposal-link privacy/retention must be approved before those remaining H features are implemented.

**PR #54 merged — 2026-11-02:** Durable per-recipient notification delivery merged as `37ce6003c9459f1b391de5dff8354e4bfc04cb9b`. Final synchronized head `f1cbd3e92946a4a5513b7555396cada4491fdd3e` passed all eight required ruleset contexts (Python 3.10/3.11/3.12/3.14, lint/static, Semgrep, Bench v15/v16) and the additional pinned Frappe v16.5.0 + ERPNext v16.5.0 + Helpdesk v1.28.0 lane. Target-site Redis outage, worker restart, scheduler and permission-revocation acceptance remain open.

**PR #53 merged — 2026-11-02:** The six-ticket D3 Helpdesk aggregate fixture merged as `9e85156ae6141e723e44fa093a75b49282459fa9` after the required checks passed. It verifies exact backlog, resolved, resolution-duration and SLA aggregate deltas on the reference Helpdesk stack.


**Sprint update — 2026-11-02:** PR #60 merged the H quotation contract regressions as `478cd0e`. PR #51 merged the Frappe v16.5 operator kit (`cab1796d`); PR #53 merged D3 aggregate verification (`9e85156a`); PR #54 merged durable per-recipient retry (`37ce6003`); PR #55 merged the staging recovery acceptance procedure (`a4b1a9d`). PR #56 then reconciled the post-PR55 progress, production-readiness and follow-up records as `704997e`; its Quality, Security and Bench Integration/E2E workflows all passed. PR #57 merged the Explorer backend as `ba631720`; PR #59 merged the Desk UI as `6b381fe`; PR #61 merged the five-context and stale-response Playwright regressions plus operator runbook hardening as `6ef9642`, after all required and pinned-target checks passed. The target-site Company thresholds, Helpdesk role/SLA calendar, D1/D2 reconciliation, deployment rehearsal and realtime fault-injection execution remain unverified.


| Workstream | Status | Evidence / next action |
|---|---|---|
| CRM Signals core | Implemented; PR #19 merged | Target-site permission, upgrade and deployment checks remain |
| Signals Console | Implemented | Validate actual target-site roles and list/form/report/export/API behavior |
| D1 Sales Compass | Implemented; status-metadata safety fix merged | PR #17 merged as `fed496f`; PR #63 adds a real ERPNext Bench query-contract smoke (CI pending); target-site workflow/status validation remains |
| D2 Billing Realization | Implemented; return-metadata safety guard merged | PR #17 requires `is_return` for return-sensitive measures; PR #63 adds a real ERPNext Bench query-contract smoke (CI pending); target-site financial reconciliation remains |
| File/function standards | Merged | PR #18 merged as `f51fbce`; limits, checker, pre-commit and CI enforcement are on main |
| Settings + presets | Merged in PR #19 | Settings singleton, validation, Balanced/Sales Focused/Executive presets and administrator guide; confirm target-site defaults before activation |
| Event identity/idempotency | Runtime merged in PR #19; migration rehearsal merged in PR #21; concurrent recovery merged in PR #23 | Unique SHA-256 source-event key; legacy-schema migration passed on Frappe v15/v16; final two-connection API race test passed on both supported versions. One created response, one deduplicated response and one notification dispatch. |
| Digest hardening | Core merged in PR #19; cross-worker serialization merged in PR #23 | Site-timezone schedule, permission-aware per-user email and per-recipient queue markers; Settings row lock plus recheck prevents overlapping workers queuing the same recipient/date; v15/v16 Bench tests passed. Target-site scheduler/mail acceptance remains open. |
| Signal outbox recovery | Core merged in PR #26; audited Failed-row replay merged in PR #38 | System Manager/read-permission-gated POST action, explicit confirmation, attempt-history preservation and audit Comment; v15/v16 Bench checks passed. Realtime delivery retry is separate and remains open |
| Realtime notification delivery | Merged in PR #54 as `37ce600`; CI verified on head `f1cbd3e` | Per-recipient ledger, stable delivery ID, bounded retry, current recipient/source permission recheck and active-session duplicate suppression. `Attempted` means callback queued, not Redis/browser/human delivery. Pilot Redis outage, worker restart, scheduler and permission-revocation acceptance remain |
| D3 Service Resolution/SLA | Adapter + field-level guard merged in PR #32/#42; aggregate fixture merged in PR #53; exact v16.5.0/Helpdesk v1.28.0 CI verified in PR #50/#53 | Standard HD Ticket/HD Service Level Agreement aggregate adapter; target-site versions, Sales read-only role and active SLA calendar remain |
| H Highlights | Partial; high-value Quotation alert and per-Company thresholds implemented | PR #60 adds hook-level tests for exact-threshold firing, below-threshold suppression and fail-closed missing currency basis. Target-site Company amounts/currency and recipient checks remain; VIP routing needs product decision (ADR-061), and proposal tracking needs privacy/consent/retention approval |
| E Explorer | Backend, Desk UI and five-context browser coverage merged in PR #57/#59/#61; CI verified | Core adapters, fail-closed field checks, bounded pagination, GET route matrix and late-response suppression pass v15/v16 and pinned v16.5 CI. Pilot role/field checks and optional-provider inventory remain |
| V Vault | Blocked pending accepted metrics and policy | D1/D2 target-site reconciliation, reporting-population/source visibility, retention period, deletion owner and audited dry-run pruning must be approved before snapshot code or scheduling |
| A Analysis | Blocked pending D1/D2 site reconciliation | Sales/Finance must approve metric definitions, currency/period/filter semantics and source permissions before the versioned registry and deterministic intent path are implemented; no generated SQL/Python |
| Repository security/CI | Merged | PR #11 security/dependency hardening; PR #18 maintainability guardrails; main ruleset active |
| Target-site acceptance kit | Base kit merged in PR #28; realtime recovery checks merged in PR #55 as `a4b1a9d` | `docs/TARGET_SITE_ACCEPTANCE.md`; records Frappe v16.5, per-company thresholds, D3 field permissions and staging-only realtime recovery tests; target-site execution remains open |

## Completed reliability hardening — PR #23

- Fixes the real unique-key race: after both API requests observe an event key as absent, the losing insert now reloads the winning CRM Signal with `for_update=True` so MariaDB repeatable-read cannot hide the row behind an older snapshot.
- Adds a deterministic Bench test using two independent database connections. The expected result is one CRM Signal, one created response, one deduplicated response and one notification dispatch.
- Serializes digest recipient claims by locking the CRM Signals Settings singleton and rechecking the queued-recipient marker before each email queue request. The lock and marker update share the same transaction as that recipient's Email Queue write.
- Adds a two-worker Bench test asserting one queue request for a recipient/date.
- **Status:** merged to `main` as `d75b7f3`. [Bench v15/v16 + Playwright](https://github.com/MitMike/crm_signals/actions/runs/41300667892), [Quality Checks](https://github.com/MitMike/crm_signals/actions/runs/41300667996) and [Security Scanning](https://github.com/MitMike/crm_signals/actions/runs/41300667997) passed on PR head `7ed0860`. No target-site mail/scheduler acceptance is implied.

## Completed engineering task — legacy schema upgrade rehearsal

- PR #21 adds a disposable Bench scenario to both Frappe v15 and v16 lanes: create two historical CRM Signal rows, remove the newer source-event identity columns and DocField metadata, run the real `bench migrate`, then verify the current schema returns and both legacy rows remain intact with null event keys.
- The test deliberately exercises Frappe DocType synchronization. An empty `crm_signals/patches.txt` is not treated as a defect; a custom patch will be added only if migration evidence requires one.
- Status: **passed** on Frappe v15 and v16 in PR #21. The final head `3578dd566683d2dff4c9f663b733e838b6627e25` passed Quality Checks, Bench Integration and E2E, and Security Scanning. The merge commit is `72833cd383811d7c9be591206647b2e0b1f3fbd9`. This does not replace target-site upgrade, backup, restore and rollback rehearsal.

## Merged repository foundation

- [PR #11](https://github.com/MitMike/crm_signals/pull/11) — dependency security monitoring, lockfile, pip/npm audits, Dependabot and tooling remediation.
- [PR #16](https://github.com/MitMike/crm_signals/pull/16) — complete specifications, decision register, delivery plan and feature roadmap.
- [PR #17](https://github.com/MitMike/crm_signals/pull/17) — D1/D2 correctness safeguards for missing Lead/Opportunity status metadata and Sales Invoice return metadata. Merge commit: [fed496f](https://github.com/MitMike/crm_signals/commit/fed496f230f5ca88af25d663bc61fe4d748f5f83).
- [PR #18](https://github.com/MitMike/crm_signals/pull/18) — graduated file/function size and complexity rules. Merge commit: [f51fbce](https://github.com/MitMike/crm_signals/commit/f51fbce19b7d1e84cfa6f3ab26118f2977a8fe40).
- [PR #19](https://github.com/MitMike/crm_signals/pull/19) — configurable settings, presets, Frappe v15/v16 permission compatibility, event idempotency and digest hardening. Merge commit: [a495919](https://github.com/MitMike/crm_signals/commit/a49591947a89b011cc1770be176c1f11571b131b).

## Repository governance

GitHub ruleset [Protect main](https://github.com/MitMike/crm_signals/rules/26282133) is active on `refs/heads/main`.

- Pull requests required; direct main updates, deletion and force pushes are blocked.
- Eight strict required contexts cover lint/static checks, Python 3.10/3.11/3.12/3.14, Semgrep and Bench v15/v16.
- Review threads must be resolved. Required approving review count is zero to avoid deadlocking a single-maintainer repository.
- No bypass actors are configured. Emergency recovery requires an authorized administrator to temporarily edit and then restore the ruleset.
- Dependency Security Audit is active, but is not one of the eight required branch contexts.

[Issue #12](https://github.com/MitMike/crm_signals/issues/12) was closed after ruleset verification.


## Durable transactional signal outbox — PR #26 merged

- PR [#26](https://github.com/MitMike/crm_signals/pull/26) merged to `main` as `b0364a74affa823977af74d1907781d1533e60c0`.
- Final synchronized head: `222e70ec71164dab4448f7319525042323a357b4` (based on main after PR #28).
- Quality Checks, Security Scanning and Bench Integration/E2E all passed on that exact head; Bench covered Frappe v15/v16 and the concurrent enqueue/process idempotency cases.
- Source events and outbox rows commit atomically; delivery is queued after commit, with the scheduled pending-event worker retained as recovery. Retry is bounded and terminal failures are visible to System Managers.
- **Still open:** audited operator replay for terminal Failed rows (PR #38 merged) and durable realtime notification retry. These are not included in the merged outbox scope.

## Stage 1 — release readiness and core hardening

### Completed in merged code
- D1 active Lead/Opportunity counts, stages and active pipeline become unavailable when status metadata is missing rather than incorrectly counting all rows as active.
- D2 Sales Invoice metrics that exclude returns require `is_return`; no return-sensitive aggregation runs without that filter.
- Payment Entry receipt metrics remain independent of Sales Invoice return metadata.
- Branch protection and file/function size standards are merged.

### Implemented and merged in PR #19
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
- CI follow-up (2026-11-01): Bench v16 exposed the changed document-permission hook contract: it passes `ptype` and requires an explicit boolean. Updated the hook to accept both v15/v16 argument names and preserve role-level DocType permissions before row-level restrictions (ADR-039). Corrected duplicate-key recovery to handle Frappe's `UniqueValidationError` using a locking read, added a race-recovery regression test, and changed notification idempotency coverage to count one dispatch rather than assume one realtime recipient. Prettier formatting was corrected and its temporary diagnostic step removed. These changes passed the final v15/v16 Bench matrices, Playwright, Python, lint and security checks before PR #19 merged.
- CI follow-up (2026-11-01): The first v16 Playwright run exposed a login race: the session cookie existed before Frappe completed the redirect, causing subsequent API/navigation actions to overlap with that redirect and trigger aborted requests and CSRF errors. The shared login helper now waits for the version-appropriate Desk URL; the settings custom-preset handler awaits its form-model update and the E2E test blurs the integer field before asserting. See ADR-040. The corrected v16 Playwright suite passed on final PR head `a90315be7ef37e2dceeacb9b4e9b77d5d31df131`.
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
- Target-site acceptance for durable realtime retry (engineering implementation in PR #54); audited terminal Failed-row replay for the transactional signal outbox is merged in PR #38.
- Multi-company quotation thresholds merged in PR #45; target-site Company amounts and exact-currency fallback approval remain; no implicit FX conversion.
- D3 field-level permission hardening and target-site acceptance; H privacy/consent decisions, E integration inventory, V retention and A metric-registry work.

## Completed branch work — PR #21

- PR #21 adds a disposable Frappe v15/v16 rehearsal for upgrading historical CRM Signal rows from the pre-source-event-identity schema.
- First rehearsal attempts failed because Frappe's stored DocType `migration_hash` still matched the current JSON, so the importer skipped the schema import even after the timestamp rewind.
- The fixture now clears that hash and rewinds the DocType timestamp before `bench migrate` (ADR-042). This is a CI fixture correction; the final migration rehearsal passed on both supported Frappe versions.
- Latest fix commit: `acc096879841286afa61073571fbe40eea473fd4`. PR #21 is merged as `72833cd383811d7c9be591206647b2e0b1f3fbd9`.

## CI and release evidence

PR #23 was merged to `main` as `d75b7f3591d2a863b0af6b8f88ad2a91e9bfd25f` after all required checks passed on final PR head `7ed0860fd45cdc152bb2dcc868489d46b69aefb9`: [Bench Integration and E2E, v15/v16 + Playwright](https://github.com/MitMike/crm_signals/actions/runs/41300667892), [Quality Checks](https://github.com/MitMike/crm_signals/actions/runs/41300667996), [Security Scanning](https://github.com/MitMike/crm_signals/actions/runs/41300667997). API idempotency and digest concurrency regression tests passed on both supported Frappe versions. The earlier PR #21 legacy-schema migration rehearsal also passed; target-site upgrade/restore/rollback remains open.

PR #21 was merged after all required checks passed on final head `3578dd566683d2dff4c9f663b733e838b6627e25`. Quality Checks, Bench Integration and E2E (Frappe v15/v16), and Security Scanning passed. The legacy-schema upgrade rehearsal is complete at CI level; target-site upgrade/restore/rollback remains open.

PR #19 was validated on head `a90315be7ef37e2dceeacb9b4e9b77d5d31df131` and merged as `a49591947a89b011cc1770be176c1f11571b131b`. [Quality Checks](https://github.com/MitMike/crm_signals/actions/runs/41274491111), [Bench Integration and E2E](https://github.com/MitMike/crm_signals/actions/runs/41274491113) and [Security Scanning](https://github.com/MitMike/crm_signals/actions/runs/41274491117) passed; all 16 check-runs on that head reported success, including Frappe/ERPNext v15 and v16 and the v16 Playwright suite.

CI is necessary, not production acceptance. Never mark a target-site gate complete based only on a mocked unit test or the existence of source code.

## Update protocol

For each change:
1. Update the relevant spec before or alongside implementation.
2. Record material data, security, compatibility and delivery choices in [DECISIONS.md](DECISIONS.md).
3. Add tests for the acceptance criteria.
4. Update [CHANGELOG.md](../CHANGELOG.md) for user-visible or operationally significant changes.
5. Reconcile this file after merge and attach commit/CI evidence.
6. Put blocked or intentionally deferred work in [FOLLOW_UPS.md](FOLLOW_UPS.md), with an owner/trigger and reason.


## D3 adapter merged — Frappe Helpdesk

- Merge: PR #32 as `43fddfbbc46cac277a48c840251a7a2c963a8eb5`; CI verified on Frappe v15/v16.
- Source schema verified against Helpdesk v1.28.0 reference: HD Ticket, HD Ticket Status, HD Service Level Agreement; ticket fields include status_category, resolution_date, resolution_time, sla and agreement_status at permlevel 0. Later Helpdesk releases may move fields to higher levels.
- API aggregates ticket creation, current Open/Paused backlog, resolved cohort, native resolution duration and SLA fulfilled/failed outcomes. Ticket and SLA permissions are checked independently; payload contains no ticket subjects, comments, contacts or identifiers.
- SLA outcome counts use the same rolling 30-day created-ticket cohort; only Fulfilled/Failed are eligible. No-SLA tickets are counted separately.
- Monday–Saturday is the agreed business-week assumption; configured Helpdesk SLA hours and holiday lists are not overridden.
- Field-level fail-closed permission guard merged in PR #42; exact Frappe v16.5.0/ERPNext v16.5.0/Helpdesk v1.28.0 CI merged and passed in PR #50. Pilot-site versions and role/SLA acceptance remain. The first run exposed a malformed MariaDB client config; the here-doc correction is in place.
- Remaining: capture the pilot site's exact app versions, configure the approved custom read-only Helpdesk role for Sales, and verify the active SLA calendar, hours and holiday list.


## Resolved PR #57 merge gate — cancelled duplicate Bench checks

- **Evidence:** GitHub rejected the earlier merge attempt on head `7f9d840226e6d6db1a435b8c1cc629e70dc63eca` because two required Bench contexts were cancelled by a push run on the stacked Desk branch. A new unique head `dda6eb88c0e8735645018de60275d9cf55d2d99d` then passed all eight required contexts and the pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 lane; PR #57 merged as `ba631720`.
- **Decision:** Do not bypass the main ruleset or retry stale shared-SHA runs. The original stacked PR #58 was closed unmerged; PR #59 is its clean replacement based on `main`.
- **Revisit criteria:** No further action is required for PR #57. If a future PR produces duplicate or cancelled contexts, inspect the push and pull-request run sources and require successful final-head contexts before merging. Never bypass branch protection.
