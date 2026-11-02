# CRM Signals — Product and Engineering Delivery Plan

**Last reviewed:** 2026-11-03  
**Repository:** [MitMike/crm_signals](https://github.com/MitMike/crm_signals)  
**Supported framework coverage:** Frappe / ERPNext v15 and v16. **Primary deployment target:** Frappe v16.5; record the exact patch/build and installed ERPNext/Helpdesk versions.  
**Reviewed main baseline:** [9c4febf](https://github.com/MitMike/crm_signals/commit/9c4febf8180ef295b48ea18b1ac5fddc164ff34f) (PR #100 merged); **latest application feature baseline:** [c5720bf](https://github.com/MitMike/crm_signals/commit/c5720bfb3fbe8b554ec6febd549a8d5e58acc1d7).

This is the execution plan and source of truth for delivery order, scope, dependencies, acceptance gates and exit criteria. The operational state is maintained in [docs/PROGRESS.md](docs/PROGRESS.md); durable choices are in [docs/DECISIONS.md](docs/DECISIONS.md); feature contracts are in [specs/](specs/).

## 1. Product scope

CRM Signals is an extension to ERPNext, not a replacement CRM. It captures business events, routes permission-aware notifications, provides a daily sales digest and adds the S.A.H.D.E.V. executive dashboard.

In scope:
- CRM Signal records and authenticated ingestion.
- Quotation and Opportunity event hooks, realtime notification routing and daily digest.
- CRM Signals Desk Console.
- S.A.H.D.E.V. D1 Sales Compass, D2 Billing Realization and D3 Service Resolution/SLA.
- H Highlights, A Analysis, E Explorer and V Vault, each delivered as a separately verified vertical slice.

Out of scope unless separately approved:
- Replacing Lead, Opportunity, Customer, Communication or ERPNext's CRM workflows.
- A general-purpose marketing automation or campaign product.
- An omnichannel inbox or replacement for email, WhatsApp, calling or support applications.
- A data warehouse containing replicated raw CRM/customer content.
- Arbitrary natural-language-to-SQL execution.

## 2. Current implementation baseline

The following capabilities are present in the repository. "Implemented" means the code and baseline tests exist; it does not mean target-site or production acceptance is complete.

| Capability | Code status | Remaining acceptance |
|---|---|---|
| Frappe app packaging and Pilot discovery metadata | Implemented | Run the actual Pilot import flow on the intended site |
| Read-only target-site preflight inventory | Implemented and CI-verified in PR #70 (merged as 13341b7) | Run on the authorized v16.5 target and review the report; effective user permissions and site acceptance remain manual |
| CRM Signal DocType and validation | Implemented | Validate installed schema, roles and customizations |
| Authenticated POST ingestion | Event-ID idempotency and concurrent duplicate recovery merged in PR #19/#23 | Verify with a dedicated target-site integration user and deployment rate limits |
| Quotation and Opportunity event hooks | Implemented; transactional outbox merged in PR #26 | Confirm target-site status/threshold policy; audited Failed-row replay merged in PR #38; per-company thresholds are in PR #45 merged |
| Record-level Signal permissions | Implemented | Verify list, direct form, report, export and API on target roles |
| Recipient-scoped realtime notifications | Implemented and CI-verified; PR #54 merged as `37ce600` | Stable delivery IDs, bounded retry, current permission rechecks and active-session dedupe; target-site Redis/worker recovery remains unverified |
| Daily CRM digest | Per-recipient queue tracking and cross-worker serialization merged in PR #19/#23 | Verify target-site semantics, timezone, recipient policy and live scheduler/mail behavior |
| CRM Signals Settings | Implemented and merged in PR #19 | Confirm the default Company currency, preset behavior and selected site configuration |
| CRM Signals Desk Console | Implemented | Target-site permission and usability smoke test |
| D1 Sales Compass | Implemented; PR #63 query-contract smoke and PR #67 synthetic Lead/Opportunity aggregate fixture are merged/CI-verified on Frappe v15/v16 and pinned v16.5.0 (PR #67 merge `84ab2ce`) | Verify target-site workflow/status semantics and role visibility |
| D2 Billing Realization | Implemented; PR #63 query smoke, PR #65 independent source-permission fix and PR #67 synthetic invoice/POS/receipt/receivable/overdue fixture are merged/CI-verified on Frappe v15/v16 and pinned v16.5.0 (PR #67 merge `84ab2ce`) | Reconcile totals/currency and validate Sales User/Manager permissions on the target site |
| D3 Service Resolution/SLA | Standard Frappe Helpdesk adapter and field-level guard merged in PR #32/#42; moving v15/v16 CI and exact Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 reference lane passed in PR #50 | Confirm the pilot site's exact app versions, Sales read-only role/field permissions and active SLA calendar |
| H Highlights | Partial; high-value Quotation events exist | Per-company threshold behavior merged in PR #45; target-site amounts and currency fallback still require approval. VIP allowlist/escalation and proposal-link tracking remain; tracking is gated on privacy/consent and retention approval |
| E Explorer | Core API, Desk UI and five-context browser coverage merged in PR #57/#59/#61; final-head CI verified | Target-site role/field-permission acceptance and optional-provider inventory remain |
| V Vault | Not implemented | Metric registry, retention and source-visibility policy |
| A Analysis | Not implemented | Approved metric/query registry and constrained intent mapping |

## 3. Delivery principles

1. **Spec first.** Every behavior change has a spec with source fields, edge cases, permissions, acceptance criteria and test mapping.
2. **Permission safety.** Use permission-aware reads. Never bypass user permissions to make a dashboard appear populated.
3. **Unavailable is not zero.** Missing fields, missing integrations, permission denial and unsupported semantics must be distinguishable from a valid empty result.
4. **Preserve source meaning.** Invoiced value is not cash received; Payment Entry receipts are not necessarily allocated to invoices; unlike currencies are never added.
5. **No guessed site configuration.** Configured business thresholds, statuses, timezones and source DocTypes must be observed and recorded.
6. **Idempotent event handling.** Replayed provider events and retried hooks must not create duplicate signals/alerts/snapshots.
7. **CI is necessary, not production acceptance.** Bench tests and target-site acceptance are separate gates.
8. **Every material choice is recorded.** Update docs/DECISIONS.md when scope, data semantics, security, architecture, compatibility or delivery order changes.

## 4. Delivery sequence

### Stage 0 — Repository security and reproducible CI

**Status:** Complete. PR #11 dependency/security hardening and PR #18 source-size/complexity guardrails are merged. Main ruleset [Protect main](https://github.com/MitMike/crm_signals/rules/26282133) is active and verified. PR #18 merged as [f51fbce](https://github.com/MitMike/crm_signals/commit/f51fbce19b7d1e84cfa6f3ab26118f2977a8fe40).

Work:
- Add weekly Dependabot checks for pip, npm and GitHub Actions.
- Keep npm development dependencies pinned and commit package-lock.json.
- Use npm ci in Quality Checks and Dependency Security Audit.
- Run pip-audit and npm audit --audit-level=moderate on relevant dependency pull requests, weekly and on manual dispatch.
- Keep Semgrep SARIF scanning and the Frappe v15/v16 Bench + Playwright matrix.
- [x] PR #76 merged as `cec49e7` after all 19 final-head check runs passed. ADR-075 preserves required check names, uses fail-closed path detection, covers workflow/DocType/Page/workspace/patch/fixture/package/requirements/app-config/module paths, retains full main/manual Bench validation, and prevents duplicate feature-branch Quality push runs. A docs-only PR should confirm that successful path detection allows Python/Bench execution to skip while stable required contexts pass. Workspace JSON intentionally remains in the Bench and pinned-stack selectors. PR #85 changed both workspace JSON and `tests/test_static_contracts.py`, so all four workflows ran; it did not prove the Python skip path. PR #89 is docs-only and is the current validation case for that optimization.
- [x] PR #84 restored the 24px horizontal inset on the dashboard and merged as `b1f4ad7` after all four required workflows passed; desktop/mobile UAT remains open.
- [x] PR #85 changed the Frappe workspace display label/title to GME CRM Signals, preserving technical identifiers and routes; merged as `5cc4308` after all four required workflows passed.
- [x] PR #88 upgraded `actions/upload-artifact` from v4 to v7 in both workflow sites; merged as `de8e78b` after all four required workflows passed. The project currently uses GitHub-hosted runners; future self-hosted runners must satisfy Node 24 requirements.
- Verify the existing main branch policy: required CI checks, PR-only updates, blocked force pushes/deletion and required review-thread resolution. Record allowed merge methods and the no-bypass emergency procedure.

Exit criteria:
- [x] PR #11 merged after all checks passed on its latest head.
- [x] package-lock.json is committed and npm jobs use npm ci.
- [x] Quality Checks, Bench Integration/E2E (v15/v16 + Playwright), Security Scanning and Dependency Security Audit passed on the final PR head. Post-merge Quality Checks, Security Scanning and Bench Integration/E2E also passed on main (runs 41232593555, 41232593543 and 41232593526).
- [x] Required-check enforcement is confirmed: Lint/static, Python 3.10/3.11/3.12/3.14, Semgrep, and Bench v15/v16. GitHub rejected PR #16 when 7 of 8 required checks were cancelled.
- [x] Ruleset Protect main verified active on refs/heads/main: PRs required; strict required checks; thread resolution; zero approval requirement; deletion and non-fast-forward blocked; merge/squash/rebase allowed; no bypass actors. An emergency requires an authorized administrator to edit the ruleset temporarily and revert it. [Issue #12](https://github.com/MitMike/crm_signals/issues/12) closed.

### Stage 1 — Release readiness and CRM core hardening

**Priority:** P0  
**Dependencies:** Stage 0.

Work:
- [x] **Pin-before-install correction (ADR-077; PR #82 merged as `ac030b1`, CI-verified):** direct clone CRM Signals with remote `upstream`, detach and verify the approved full SHA before `bench setup requirements crm_signals`, site install, migration or asset build; upgrade guidance verifies the Bench remote. Final head `ef4dc09` passed Quality, Security, Frappe v15/v16 Bench + Playwright and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. Authorized staging rehearsal and target-site acceptance remain open.
- Run a target-site preflight: framework versions, installed apps, Company default currency, timezone, roles, DocType metadata, workflows, custom fields and permissions.
- Configure a dedicated integration user, rotateable API credentials, HTTPS, gateway rate limiting and secret storage.
- Add source DocType, source document name and source event ID to CRM Signals; enforce idempotent inserts for identifiable events.
- Add a validated CRM Signals Settings singleton for the quotation threshold, Opportunity trigger statuses, Lead stale window, digest time and escalation recipients.
- [x] Fix D1 active-count handling when `status` metadata is missing. Implemented and merged in PR #17 as `fed496f`; regression tests and browser unavailable-state coverage are included.
- [x] Require `is_return` metadata for every return-sensitive D2 Sales Invoice measure. Implemented and merged in PR #17 as `fed496f`; no Sales Invoice aggregation runs without the return filter. Payment Entry receipts remain independent.
- [x] Add calibrated source file/function size standards, checker, pre-commit and CI integration. Implemented and merged in PR #18 as `f51fbce`.
- [x] Merge the settings, presets, event identity and digest foundation (PR #19, merged as `a495919`).
- [x] Merge the independent-connections API idempotency and overlapping-digest-worker hardening (PR #23); v15/v16 Bench, v16 Playwright, quality and security checks passed on the final head.
- Verify that CRM Signal list, direct-document, API, report and export permissions are equivalent.
- Verify that the current shared is_read flag is acceptable as a team acknowledgement.
- Confirm daily digest currency formatting, site timezone, recipients and duplicate-run behavior.
- Reconcile D2 invoice/receipt/outstanding totals against native ERPNext reports.
- Complete deployment runbook, rollback steps and webhook operational controls.

Exit criteria:
- [ ] Target-site discovery record completed and versioned.
- [ ] Sales User, Sales Manager, System Manager and non-sales test accounts pass the permission matrix.
- [ ] Ingestion and event retries do not duplicate signals.
- [ ] D1/D2 metrics match documented definitions and the target site's source reports.
- [ ] Settings are validated and defaults are confirmed/overridden for the site.
- [ ] Install, migrate, scheduler, notification, dashboard and rollback smoke tests pass on the selected site version(s).


### Merged Stage 1 implementation and verified reliability hardening

PR #19 merged as [a495919](https://github.com/MitMike/crm_signals/commit/a49591947a89b011cc1770be176c1f11571b131b). It delivers the System Manager-only CRM Signals Settings singleton, Balanced/Sales Focused/Executive presets, configurable event controls, SHA-256 source-event identity, webhook retry deduplication, permission-safe notification routing and per-recipient digest tracking.

PR #21 merged as [72833cd](https://github.com/MitMike/crm_signals/commit/72833cd383811d7c9be591206647b2e0b1f3fbd9). Its real `bench migrate` rehearsal preserved historical CRM Signal rows and restored event-identity fields on Frappe v15 and v16.

PR #23 merged as [d75b7f3](https://github.com/MitMike/crm_signals/commit/d75b7f3591d2a863b0af6b8f88ad2a91e9bfd25f). It closes two demonstrated concurrency defects:
- API duplicate recovery now loads the winning CRM Signal using a current locking read after a unique-key collision; a deterministic two-connection Bench test proves one Signal, one created response, one deduplicated response and one notification dispatch.
- Digest workers lock the Settings singleton and re-check each recipient/date marker before queueing. System-owned marker fields use `db_set` so a digest status update does not rerun unrelated administrator configuration validation; the queue row and marker remain in one transaction.

**Verification passed on final PR head `7ed0860`:** [Bench v15/v16 + Playwright](https://github.com/MitMike/crm_signals/actions/runs/41300667892), [Quality Checks](https://github.com/MitMike/crm_signals/actions/runs/41300667996) and [Security Scanning](https://github.com/MitMike/crm_signals/actions/runs/41300667997). Merge commit: `d75b7f3`.

The transactional signal outbox is merged in PR #26 and CI-verified on Frappe v15/v16. Audited Failed-row replay merged in PR #38. Durable per-recipient realtime notification retry merged in PR #54 as `37ce600`; final head `f1cbd3e` passed all eight required checks and the exact Frappe v16.5.0/ERPNext v16.5.0/Helpdesk v1.28.0 lane. Target-site Redis/worker/scheduler acceptance remains open. Company-specific quotation thresholds merged in PR #45; PR #49 fixes the child-row currency display/fetch behavior. The legacy site-wide threshold is a fallback only on an exact Company-currency match, with no implicit FX conversion. Target-site values, field-level permissions and production security remain external acceptance gates.

### Stage 2 — D3 Service Resolution/SLA

**Priority:** P1  
**Dependencies:** Stage 1 permission contract; owner-confirmed standard Frappe Helpdesk source; target-site version, field-level permission and SLA-calendar acceptance.

Work:
- Verify the target site has the standard `HD Ticket` and `HD Service Level Agreement` schema; record exact app versions and required fields.
- Map ticket lifecycle, resolution timestamp, native SLA outcomes, pause behavior, business calendar, timezone and DocType/field-level permissions.
- Maintain the merged Helpdesk adapter behind a normalized D3 metric contract; unavailable fields must remain unavailable, never silently become zero.
- Add permission-aware ticket volume, open backlog, resolutions, resolution duration and SLA compliance.
- Keep missing/unsupported sources visibly unavailable.

Exit criteria:
- [ ] Target-site record confirms Frappe v16.5 patch, ERPNext/Helpdesk versions and required DocTypes/fields.
- [ ] Business owner approves created/resolved cohorts and SLA denominator semantics.
- [ ] Sales User/Manager DocType and field-level permissions are tested; missing fields show unavailable.
- [ ] Active SLA working hours, holiday list and timezone are verified against the Monday–Saturday assumption.
- [x] Initial adapter unit/Bench v15/v16 and dashboard coverage passed in PR #32.
- [x] Field-level permission hardening merged in PR #42 and passed Bench v15/v16; target-site role policy remains open.

### Stage 3 — H Highlights

**Priority:** P1  
**Dependencies:** Stage 1 settings, recipient permissions and idempotency.

**Current implementation:** High-value Quotation alerts and Company-specific base-currency thresholds are implemented (PR #45/#49). The hook compares the Company base total with the Company threshold, falls back to transaction total only on an exact currency match, emits on submission at `>=` threshold and preserves the Quotation transaction amount in the message. Current recipients remain the linked party owner and active ToDo assignees, constrained to enabled System Users with read permission. PR #60 adds direct hook-level regression coverage. PR #71 adds a High-Value Quote source link in the CRM Signals Console only when the current user can read both CRM Signal source fields and the exact Quotation; it merged as `c5720bf` and final head `df0c273` passed Quality, Security, Python 3.10/3.11/3.12/3.14, Frappe v15/v16 Bench Integration/E2E including Playwright, and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. H-AC11 is code-complete and CI-verified, not pilot-verified; target-site Sales User/Manager/non-sales source-permission acceptance remains open. VIP membership and escalation routing are not defined well enough to implement safely; ADR-061 records the required product decision. Proposal-link tracking remains blocked by privacy/consent and retention approval.

Work:
- [x] Implement Company-specific quotation thresholds (PR #45/#49) with no implicit FX conversion and exact-currency fallback only.
- [x] Reuse CRM Signals for submitted-Quotation alerts, preserve source links and use stable submission event identity.
- [x] Route current quote alerts through existing owner/active-assignee recipients after enabled-user and source/party permission checks.
- [x] Add direct regression coverage for threshold equality, below-threshold suppression, base-total selection and same-currency fallback (PR #60).
- [ ] Confirm Company-by-Company threshold amounts/currencies and recipient behavior on the target site.
- [ ] Verify the High-Value Quote source link with target-site Sales User/Manager and non-sales accounts; PR #71's API and browser tests are reference CI evidence only.
- [ ] Add the admin-managed VIP Customer allowlist and escalation routing only after the product owner approves the triggering events, priority/threshold effect, recipients and cooldown (ADR-061).
- [ ] Add first-party proposal-link tokens stored as hashes, expiry and revocation only after privacy/consent and retention approval.
- [ ] Accept stable provider event IDs; deduplicate opens and throttle alert delivery.
- [ ] Exclude known scanners/previews from human-engagement alerts; never fingerprint browsers.
- [ ] Complete privacy/consent review and retention configuration before enabling proposal-link tracking.

Exit criteria:
- [ ] Target-site threshold, currency and recipient behavior pass multi-company Bench acceptance.
- [x] The code-level quotation hook is covered for threshold equality and suppression below threshold; existing outbox tests cover source-event deduplication/replay.
- [ ] Link tokens are opaque, expiring and revocable.
- [ ] Scanner, ambiguous and human event classifications pass tests.
- [ ] Privacy/consent approval and retention configuration are recorded.
- [ ] Playwright verifies the manager/user alert workflow.

### Stage 4 — E Explorer

**Priority:** P2  
**Dependencies:** Stage 1 permission contract; verified integrations and source event identities.

**Current implementation:** PR #57 is merged as `ba631720` after Quality Checks, Security Scanning, the Frappe v15/v16 Bench + Playwright matrix and the pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 lane passed on its final head. It provides read-only CRM Signal, Quotation and Opportunity adapters for Lead, Customer, Opportunity, CRM Signal and High-Value Quote contexts, metadata-only summaries, bounded snapshot pagination and fail-closed field-level permission checks. PR #59 is merged as `6b381fe` after all eight required ruleset contexts and the pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk v1.28.0 lane passed on final head `4bc7893513253d40ee60bb3a00b7c70827041eb9`. It adds the role-restricted Desk timeline page, form entry points, GET cursor paging, stale-response protection and Lead-context browser coverage. PR #61 merged as `6ef9642`; final head `902b38e4dd4713461acfb12dc837f5b2b84da7d8` passed all eight required contexts and the pinned v16.5.0 lane. It adds Playwright route coverage for all five contexts, stale-response suppression and operator runbook contracts. Optional providers remain deferred until the target-site inventory is recorded.

Work:
- [x] Merge the read-only CRM Signal, Quotation and Opportunity adapters and bounded timeline API (PR #57; CI verified).
- [x] Add the role-restricted Desk timeline page and Activity Timeline form actions (PR #59; merged and CI-verified).
- [x] Add GET cursor paging, source navigation, distinct source states and stale-response protection (PR #59; merged and CI-verified).
- [x] Add authenticated Playwright coverage for all five context routes and late-response suppression (PR #61; merged and CI-verified).
- [x] Maintain an explicit registry for the supported CRM Signal, Quotation and Opportunity sources; defer all optional provider adapters until site inventory.
- [x] Normalize source ID, event ID, timestamp, related party, safe summary and authorized source link for the first three sources.
- [x] Add stable snapshot pagination, deduplication and deterministic timestamp/source ordering.
- [x] Re-check permissions for every source row and link, including required field-level read access.
- [x] Keep message bodies, amounts, recordings and attachments out of the timeline payload.
- [ ] Add Communication/Event/ToDo/call/WhatsApp adapters only after target-site provider, schema, identity and permission inventory is approved.

Exit criteria:
- [ ] Installed/configured adapters and versions are recorded.
- [x] The initial adapters have contract, field-permission and compatibility tests; v15/v16 Bench and pinned v16.5 reference tests pass.
- [x] Duplicate IDs, equal timestamps, pagination and unavailable states pass unit/Bench tests.
- [x] Browser E2E verifies authenticated GET routes for Lead, Customer, Opportunity, CRM Signal and Highlight, paging/source drill-down and late-response suppression (PR #59/#61; CI verified).
- [ ] Verify actual form-action clicks and role-specific visibility with real target-site Sales User/Manager/non-sales accounts; static registration contracts do not replace live permission tests.

### Stage 5 — V Vault

**Priority:** P2  
**Dependencies:** Stable D1/D2 definitions; D3/H metrics only after they are accepted; approved retention and source-visibility policy.

**Status:** Blocked. D1/D2 have not been reconciled against the target site's native reports, and no source-visibility or retention/deletion policy has been approved. Keep snapshot scheduling disabled.

Work:
- Register approved metrics with definition versions.
- Create append-only daily aggregate snapshots with dimensions, source counts and provenance.
- Add idempotency, correction revisions and bounded admin-only backfill.
- Store aggregates only; do not copy customer names, raw documents or free-text content.
- Keep snapshot scheduling disabled until a retention period and source-visibility policy are explicitly configured.
- Implement audited dry-run pruning before retention deletion is enabled.

Exit criteria:
- [ ] Metric registry is versioned and approved.
- [ ] Retention and source visibility are approved and configured.
- [ ] Duplicate, correction, backfill, permission and pruning tests pass.
- [ ] Monetary snapshots preserve currency groups.
- [ ] Manager Vault view and historical comparisons pass Bench/E2E.

### Stage 6 — A Analysis

**Priority:** P2  
**Dependencies:** Stable D1/D2/D3/H metric registry; Stage 1 permission contract.

**Status:** Blocked until Sales/Finance approve the D1/D2 metric definitions, currency/date/filter semantics and target-site source permission matrix. Do not expose query intents before that evidence exists.

Work:
- Start with a deterministic catalog of approved sales questions.
- Map text to a constrained metric ID, date range, filter and grouping.
- Execute only server-owned versioned query definitions using permission-aware Frappe reads.
- Optionally use an LLM for constrained intent classification only; never accept generated SQL, Python, DocTypes, fields or executable queries.
- Return results with metric definition version, filters, period, unit/currency and authorized source links.

Exit criteria:
- [ ] Every supported question maps to an approved registry entry.
- [ ] Unknown/ambiguous questions fail closed.
- [ ] Generated SQL execution is impossible by design.
- [ ] Permission, date-range, pagination and currency tests pass.
- [ ] Deterministic templates work without an LLM.
- [ ] Playwright covers useful question/answer and unavailable states.

## 5. Dependency map

- Stage 0 is a prerequisite for all merges.
- Stage 1 hardens the shared CRM Signals data, event and permission contract.
- D3 uses the standard Frappe Helpdesk adapter when that app is installed; the discovery guide and read-only preflight verify the pilot's exact Helpdesk version, ticket fields and SLA policy before enabling site acceptance.
- H depends on settings, idempotency and recipient permission checks.
- E depends on source adapter discovery and permission-safe event identities.
- V depends on accepted metric definitions and an explicit retention/source-visibility policy.
- A depends on the approved metric registry produced by D1/D2/D3/H.

Do not implement downstream cards before their data source is accepted. Do not build Vault or Analysis on metrics that are still semantically provisional.

## 6. Definition of done for every slice

A slice is done only when all applicable items are complete:
- Spec accepted and linked from this plan.
- Source DocTypes/fields, data types, date windows, currency basis and edge cases are documented.
- Role and record-level permission behavior is tested.
- Missing/unavailable/empty states are distinguished.
- Unit tests pass.
- Bench integration tests run on both supported Frappe/ERPNext lines where applicable.
- Playwright covers user-visible behavior.
- Migrations are forward/backward assessed and exercised.
- Operational settings, failure behavior and rollback are documented.
- docs/PROGRESS.md, docs/DECISIONS.md and CHANGELOG.md are updated.
- Latest CI evidence is linked; production/target-site acceptance is recorded separately.

## 7. Specifications catalogue

| Area | Specification | State |
|---|---|---|
| CRM Signals data, ingestion and access | [Core and access](specs/2026-11-01-crm-signals-core-and-access.md) | Baseline implemented; release hardening open |
| Settings and core reliability | [Settings, presets and idempotency](specs/2026-11-01-settings-and-core-reliability.md) | PR #19 and concurrency hardening PR #23 merged; v15/v16 Bench, Playwright, quality and security passed |
| Document events and realtime routing | [Events and notifications](specs/2026-11-01-crm-signals-events-and-notifications.md) | Settings/idempotency merged in PR #19; concurrent API recovery in PR #23; durable per-recipient realtime retry merged in PR #54 and CI-verified; pilot recovery remains |
| Daily digest | [Digest](specs/2026-11-01-crm-signals-daily-digest.md) | Per-recipient tracking and overlapping-worker serialization merged in PR #19/#23; live policy open |
| D1 | [Sales Compass](specs/2026-11-01-pillar-d1-sales-compass.md) | Implemented; PR #63 query-contract smoke and PR #67 synthetic aggregate-value fixture merged/CI-verified on v15/v16 and pinned v16.5.0; target-site validation open |
| D2 | [Billing Realization](specs/2026-10-31-pillar-d2-billing-realization.md) | Implemented; PR #63 query smoke, PR #65 independent permission fix, PR #67 synthetic aggregate-value fixture and PR #69 real POS invoice settlement merged/CI-verified on v15/v16 and pinned v16.5.0; target-site native-report reconciliation and role acceptance open |
| D3 | [Service Resolution/SLA](specs/2026-11-01-pillar-d3-service-resolution-sla.md) | Adapter, exact v16.5.0 reference CI and aggregate fixture verified in PR #50/#53; pilot-site source/permission/SLA acceptance remains |
| H | [Highlights](specs/2026-11-01-pillar-h-highlights.md) | Partial: high-value quotation signals, per-Company thresholds and PR #71 permission-gated source Quotation drill-down are merged and CI-verified; target-site persona acceptance remains. VIP escalation and proposal tracking remain gated on product, privacy/consent and retention decisions |
| A | [Analysis](specs/2026-11-01-pillar-a-analysis.md) | Planned |
| E | [Explorer](specs/2026-11-01-pillar-e-explorer.md) | Core API, Desk UI and five-context browser coverage merged and CI-verified; target-site role/source acceptance remains |
| V | [Vault](specs/2026-11-01-pillar-v-vault.md) | Planned |

## 8. Release blockers and external inputs

The following cannot be safely inferred from source code or CI and must be observed on the intended site:
- Frappe/ERPNext version and installed support/communication integrations.
- Company default currency and any company-specific currency conventions.
- Site timezone and scheduler execution timezone.
- Opportunity workflow/status values and terminal Lead statuses.
- Support-ticket DocType and SLA field/lifecycle semantics.
- Sales User/Sales Manager permissions, custom roles and DocType customizations.
- Actual invoice, receipt and receivable totals for financial reconciliation.
- Privacy/consent approval and retention policy for proposal-link tracking and historical snapshots.

The project can continue implementing source-independent work while these inputs are pending. Site-dependent metrics or tracking must remain unavailable/disabled until they are validated.



## 9. Historical repository maintenance snapshot — 2026-11-03 (superseded by Sections 10–13)

Latest main at this review is [`b18f504`](https://github.com/MitMike/crm_signals/commit/b18f5045cb218b351bd9e3033577b03767847014). PR #97 reconciled the maintenance snapshot after PR #94 and merged as `b18f504` after its final-head Quality, Security and Bench Integration/E2E checks passed. PR #8 (setup-node v7) and PR #94 (setup-python v7) are merged; PR #7 (setup-uv v7) remains merged as `331492c`.

PR #96 is the only open pull request in this snapshot. It updates the build-system range to `flit_core >=3.4,<5` and adds explicit wheel/sdist build and isolated-install verification using flit-core v4 on Python 3.10 and 3.14. The package artifacts are built with the installed v4 backend; the wheel and source distribution are each installed in a clean virtual environment and imported. Final-head Quality, Security, Python, Frappe v15/v16 Bench + Playwright and pinned Frappe v16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 checks must pass before merge. Existing PR #96 checks on the pre-PR-97 base are not reusable; its branch is refreshed onto `b18f504`.

The product baseline remains code-complete and reference-stack CI-verified for D1/D2, D3, Explorer and H-AC11. The pin-before-install operator procedure is CI-verified. Target-site configuration, effective-role permissions, financial reconciliation, Helpdesk SLA calendar, scheduler/mail/realtime/webhook operations, deployment rollback and dashboard desktop/mobile visual UAT remain open acceptance gates. No pilot verification is inferred from repository CI.


## 10. Maintenance update — 2026-11-03

PR #96 (flit-core v4 build-system compatibility) merged as `d0ab24b6a50184af99f4af638ae64ddd9a22d08a` after all 20 final-head checks passed on `349bf71b0687c77e830fb8b054cedacabb16f61b`. The checks cover Python 3.10/3.11/3.12/3.14, Security/Semgrep, Python/npm dependency audits, Frappe v15/v16 Bench + Playwright, and the pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 lane. The dedicated flit-core v4 wheel and sdist build/install/import checks passed on Python 3.10 and 3.14. No open PRs remained immediately after merge.

This closes the current dependency-maintenance queue. It does not close target-site acceptance: the authorized v16.5 staging preflight, effective-role tests, D1/D2 reconciliation, Helpdesk SLA confirmation, operational recovery checks, rollback rehearsal and dashboard desktop/mobile visual UAT remain open. Keep code-complete, reference-stack CI-verified and pilot-verified states distinct.


## 11. Post-PR #98 merge status — 2026-11-03

Current main is `1a27166bfe988c860b3527af5bba9a0299e1e30f` (PR #98). Its final-head documentation-only checks passed, including required Quality, Security and Bench v15/v16 validation; test-surface detection correctly skipped runtime execution for this docs-only diff. No open PRs remained immediately after merge.

The PR #96 packaging change remains reference-stack CI-verified. This documentation merge does not change pilot status: dashboard desktop/mobile visual UAT and target-site v16.5 preflight, role permissions, financial reconciliation, Helpdesk SLA, operational recovery and rollback rehearsal remain outstanding.


## 12. Dashboard inset regression prevention — 2026-11-03

PR #99 reconciled the post-PR #98 documentation and merged as `6a46c26b3a58a3ea035d7e53b15bc2f8839e2bb5` after all 13 final-head checks passed. The next focused change is PR #100: a Playwright assertion for the CRM Signals dashboard wrapper's computed horizontal padding at desktop (1440px: 24px each side) and mobile (390px: 12px each side). This closes the automated regression-prevention gap recorded by BUG-2026-001 / FIX-2026-001; it does not close manual visual UAT or target-site acceptance.


The first PR #100 path-detection review exposed a CI selector gap: the Bench filter did not include `e2e/**` or `playwright.config.ts`, so an E2E-only change could skip the browser runner. ADR-084 adds both paths to the Bench selector and a static contract test. The v16 Bench job now runs the new Playwright regression test; final-head CI passed and PR #100 merged. See Section 13 for the final evidence.


## 13. PR #100 complete; staging acceptance is the next release gate — 2026-11-03

PR #100 merged as 9c4febf8180ef295b48ea18b1ac5fddc164ff34f from final head 50759954b8801fb8edd7194fea354c3521b457f1. All 18 final-head check runs completed successfully: Quality/lint and Python 3.10/3.11/3.12/3.14, Security/Semgrep, pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0, Bench v15 and v16, and the v16 Playwright browser suite. The browser suite now asserts 24px left/right padding at 1440px and 12px at 390px; ADR-084 ensures changes under e2e/** and playwright.config.ts trigger Bench validation.

The automated dashboard regression guard is code-complete and reference-stack CI-verified. Manual staging visual UAT is still open. The repeatable screenshot/evidence procedure is now in [Target-Site Acceptance Kit §11](docs/TARGET_SITE_ACCEPTANCE.md#11-dashboard-horizontal-inset-visual-acceptance).

**Next priority:** execute dashboard visual UAT and the P0 target-site acceptance gates on an authorized Frappe v16.5 staging site. Do not start Vault/Analysis, VIP escalation, proposal tracking or optional Explorer adapters until their metric, permission, privacy, retention and source contracts are approved. No target site is connected to this work; do not claim pilot verification or infer site configuration from CI.



## 14. Read-only preflight release identity — 2026-11-03

ADR-086 closes an operator evidence gap without guessing site configuration: `crm_signals.diagnostics.get_site_preflight_report` now includes `framework.crm_signals_source`. It executes only a fixed `git rev-parse --verify HEAD` query from the imported CRM Signals package directory, bounded by a five-second timeout. Only a valid full 40-character hexadecimal SHA is accepted; missing Git, a non-Git checkout, timeout or invalid output is an explicit unavailable state with no path or stderr disclosure.

The administrator guide and target-site acceptance kit require that SHA to match the approved release revision before installation or migration proceeds. If the diagnostic cannot report it, operators must stop and inspect the checkout manually; branch names and package versions are not substitutes.

**Verification state:** implementation and focused unit tests are committed on `ops/preflight-source-sha-20261103`; final-head CI is pending. The feature is not yet CI-verified and has no target-site or pilot evidence. Existing Frappe/ERPNext v15/v16 coverage and the pinned Frappe v16.5.0 / ERPNext v16.5.0 / Helpdesk 1.28.0 lane remain required.
