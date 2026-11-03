# CRM Signals — Product and Engineering Delivery Plan

**Last reviewed:** 2026-11-03  
**Repository:** [MitMike/crm_signals](https://github.com/MitMike/crm_signals)  
**Supported framework coverage:** Frappe / ERPNext v15 and v16. **Primary deployment target:** Frappe v16.5; record the exact patch/build and installed ERPNext/Helpdesk versions.  
**Reviewed main baseline:** [aa2e211](https://github.com/MitMike/crm_signals/commit/aa2e2112be4956f270cd730375c8da1e3d396f1f) (PR #131's final-head verification is reconciled by merged documentation PR #132); **latest application feature baseline:** [c5720bf](https://github.com/MitMike/crm_signals/commit/c5720bfb3fbe8b554ec6febd549a8d5e58acc1d7).

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
| Read-only target-site preflight inventory | Implemented and CI-verified in PR #70; optional effective-user DocType/field, bounded synthetic-record list, and Sales User record-filter probes are CI-verified in PRs #120, #122 and #124; PR #126 adds real-Frappe `frappe.client.get` / `get_list` permission-wrapper coverage and is merged/CI-verified; PR #130 adds browser-session HTTP permission coverage on Frappe v16 and pinned v16.5, merged/CI-verified; PR #131 adds direct CRM Signal form-load permission coverage, pending | Run on authorized v16.5 staging and review the actual site inventory/permission matrix; authenticated HTTP transport, browser form, report/export/print/dashboard and release acceptance remain manual |
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
- Run a target-site preflight: framework versions, installed apps, Company default currency, timezone, roles, DocType metadata, workflows, custom fields and permissions. ADR-092 / PR #120 adds an optional explicit synthetic-user DocType/field probe; ADR-094 / PR #122 adds a bounded name-only `frappe.get_list` visibility probe for explicitly supplied synthetic records. Direct form/API/report/export/print/dashboard acceptance remains separate.
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

ADR-086 closes an operator evidence gap without guessing site configuration: `crm_signals.diagnostics.get_site_preflight_report` now includes `framework.crm_signals_source`. It executes fixed read-only Git queries from the imported CRM Signals package directory: `git status --porcelain --untracked-files=all`, followed by `git rev-parse --verify HEAD` only when the working tree is clean. Each command has a five-second timeout. Only a valid full 40-character hexadecimal SHA from a clean checkout is accepted; dirty state, missing Git, a non-Git checkout, timeout or invalid output is an explicit unavailable state with no path or stderr disclosure.

The administrator guide and target-site acceptance kit require that SHA to match the approved release revision before installation or migration proceeds. If the diagnostic cannot report it or detects local changes, operators must stop and inspect the checkout manually; branch names and package versions are not substitutes.

**Verification state:** merged as PR #103 / `5dbda0291358350d5a720127a7d526145d3e3c60` from final head `fc7f0ae381267d04d7db9f14ec888d965c7fe828`. All 18 final-head check runs passed, including Python 3.10–3.14, Quality, Security/Semgrep, Bench v15/v16 with v16 Playwright E2E, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0. The feature is code-complete and CI-verified, not pilot-verified; no target-site execution has been performed.


## 15. Preflight repository-root identity hardening — merged and CI-verified (2026-11-03)

ADR-087 records a source-identity edge case: Git searches parent directories, so a clean app directory nested under another repository could otherwise report the enclosing repository's commit. The preflight now verifies `git rev-parse --show-toplevel` resolves to the CRM Signals repository root derived from the imported package path before checking working-tree cleanliness and `HEAD`. A mismatch is an explicit unavailable state (`repository_root_mismatch`); the diagnostic never returns the enclosing repository SHA.

PR #105 merged as [`db95812`](https://github.com/MitMike/crm_signals/commit/db958124bca6a6704a75f606629c22444716f5b9) from final head `fd2161dc933fbaf74fd5a50a5261e5f1501b283e`. Its 19 final-head check runs all completed successfully: Quality/lint, Python 3.10/3.11/3.12/3.14, Security/Semgrep, Bench v15/v16 (including the v16 Playwright lane), and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation. The corrected dirty-checkout assertion verifies root validation precedes status and that `HEAD` is not read for a dirty tree.

The administrator guide, target-site acceptance kit and deployment runbook require the root check. **Status: code-complete and reference-stack CI-verified; not pilot-verified.** Revisit the root derivation only if the package layout changes, the app is installed without a Git checkout, or Bench's app layout changes; add a matching-layout regression test before changing the rule.


## 16. Real-Git regression for nested parent repository discovery — PR-opening plan (2026-11-03)

ADR-088 adds a focused test using an actual temporary Git repository. It creates a committed parent repository and a nested Bench-style `apps/crm_signals/crm_signals` package directory without its own Git metadata, then invokes the real preflight Git commands and requires `repository_root_mismatch`. This complements the mocked tests, which continue to cover dirty state, missing Git, timeout, command failure and malformed SHA output.

The test changes no runtime code and requires no Frappe site. It verifies Git's actual upward repository discovery behavior that ADR-087 is intended to reject. At PR opening, #107 was code-complete with CI pending; the final merge and verification are recorded in Section 17. This is not pilot verification.


## 17. Real-Git parent-repository regression — merged and CI-verified (2026-11-03)

ADR-088's regression test is merged in PR #107 as [`a472f19`](https://github.com/MitMike/crm_signals/commit/a472f1981f758ce7b6233d95fc0682fe69d7a304), from final head `a47c3975eebe52dccb918a1056cf30d818cdcae4`. The test creates a committed temporary parent repository, places a Bench-style `apps/crm_signals/crm_signals` package path beneath it without a child repository, invokes the real `_source_revision()` helper and requires `repository_root_mismatch`. This exercises Git's actual upward repository discovery rather than mocking the root output.

All 19 final-head check runs completed successfully across Quality/Python 3.10–3.14, Security/Semgrep, Bench v15/v16 including v16 Playwright, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation. All four required workflows completed successfully. No runtime behavior or target-site configuration changed.

**Status:** code-complete and reference-stack CI-verified; not pilot-verified. Main is `a472f1981f758ce7b6233d95fc0682fe69d7a304`. The next release gate remains authorized target-site staging evidence: exact deployed SHA, effective-role permissions, D1/D2 finance reconciliation, Helpdesk SLA, operational recovery, rollback rehearsal and desktop/mobile visual UAT. Do not infer any of these from CI.


## 18. Real-Git clean and untracked-dirty source identity regression — PR-opening snapshot (merged; see Section 19)

PR #108 merged as `c31fe7eb328f552cf49f670257370189f09da9e2`; its documentation-only reconciliation passed all 11 applicable checks, with two runtime selectors skipped as expected.

ADR-089 adds a real temporary CRM Signals Git checkout test. It commits the package `__init__.py`, invokes the production `_source_revision()` helper and requires the exact real `HEAD` SHA for a clean tree. It then creates an untracked Python override and requires `working_tree_dirty`, verifying the helper does not proceed to `HEAD`. This complements ADR-087/088's root-identity tests and the mocked timeout/missing-Git/invalid-output cases.

[PR #109](https://github.com/MitMike/crm_signals/pull/109) was test-only; no runtime code or target-site configuration changed. Its opening status was code-complete with CI pending; final merge evidence is recorded in Section 19. This is not pilot verification.


## 19. Real-Git clean/dirty source identity regression — merged and CI-verified (2026-11-03)

PR #109 merged as [`94d14f5`](https://github.com/MitMike/crm_signals/commit/94d14f56a526670d2c0ecb150ab9f08b4f034389) from final head `d8b65eedc45c05947409f9781a9caaee848aa4ba`. All 18 final-head check runs completed successfully: Quality/lint, Python 3.10/3.11/3.12/3.14, Security/Semgrep, Bench v15/v16 including v16 Playwright, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation.

The real-Git test commits a temporary CRM Signals package, verifies the production preflight returns the exact clean `HEAD` SHA, adds an untracked Python override, then verifies `working_tree_dirty` without a `HEAD` query. This complements ADR-087/088's repository-root tests and the mocked error-path tests. No runtime behavior or site configuration changed.

**Status:** code-complete and reference-stack CI-verified; not pilot-verified. Main at merge is `94d14f56a526670d2c0ecb150ab9f08b4f034389`. The release gate remains authorized Frappe v16.5 staging evidence: deployed full SHA, effective-role permissions, D1/D2 finance reconciliation, Helpdesk SLA, operational recovery, backup/restore/rollback and dashboard visual UAT. Do not infer these from CI.


## 20. PR #110 release-document reconciliation — merged (2026-11-03)

PR #110 merged as [`fe7dca4`](https://github.com/MitMike/crm_signals/commit/fe7dca402293faa1e7e60f147d53adaef63009d6) from final head `f4904b7bd88725017f5f2254de9ceb3c123163cc`. All 13 final-head check runs completed: 11 succeeded and two runtime selectors were skipped as expected for the documentation-only diff. Quality/lint, Security/Semgrep, Python version gates and stable Bench v15/v16 validation passed.

The PR refreshed the release-readiness sprint and historical production-audit notice, reconciled the implementation/progress/follow-up records and changelog, and corrected the README's obsolete D3 implementation prerequisite. D3 is implemented; target-site Helpdesk version/schema/field permissions and active SLA calendar acceptance remain open.

**Status:** documentation complete and reference CI-verified. Main is `fe7dca402293faa1e7e60f147d53adaef63009d6`; the live repository query immediately after merge returned no open PRs or issues. Production sign-off remains blocked by authorized Frappe v16.5 target-site acceptance. No pilot verification is claimed.


## 21. PR #111 release-document reconciliation — merged (2026-11-03)

PR #111 merged as [`166ca6b`](https://github.com/MitMike/crm_signals/commit/166ca6b2cc9838ffd68c551b327ee41d2a5316b4) from final head `30d44ffd48a1f39ef39d658a6bdc12b07f8130da`. All 13 final-head checks completed: 11 passed and two runtime selectors were skipped as expected for the documentation-only diff. Main commit `166ca6b` subsequently completed 17 check runs: 16 passed and the docs-only integration-test selector was skipped. No application behavior or target-site configuration changed.

## 22. README pin-before-install consistency correction — PR #112 opening snapshot (2026-11-03)

ADR-090 corrects the root README's first-install command. The former `bench get-app ... --branch main` example contradicted the Administrator Guide and Deployment Runbook: Bench installs dependencies from the fetched tree before returning, so a later SHA checkout cannot guarantee the installed tree was the approved release.

The README now uses the established safe order: direct clone with the `upstream` remote, fetch, detach at the approved full SHA, verify `HEAD`, then run `bench setup requirements crm_signals`, site install, migration, asset build and restart. Existing-install upgrades link to the detailed operator procedure.

PR #112 updates documentation and the static operator-installation contract test; no runtime or dependency changes. The test change must trigger Python 3.10–3.14, Bench v15/v16 and pinned Frappe 16.5.0 validation in addition to Quality and Security. **Status at opening:** documentation and static regression code-complete, CI pending, not pilot-verified.

**Next release gate remains unchanged:** execute the first-install and upgrade sequence, preflight, effective-role tests, D1/D2 finance reconciliation, Helpdesk SLA acceptance, dashboard visual UAT, operational recovery and backup/restore/rollback on an authorized Frappe v16.5 staging site. No such site evidence is available from repository CI.


## 23. README pin-before-install correction — PR #112 merged (2026-11-03)

PR #112 merged as [`d2e1d87`](https://github.com/MitMike/crm_signals/commit/d2e1d873a8f257545596379e179aeb3e4de40dd4) from final head `f68939ba5e2977ed62698e2a78084277fa091479`. All 18 final-head check runs passed: Quality/lint, Python 3.10/3.11/3.12/3.14, Security/Semgrep, Bench integration v15/v16 including Playwright, and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation.

The README now uses the same safe sequence as the operator guide: clone directly into `apps/crm_signals`, fetch the approved release, detach at and verify the full SHA, then run Bench dependency setup and site installation/migration/build. The static contract test protects the command order. No runtime behavior, dependency or site configuration changed.

**Status:** documentation/static-test work is merged and reference-stack CI-verified; the staging first-install/upgrade rehearsal remains open and this is not pilot verification.

## 24. D3 operator-guide implementation status and custom-source boundary

The Support & SLA setup guide now states that the standard Frappe Helpdesk `HD Ticket` / `HD Service Level Agreement` adapter is implemented and directs operators to validate the target site's exact versions, schema, field permissions and active SLA calendar. The D3 discovery guide's custom-DocType FAQ now explicitly says custom/different ticket sources are outside the standard adapter and remain unavailable until support, security and business owners approve a separate adapter scope, mapping and KPI semantics. Static contract coverage protects both statements.

No runtime code, dependencies, schema or site configuration changed. **Status at PR opening:** documentation and static regression code-complete; final-head CI pending; not pilot-verified. Final verification and merge evidence are recorded in Section 25.

**Target-site gate:** D3 remains not pilot-verified until authorized Frappe v16.5 staging confirms exact Helpdesk version/schema, effective Sales field permissions, active SLA schedule/holidays/timezone, pause/resume behavior and native metric outcomes.


**CI triage (PR-opening run):** Python 3.11 and 3.12 each exposed one static-contract failure (125 passed, 36 skipped, 1 failed). The assertion correctly found a second stale promise in the Support & SLA setup guide's final workflow list: "We build a small adapter for the support app actually installed." The same page also carried the wrong "Read-only discovery guide" footer. Both are corrected: the page now instructs operators to compare and configure the existing standard adapter, requires separate approval for custom sources, and has the correct Support and configuration guide footer. The static test now rejects both stale statements. Re-run the complete final-head matrix; do not merge based on the earlier passing lint/Semgrep results or the initial failed Python run.


**Second CI triage:** on head `87a5f8f479d291ddaf119c8d4938a9a2d30d54bc`, Python 3.11, 3.12 and 3.14 each reported 1 failed, 125 passed and 36 skipped. The guide correction was present; the static test still expected the old phrase `separately scoped adapter change`, while the revised guide correctly says `custom sources require separate approval and scope`. Updated the assertion to the actual operator wording. This was a test expectation mismatch, not a runtime or product defect. Require a fresh full matrix on the corrected head.


## 25. D3 operator-guide correction — PR #117 merged (2026-11-03)

PR #117 merged as 93e7e16 (merge commit 93e7e16271d727476618b4981498ad901835bad4) from final head 2d7463f5e73bec3741ef9fb68d9b707b9bb1afc6. All 35 final-head check runs passed: Python 3.10–3.14, lint/static checks, Semgrep, Bench v15/v16 including Playwright, pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation and both bench-validation selectors.

The D3 Support & SLA setup guide now describes the implemented standard Helpdesk adapter, its actual validation/configuration sequence and separate approval for custom sources. The discovery FAQ enforces the same boundary. Static tests protect the implementation status, custom-source scope and guide footer. Two early CI failures were fixed and retained as historical evidence; no failing head was merged. No runtime code, dependency, schema or site configuration changed.

Status: D3 guide and static regression are merged and reference-stack CI-verified. They are not pilot-verified.

Remaining target-site gate: authorized Frappe v16.5 staging must confirm exact Helpdesk version/schema, effective Sales field permissions, active SLA schedule/holidays/timezone, pause/resume behavior and native metric outcomes. The README first-install/upgrade rehearsal, D1/D2 native-report reconciliation, desktop/mobile visual UAT, scheduler/mail/realtime/webhook recovery and backup/restore/rollback remain separate site acceptance work.


## 26. PR #118 documentation reconciliation merged (2026-11-03)

PR #118 merged as 3cb9f017b1694727f0b1729d5e2af9a7913a7715. All 11 applicable final-head checks passed; the two runtime selectors were skipped as expected for the documentation-only change. It records PR #117's 35/35 final-head verification and the remaining target-site acceptance gates. No runtime code, dependency, schema or site configuration changed.

Main at this reconciliation point: 3cb9f017b1694727f0b1729d5e2af9a7913a7715. The live repository query returned no open PRs or issues. Main-push Quality/Security checks for this documentation merge were still running at the time of review; PR final-head checks passed.


## 27. Effective-user permission preflight — PR #120 opening snapshot (2026-11-03)

ADR-092 adds an optional, read-only effective DocType/field permission probe to the existing target-site inventory. The operator supplies aliases mapped to dedicated active synthetic accounts; the code does not search for or choose site users. It validates the expected Sales User, Sales Manager, System Manager or non-sales role boundary, then calls Frappe's `has_permission(..., user=..., throw=False)` and `Meta.get_permitted_fieldnames(user=...)` for the installed preflight DocTypes. Only profile aliases, permission outcomes, status and exception type are returned; account names/emails, credentials and business-document rows are not included.

The Administrator Guide, Deployment Runbook and Target-Site Acceptance Kit document the optional `--kwargs` invocation. The output proves only DocType-level and required-field-level read access for the supplied accounts. Row-level User Permissions, ownership, shares, list filters, API/report/export and dashboard visibility still require controlled-record acceptance on the site.

**Status at PR opening:** code-complete; CI pending. Tests cover allowed/denied DocType and field results, disabled and Administrator rejection, absent-user unavailable state, unknown alias rejection and identity non-disclosure. Final-head Python 3.10–3.14, Quality, Security/Semgrep, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation are required before merge. This is not pilot verification.

**Release blocker remains:** no authorized Frappe v16.5 staging session, approved full SHA, named owners or synthetic site accounts are available in this repository review. Revisit only when those inputs are supplied; then run the optional probe and the full controlled-record permission matrix, finance reconciliation, Helpdesk SLA, deployment/rollback and operational recovery acceptance. Do not treat reference-stack CI as site evidence.


## 28. Effective-user permission preflight — merged and CI-verified (2026-11-03)

PR #120 merged as [`a778c47`](https://github.com/MitMike/crm_signals/commit/a778c47b5078ac69dd89bdcd3ecab41de09b8072) from final head `e95efccec019df3fbadd1703f34c5682340b7f58`. All 18 final-head check runs passed: Quality/lint, Python 3.10–3.14, Security/Semgrep, Bench v15/v16 with Playwright and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation.

The optional read-only preflight accepts explicit aliases for active, distinct System User accounts; validates the Sales User, Sales Manager, System Manager and non-sales role boundaries; and reports Frappe user-aware DocType and required-field read outcomes without returning account identities or business rows. The CI-only `allow_tests` fixture exercised the production preflight on real Frappe v15, v16 and pinned v16.5.0 disposable sites. It creates no business documents and does not establish row-level permission or pilot acceptance.

**Status:** code-complete and reference-stack CI-verified; not pilot-verified. The target-site permission matrix still requires controlled-record tests for User Permissions, ownership, shares, list filters, API/report/export and dashboard behavior. The broader P0 gates remain exact deployed SHA/version inventory, D1/D2 native-report reconciliation by currency, Helpdesk SLA calendar and metrics, first-install/upgrade, scheduler/mail/realtime/webhook/worker recovery, backup/restore/rollback and desktop/mobile visual UAT. No authorized staging evidence is available; do not infer it from CI.



## 29. Synthetic-record list-visibility preflight — PR #122 (2026-11-03)

ADR-094 adds an optional, non-whitelisted `test_records` input to the existing Bench preflight. It accepts exact synthetic record names only for explicitly supplied test-user profiles, known preflight business DocTypes and lowercase non-sensitive labels; limits each profile to 50 records and the request to 100 total. The probe switches to each validated System User, uses permission-filtered `frappe.get_list` with `fields=["name"]`, and returns labels/booleans only. Missing and inaccessible records both return false. Direct form/API/report/export/print/dashboard behavior remains a separate target-site gate.

A review found and corrected a session-safety edge case: if `frappe.set_user(test_user)` mutated the current session and then raised, the old error path returned before restoration. The corrected path records the exception type, marks requested results unavailable and always attempts to restore the original user in a shared `finally`. A regression injects the mutate-then-raise behavior and verifies restoration and non-disclosure.

**Status:** PR #122 merged as `de16ead`; all four final-head workflows passed after the session-restoration correction. Code-complete and reference-stack CI-verified; not pilot-verified. Authorized Frappe v16.5 staging remains required for actual role/record acceptance.


## PR #122 merged — synthetic-record list visibility (2026-11-03)

PR [#122](https://github.com/MitMike/crm_signals/pull/122) merged as [de16ead](https://github.com/MitMike/crm_signals/commit/de16ead6ed2f155e83189196755048a264c2ec74) from final head [5339d71](https://github.com/MitMike/crm_signals/commit/5339d7135ff87902974dc2d038051e101434389e).

All four final-head workflows completed successfully: Quality Checks (run 41603744414), Security Scanning/Semgrep (41603744435), Bench Integration and E2E (41603744404), and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation (41603744511). The Quality run passed the configured Python 3.10, 3.11, 3.12 and 3.14 test jobs plus lint/static checks. Bench v15/v16 integration passed, including the v16 Playwright job. The pinned lane passed the real-Frappe synthetic-record visibility probe, D1/D2 aggregate/permission checks, Helpdesk schema and D3 aggregate checks, schema upgrade, asset build, Python tests and Frappe integration tests.

The first Python run had five failures from a stale helper signature; it was corrected and the final-head matrix passed. A separate review correction ensured a frappe.set_user call that mutates session state and then raises still flows through the restoration finally; the final-head regression verifies restoration is attempted, no list query runs and record names/exception messages are not disclosed. No failing head was merged.

The optional preflight is code-complete and reference-stack CI-verified, not pilot-verified. It checks bounded permission-filtered list visibility for exact supplied synthetic records and returns labels/booleans only. Direct form, REST API, report, export, print and dashboard access remain separate acceptance paths. Authorized Frappe v16.5 staging, approved release SHA, named owners and controlled synthetic records are still required for pilot acceptance, alongside D1/D2 native-report reconciliation, Helpdesk SLA, deployment/rollback, operational recovery, backup/restore and desktop/mobile UAT.


## PR #124 opening snapshot — real Sales User record-filter preflight regression (2026-11-03)

- **Reviewed main:** `c9df68e3728fe675e4eb3b4d5dafaf8b4d29fcc6` (PR #122 and PR #123 merged; no open PRs or issues at branch creation).
- **Finding:** PR #122's real-Frappe preflight smoke proves a System Manager can list a synthetic CRM Signal, but does not invoke the new `test_records` path for a restricted Sales User. The existing Bench permission test already creates a Sales User, a linked Lead excluded by a User Permission, and an unlinked signal owned by that user.
- **Decision (ADR-095):** reuse that controlled fixture to call `get_site_preflight_report(test_users=..., test_records=...)` and assert the probe reports the linked/restricted signal as false and the unlinked/owned signal as true. Assert the result is checked, the original session user is restored, and neither record name nor user identity is returned.
- **Scope:** integration-test-only; no runtime behavior, schema, dependency or site configuration change. The existing Bench v15/v16 + Playwright and pinned Frappe 16.5.0 workflows execute the integration test suite.
- **Status at opening:** code-complete; final-head Quality, Python, Security/Semgrep, Bench v15/v16 and pinned Frappe 16.5.0 checks pending. Not pilot-verified.
- **Revisit criteria:** if Frappe v15/v16 returns a different list result, inspect the real `crm_signal_query` and User Permission behavior; do not weaken the expected false/true boundary or replace permission-filtered `get_list` with `get_all`. Authorized target-site direct form/API/report/export/print/dashboard tests remain separate.


## 30. Sales User record-filter preflight regression — PR #124 merged (2026-11-03)

PR #124 merged as [af94b14](https://github.com/MitMike/crm_signals/commit/af94b14038250b75ebc849e424779432d57dee98) from final head [0c7a6bf](https://github.com/MitMike/crm_signals/commit/0c7a6bfc77c3ee9df7189007c0326491906aca76). All four final-head workflows passed: Quality Checks (run 41614477641, configured Python 3.10/3.11/3.12/3.14 jobs and lint/static checks), Security Scanning/Semgrep (41614477907), Bench Integration and E2E (41614477805; Frappe v15 and v16 integration passed, with v16 Playwright passed), and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation (41614477749). The real-Frappe Sales User fixture confirmed a linked CRM Signal excluded by the Lead User Permission is not visible while an unlinked signal owned by the same user remains visible. The report returned checked status, restored the original session user and disclosed neither user nor record names.

The new regression reuses the real Frappe User Permission fixture: a Sales User owns both signals, but a linked CRM Signal whose Lead is excluded by that user's Lead User Permission is hidden; an unlinked signal owned by the same user remains visible. The test exercises the production get_site_preflight_report(test_users=..., test_records=...) path and asserts checked status, session restoration and name/identity non-disclosure. It does not replace target-site direct form/API/report/export/print/dashboard acceptance or the broader release gates.


## 31. Exercise Frappe document/list API permission wrappers — PR #126 opening snapshot (2026-11-03)

- **Finding:** PR #124 proves the preflight's permission-filtered list probe against a real Sales User User Permission, but the target-site checklist separately requires the standard single-document and list API paths. The integration suite did not directly invoke Frappe's `frappe.client.get` and `frappe.client.get_list` wrappers for the linked-restricted/unlinked-owned pair.
- **Decision (ADR-096):** reuse the same disposable Sales User/Lead/User Permission/CRM Signal fixture. As that user, assert `frappe.client.get` raises `PermissionError` for the linked restricted signal, returns the unlinked owned signal, and `frappe.client.get_list` returns only the unlinked signal. Always restore the original session user.
- **Scope:** integration-test and operator-guide coverage only; no runtime, schema, dependency, metric or site configuration change. CI must run on Frappe v15/v16 and pinned v16.5.0. Direct authenticated HTTP, browser form, reports, exports, print and dashboard checks remain target-site acceptance.
- **Status at opening:** code-complete; final-head CI pending. Not pilot-verified.


### PR #126 first CI triage — Ruff import ordering

- **Observed:** Quality Checks lint failed on head `a5998ec` with Ruff `I001` for the local `frappe.client` import in the integration test helper. The Python 3.11/3.12/3.14 unit jobs passed; Python 3.10 and the Frappe integration/pinned workflows were still running at triage.
- **Decision:** keep the test import-safe when Frappe is not installed by moving the two API wrapper imports into the module's existing guarded `try` block beside `import frappe` and `FrappeTestCase`. Do not suppress or relax Ruff's import-order rule.
- **Correction:** import `frappe.client.get` and `get_list` in the guarded Frappe block; remove the local import from the helper. A fresh final-head matrix is required.
- **Revisit criteria:** if Ruff still reports `I001`, use its exact `--fix` ordering while retaining the `ModuleNotFoundError` fallback; if Bench reports an API wrapper mismatch, inspect the pinned v15/v16 implementation and keep the denied/allowed assertions intact.


### PR #126 second CI triage — guarded import still fails Ruff I001

- **Observed:** Quality Checks on head `97ac553` failed the same Ruff `I001` at the guarded import block (`crm_signals/tests/test_notification_permissions.py:7`); the first attempted correction moved aliased `frappe.client` imports into the existing `try` block but did not satisfy Ruff's ordering rule.
- **Decision:** import the `frappe.client` module itself (`import frappe.client`) inside the existing guarded block and call `frappe.client.get` / `frappe.client.get_list`. This preserves the no-Frappe unit-test fallback and removes the aliased member import ordering ambiguity.
- **Correction:** replace the aliased imports and rerun the full final-head matrix. Do not suppress I001 or relax lint.
- **Revisit criteria:** if I001 persists, retrieve Ruff's exact `--fix` diff from the job or run the pinned Ruff 0.8.1 formatter against the file before another commit; if the integration test fails after lint passes, inspect the exact v15/v16 API result and keep the denied/allowed assertions intact.


### PR #126 review correction — restore session when the initial user switch raises

- **Finding:** final-head CI passed, but review found the API helper called `frappe.set_user(test_user)` immediately before its `try`. If that call changed session state and then raised, the `finally` restoration would not run.
- **Decision:** move the initial user switch inside the existing `try`, so every attempted switch is covered by restoration. Keep the original user captured before the switch and retain the denied/allowed API assertions.
- **Status:** the prior head `30a3890a994a3402b4efdf15732843f86a62b789` passed all four workflows (Quality/Python, Semgrep, Bench v15/v16 + Playwright, pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0). This correction creates a new head and requires a fresh complete matrix before merge.
- **Revisit criteria:** if the new matrix fails, inspect the exact v15/v16 API wrapper and session behavior. Do not move the switch back outside the `try`, bypass permissions, or weaken the linked-denied/unlinked-allowed assertions.


## 32. Direct document/list API permission wrappers — PR #126 merged (2026-11-03)

PR #126 merged as [812aa1e](https://github.com/MitMike/crm_signals/commit/812aa1eb76fbabc0e7f73a664caa72a1e208feb6) from final head [24d12ac](https://github.com/MitMike/crm_signals/commit/24d12acb50613c25f71fc2d809b464e311ba7f3e). All four final-head workflows passed: Quality Checks (run 41634012616; lint/static plus Python 3.10/3.11/3.12/3.14), Security/Semgrep (41634012907), Bench Integration and E2E (41634012673; Frappe v15/v16 integration and v16 Playwright), and pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 validation (41634012853). The pinned lane completed effective-user permission checks, D1/D2 query/aggregate checks, Helpdesk schema/read-role and D3 aggregate checks, schema upgrade, asset build, Python tests and Frappe integration tests.

The real-Frappe Sales User/User Permission fixture now invokes `frappe.client.get` and `frappe.client.get_list`: the linked CRM Signal whose Lead is excluded by the Sales User's Lead User Permission is denied by the document wrapper, the unlinked owned signal is readable, and the list wrapper returns only the unlinked signal. The initial `frappe.set_user` call is inside the restoration `try/finally`. The corrected final head is code-complete and reference-stack CI-verified; it is not pilot-verified. These tests call Frappe's Python method wrappers directly and do not validate HTTP authentication/cookies/routing or browser form loading. Keep those as authorized Frappe v16.5 staging checks, alongside reports/exports/print/dashboard, D1/D2 native-report reconciliation by currency, D3 SLA calendar behavior, deployment/rollback, operational recovery, backup/restore and desktop/mobile UAT.


## 33. Reproducible authenticated Sales User HTTP acceptance — PR #128 opening snapshot (2026-11-03)

- **Finding:** PR #126 now verifies `frappe.client.get` and `frappe.client.get_list` by calling their Python wrappers directly in real-Frappe CI. The Target-Site Acceptance Kit previously named the GET endpoints but did not provide exact query parameters, credential identity validation, expected HTTP statuses or safe response handling. Operators could not execute the check consistently without constructing requests themselves.
- **Decision (ADR-097):** add a copy/paste Bash/curl/Python standard-library smoke procedure. It requires HTTPS, checks `frappe.auth.get_logged_user` against the explicitly expected dedicated Sales User (never Administrator), stores the API token header in a mode-0600 temporary curl config, does not follow redirects, stores response bodies in a private temporary directory and removes them on exit. It expects 403 for the linked restricted document, 200 for the unlinked owned document and exactly the unlinked record from the permission-filtered list.
- **Scope:** operator documentation only. No runtime, schema, dependency or site configuration changes. This verifies HTTP authentication/routing for these method endpoints only when run on authorized staging; browser form, REST resource, report/export/print/dashboard and all business/operational acceptance remain separate.
- **Status at opening:** guide change complete; documentation PR checks pending. Not pilot-verified until executed on the approved target site with sanitized evidence.
- **Revisit criteria:** if the target Frappe build returns a different documented status or response shape, capture only sanitized status/error class and version, inspect that version's API wrapper and exception mapping, then update the guide without using Administrator credentials or weakening the record boundary.


## 34. Authenticated Sales User HTTP acceptance procedure — PR #128 merged (2026-11-03)

PR #128 merged as [85c492e](https://github.com/MitMike/crm_signals/commit/85c492ea2c84444d7cc45c0d61706736fa972a83). The Target-Site Acceptance Kit now provides a copy/paste HTTPS-only procedure that verifies the API token identity against the dedicated synthetic Sales User, rejects Administrator, expects 403 for the linked restricted CRM Signal, expects 200 for the unlinked owned signal, and requires `frappe.client.get_list` to return only the unlinked record. The procedure stores the Authorization header in a mode-0600 temporary curl config, does not follow redirects, keeps response bodies in a private temporary directory and removes them on exit. The Administrator Guide links to the procedure.

All applicable final-head checks passed: Quality Checks run `41639851748` (Python 3.10/3.11/3.12/3.14 and lint/static), Security/Semgrep run `41639851870`, and Bench Integration/E2E path selectors run `41639851663`. Bench runtime and Python workflow runtime selectors were skipped as expected for documentation-only changes; no pinned Frappe workflow was triggered. The extracted Bash procedure passed `bash -n`; ShellCheck was unavailable and is not claimed. This is an operator-guide improvement, not a site execution or pilot verification. Execute it only on authorized Frappe v16.5 staging with the approved SHA and synthetic records; browser form and remaining acceptance paths remain separate.


## 35. Browser-session HTTP permission regression on Frappe v16 and pinned v16.5 — PR #130 opening snapshot (2026-11-03)

- **Finding:** PR #126 exercises Frappe's Python method wrappers directly, and PR #128 documents an API-token HTTP smoke. The v16 Playwright suite had no real Sales User/User Permission fixture or cookie-session HTTP assertion for the linked-restricted/unlinked-owned CRM Signal pair. The pinned Frappe 16.5 workflow did not run Playwright at all.
- **Decision (ADR-098):** extend the disposable E2E site setup to create an allowed and restricted Lead, a Sales User Lead User Permission, a linked restricted CRM Signal owned by that user and an unlinked owned signal. Assert the fixture's permission-filtered list result before browser tests. Add a Playwright test that authenticates as Administrator to discover only the synthetic fixture names, switches to the dedicated Sales User, then calls `frappe.client.get` and `get_list` over same-origin browser-session HTTP: linked document 403, unlinked document 200, list only the unlinked signal. Run the E2E suite on both Frappe v16 and exact pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0.
- **Scope:** CI fixture and test workflow only; no production runtime, schema, dependency or site configuration change. The API-token smoke, browser form route, REST resource, report/export/print/dashboard and wider site acceptance remain separate.
- **Status at opening:** implementation committed on the focused branch. The first Quality run caught the fixture helper exceeding the repository's 100-nonblank-line hard limit (102 lines); split lead/signal setup into focused helpers. The next Quality run passed Ruff/code standards and Python but flagged Prettier formatting in the E2E spec; applied the formatter's exact layout. Review then found the new pinned Playwright step used `npm install` instead of the repository-required lockfile-enforced `npm ci`; ADR-098 records the npm-ci correction, duplicate-entry cleanup and masking of generated ephemeral E2E passwords before step-output propagation. Fresh final-head Quality, Security, Bench v15/v16 and pinned v16.5 Playwright checks are required. Not pilot-verified.
- **Revisit criteria:** if the linked record returns anything other than 403, or the list contains it, inspect Frappe v15/v16 User Permission and CRM Signal query conditions; do not use Administrator for the assertions or weaken the denied/allowed boundary. If pinned E2E exceeds the workflow timeout, profile setup/install/browser steps before raising the timeout.


## PR #130 — Frappe v16.5 login-route compatibility correction (2026-11-03)

The first complete PR #130 final-head matrix passed Quality/Python, Security/Semgrep and the supported Frappe v15/v16 Bench + Playwright workflow. The pinned Frappe 16.5.0 job completed setup, all preflight/D1/D2/Helpdesk/schema checks, E2E fixture setup, asset build, Python tests, Frappe integration tests, browser installation and server startup, then failed in the new Playwright test's shared login helper. Artifact trace evidence shows Frappe v16.5 submitted POST /login with HTTP 200, while the helper waited exclusively for POST /api/method/login. ADR-099 accepts both exact POST routes and adds a static regression guard. The corrected head must pass all four workflows before merge. This is a test-harness compatibility correction, not a runtime permission failure or pilot verification.



## 36. PR #130 — pinned Frappe 16.5 Sales User identity assertion correction (2026-11-03)

- **Evidence:** corrected head b6128589c40d3b2c7bedf639cc62d1ab3bd16f77 passed Quality, Security and supported Frappe v15/v16 Bench + Playwright. Pinned Frappe 16.5.0 run 41647478405 passed site/app setup, preflight, D1/D2, Helpdesk, schema upgrade, E2E fixture creation, asset build, Python and Frappe integration tests, browser installation and server startup. Playwright then failed at the precondition expect(roles).toContain("Sales User") because the helper returned an empty array from frappe.core.doctype.user.user.get_current_user_roles. It did not reach any document/list permission assertion.
- **Decision (ADR-100):** validate the synthetic user's Sales User role in the server-side fixture via frappe.get_roles(sales_user), then validate the browser session with frappe.auth.get_logged_user and exact email equality before the HTTP permission requests.
- **Implementation:** remove the version-sensitive currentUserRoles browser helper; add the server-side role guard, browser identity assertion and static regression test. Retain linked document 403, unlinked document 200 and list-only-unlinked assertions.
- **Status:** correction code-complete on PR #130. Require all four final-head workflows on the corrected commit before merge. Not pilot-verified.
- **Revisit criteria:** if role fixture validation fails, inspect the User role rows and Frappe role API; if session identity fails, inspect the exact login route, session cookie and identity endpoint response. Do not remove identity validation or weaken permission expectations.



### PR #130 — static-test follow-up for both Sales and non-sales browser identities (2026-11-03)

The first ADR-100 correction changed a separate Sales User dashboard test but left currentUserRoles references in both the new HTTP permission test and the Employee dashboard test. Quality/Python run 41663119127 caught this in the static contract (Python 3.12: 141 passed, 36 skipped, one failed). The Employee test was converted to exact frappe.auth.get_logged_user identity verification; final full-file review then removed the remaining role lookup from the new HTTP test. The fixture validates the Sales User and Employee role boundaries server-side and rejects elevated Sales Manager/System Manager roles. All four workflows must pass on the new final head; the failed head is not mergeable. Not pilot-verified.



### PR #130 — final HTTP permission test identity assertion correction

Full-file review found that the new Sales User HTTP permission test still called currentUserRoles after the earlier broad replacement changed a separate Sales User dashboard test. The remaining call is now replaced with frappe.auth.get_logged_user and exact synthetic email equality. The Employee dashboard test uses the same identity check, and server-side fixture setup validates both role boundaries. The Python static-contract failure remains a failed result for its original head; all four workflows must rerun on the corrected head.



### PR #130 — corrected final-head CI run IDs

Corrected head fd855ae056c81b16defa1eac6085ab481ef08ac9 is under fresh verification: Quality Checks 41663665399, Security/Semgrep 41663665370, Bench Integration/E2E 41663665401 and pinned Frappe 16.5.0 / Helpdesk 1.28.0 41663665390. At this review, Security's Semgrep job was in progress and the other three runs were pending. Do not merge until all four pass on this exact head.

### PR #130 final-head CI triage — deterministic non-sales role fixture

The final-head Quality and Security workflows passed on `7525c1521835e93245faf5840c0af1c47f9d590b`, but the pinned Frappe 16.5.0 and supported v16 Bench executions both failed before browser tests at the synthetic Employee role-boundary assertion in `crm_signals/ci.py:176`. Site setup, preflight, D1/D2, Helpdesk and schema-upgrade steps had completed. The CI log did not expose the effective role set, so the precise reason the built-in Employee role was absent is not asserted.

ADR-101 replaces that assumption with a CI-only custom `CRM Signals E2E Non-Sales` Desk role (enabled, `desk_access=1`), assigned to the synthetic non-sales System User. The fixture still rejects Sales User, Sales Manager and System Manager, and the browser still verifies exact session identity. The Sales User linked-denied/unlinked-allowed/list-only-unlinked HTTP expectations are unchanged. Code commits: `eb55ca5` and static guard `1e7c911`. Require a fresh complete four-workflow final-head matrix before merge; no pilot verification is implied.

## 37. Direct CRM Signal form-load permission regression — PR #131 opening snapshot (2026-11-03)

- **Reviewed main:** `2b697b4d37a12b2e339bcf680ff808f23b97850f` (PR #130 merged after all four final-head workflows passed).
- **Finding:** PR #130 verifies the standard `frappe.client.get` and `get_list` methods over an authenticated browser session. A direct Desk form route uses `frappe.desk.form.load.getdoc` (GET), which loads the document, calls `doc.check_permission("read")` and applies field-level read permissions. That path was not exercised by the prior browser test.
- **Decision (ADR-102):** navigate as the synthetic Sales User to `/app/crm-signal/<name>` for the linked-restricted and unlinked-owned fixture records. Require the form loader request to return 403 without the restricted signal message; require 200 for the unlinked signal and verify its message is present in the loaded document. Include the new test in both the supported v16 Playwright lane and pinned Frappe 16.5.0 Playwright lane; retain the existing HTTP API test. Enforce lockfile-based `npm ci` in both Bench E2E workflows and guard it with static tests (ADR-103).
- **Scope:** disposable CI fixture and operator-guide coverage only. No production runtime, schema, dependency or site configuration change. Report/export/print/dashboard and target-site browser acceptance remain separate.
- **Status:** code-complete on focused branch `test/sales-user-direct-form-permission-20261103`; final-head Quality/Python, Security, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 workflows pending. Not pilot-verified.
- **Revisit criteria:** if the form route or loader method differs on v15/v16, inspect the exact Frappe router and `frappe.desk.form.load.getdoc` behavior. Keep the linked-denied/unlinked-allowed boundary and do not substitute Administrator for the Sales User assertion.


## 38. PR #131 merged — direct CRM Signal form-load permission regression (2026-11-03)

PR #131 merged as [08f269c](https://github.com/MitMike/crm_signals/commit/08f269cdfaedc58fd4ce396c823d589e7dd3481b) from final tested head [a72ebff](https://github.com/MitMike/crm_signals/commit/a72ebffbae116adf06830473bb15d764a169651b).

All four final-head workflows passed:
- Quality Checks run [41676858036](https://github.com/MitMike/crm_signals/actions/runs/41676858036): lint/static checks and Python 3.10, 3.11, 3.12 and 3.14.
- Security/Semgrep run [41676862616](https://github.com/MitMike/crm_signals/actions/runs/41676862616).
- Bench Integration/E2E run [41676858619](https://github.com/MitMike/crm_signals/actions/runs/41676858619): Frappe v15 integration passed; Frappe v16 integration and the complete 18-test Playwright suite passed.
- Pinned Frappe 16.5.0 / ERPNext 16.5.0 / Helpdesk 1.28.0 run [41676858020](https://github.com/MitMike/crm_signals/actions/runs/41676858020): the focused three-test Playwright selection passed after site installation, preflight, D1/D2, Helpdesk, schema upgrade, Python and Frappe integration checks.

The direct Desk form test observed GET `frappe.desk.form.load.getdoc`: linked-restricted CRM Signal returned 403 without its message; unlinked-owned signal returned 200 with the expected message. The same-head browser-session HTTP API tests also passed. The supported v15 lane passed Bench integration; the v16 lane ran the full Playwright suite. No failing head was merged.

**Classification:** code-complete and reference-stack CI-verified on Frappe v16 and pinned v16.5.0; not pilot-verified. Authorized target-site API-token authentication, live direct-form and other permission paths, D1/D2 finance reconciliation, D3 SLA, deployment/rollback, operational recovery and visual UAT remain open.


## 39. PR #133 — API-token authentication permission regression (2026-11-03)

## PR #133 — synthetic Sales User API-token permission regression

- **Reviewed main:** `aa2e2112be4956f270cd730375c8da1e3d396f1f` (PR #131 merged and CI-verified; PR #132 reconciled the final verification and operator records).
- **Finding:** PR #130/131 verify the same Sales User record boundary through browser-session HTTP and direct Desk form loading. The operator kit has an API-token smoke, but CI did not exercise Frappe's token authentication or prove the requests could not fall back to the Administrator browser cookie.
- **Decision (ADR-104):** generate API credentials for the disposable Sales User with Frappe's supported `generate_keys` function. Write them only to a runner temporary file with mode 0600; return only a boolean from Bench; mask both values before GitHub step-output propagation; remove the file with an EXIT trap. Use Node's native fetch (outside the Playwright page/trace) with an explicit `Authorization: token key:secret` header and manual redirect handling. Verify token identity, linked-restricted 403, unlinked-owned 200 and list-only-unlinked.
- **Scope:** disposable CI fixture, E2E workflow and operator guide only. No production runtime, schema, dependency, permission or site configuration change. Keep Frappe v15 Bench integration; run the token E2E in supported v16 and pinned Frappe 16.5.0.
- **Status:** implementation code and static regression guards are committed on `test/sales-user-api-token-permission-20261103`; final-head Quality/Python, Security, Bench v15/v16 + Playwright and pinned Frappe 16.5.0 validation pending. Not pilot-verified.
- **Revisit criteria:** if `generate_keys` or token auth differs by version, inspect the exact v15/v16 implementation; do not fall back to Administrator credentials or session cookies. If any request redirects, fail rather than follow it. Keep API credentials out of Playwright traces/artifacts and logs; if a test failure reveals a credential, revoke it by discarding the ephemeral site and correct the handling before rerun.
