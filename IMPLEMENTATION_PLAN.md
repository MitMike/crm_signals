# CRM Signals — Product and Engineering Delivery Plan

**Last reviewed:** 2026-11-02  
**Repository:** [MitMike/crm_signals](https://github.com/MitMike/crm_signals)  
**Supported framework coverage:** Frappe / ERPNext v15 and v16. **Primary deployment target:** Frappe v16.5; record the exact patch/build and installed ERPNext/Helpdesk versions.

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
| CRM Signal DocType and validation | Implemented | Validate installed schema, roles and customizations |
| Authenticated POST ingestion | Event-ID idempotency and concurrent duplicate recovery merged in PR #19/#23 | Verify with a dedicated target-site integration user and deployment rate limits |
| Quotation and Opportunity event hooks | Implemented; transactional outbox merged in PR #26 | Confirm target-site status/threshold policy; audited Failed-row replay merged in PR #38; per-company thresholds merged in PR #45 as `ff434bdf` after all 16 required checks passed; PR #49 then fixed Company-row currency auto-fetch/display and passed v15/v16 CI |
| Record-level Signal permissions | Implemented | Verify list, direct form, report, export and API on target roles |
| Recipient-scoped realtime notifications | Implemented | Validate target-site assignments/permissions and failure isolation |
| Daily CRM digest | Per-recipient queue tracking and cross-worker serialization merged in PR #19/#23 | Verify target-site semantics, timezone, recipient policy and live scheduler/mail behavior |
| CRM Signals Settings | Implemented and merged in PR #19 | Confirm the default Company currency, preset behavior and selected site configuration |
| CRM Signals Desk Console | Implemented | Target-site permission and usability smoke test |
| D1 Sales Compass | Implemented; missing-status fix merged in PR #17 | Verify target-site status semantics and role visibility |
| D2 Billing Realization | Implemented; return-metadata guard merged in PR #17 | Reconcile totals and currency basis against target-site reports |
| D3 Service Resolution/SLA | Standard Frappe Helpdesk adapter and field-level fail-closed guard merged in PR #32/#42; v15/v16 CI verified; exact Frappe v16.5.0 reference stack verified in PR #50 | PR #50 merged as `24a9b8d`; the pinned Frappe v16.5.0 + ERPNext v16.5.0 + Helpdesk v1.28.0 + Telephony lane passed install, schema/permlevel/read-role checks, D3 aggregate smoke test, upgrade, asset build, Python tests and Frappe tests. Confirm the pilot site's exact versions, Sales permissions and active SLA calendar |
| H Highlights | Partial; high-value Quotation events exist | Per-company threshold behavior merged in PR #45; each Company row requires explicit approval and no implicit FX conversion. VIP allowlist/escalation and proposal-link tracking remain; tracking is gated on privacy/consent and retention approval |
| E Explorer | Not implemented | Verify installed activity integrations and source adapters |
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

The transactional signal outbox and audited Failed-row replay are merged in PRs #26 and #38 and CI-verified on Frappe v15/v16. Source-document read checks for realtime notifications merged in PR #44; durable realtime retry remains deferred per ADR-053 until a per-recipient delivery ledger, stable ID, permission recheck and client deduplication/acknowledgement exist. Company-specific thresholds merged in PR #45; each row requires an explicit approved amount, currency changes require reapproval, and no implicit FX conversion is performed. Target-site values, field-level permissions and production security remain external acceptance gates.

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

Work:
- [x] Merge Company-specific quotation thresholds in PR #45; verify every enabled Company's approved threshold or exact-currency fallback during pilot acceptance.
- Reuse CRM Signals for the quote alert and preserve source links; verify one alert per submission identity.
- Add the admin-managed VIP Customer allowlist and escalation routing after product approval.
- Add first-party proposal-link tokens stored as hashes; support expiry and revocation only after privacy/consent and retention approval.
- Accept stable provider event IDs; deduplicate opens and throttle alert delivery.
- Exclude known scanners/previews from human-engagement alerts; never fingerprint browsers.
- Complete privacy/consent review before enabling proposal-link tracking.

Exit criteria:
- [ ] Quote threshold, currency and recipient behavior pass multi-currency Bench tests.
- [ ] Replayed events create one signal/alert.
- [ ] Link tokens are opaque, expiring and revocable.
- [ ] Scanner, ambiguous and human event classifications pass tests.
- [ ] Privacy/consent approval and retention configuration are recorded.
- [ ] Playwright verifies the manager/user alert workflow.

### Stage 4 — E Explorer

**Priority:** P2  
**Dependencies:** Stage 1 permission contract; verified integrations and source event identities.

Work:
- Build an adapter registry for CRM Signal, Quotation, Opportunity and only those Communication/Event/call/WhatsApp sources verified on the target site.
- Normalize source ID, event ID, timestamp, related party, safe summary and authorized source link.
- Add stable pagination, deduplication and timezone-consistent sorting.
- Re-check permissions for every source row and link.
- Do not duplicate full source messages, recordings or attachments.

Exit criteria:
- [ ] Installed/configured adapters and versions are recorded.
- [ ] Each adapter has contract, permission and compatibility tests.
- [ ] Duplicate IDs, equal timestamps, pagination and unavailable states pass tests.
- [ ] Playwright covers timeline entry points and source drill-downs.

### Stage 5 — V Vault

**Priority:** P2  
**Dependencies:** Stable D1/D2 definitions; D3/H metrics only after they are accepted; approved retention and source-visibility policy.

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
- D3 requires target-site support application discovery; it does not assume a standard ticket DocType.
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
| Document events and realtime routing | [Events and notifications](specs/2026-11-01-crm-signals-events-and-notifications.md) | Settings and idempotency merged in PR #19; concurrent API duplicate recovery verified in PR #23 |
| Daily digest | [Digest](specs/2026-11-01-crm-signals-daily-digest.md) | Per-recipient tracking and overlapping-worker serialization merged in PR #19/#23; live policy open |
| D1 | [Sales Compass](specs/2026-11-01-pillar-d1-sales-compass.md) | Missing-status correction merged; target-site validation open |
| D2 | [Billing Realization](specs/2026-10-31-pillar-d2-billing-realization.md) | Return-metadata guard merged; target-site reconciliation open |
| D3 | [Service Resolution/SLA](specs/2026-11-01-pillar-d3-service-resolution-sla.md) | Discovery spec ready; source mapping gated |
| H | [Highlights](specs/2026-11-01-pillar-h-highlights.md) | Planned |
| A | [Analysis](specs/2026-11-01-pillar-a-analysis.md) | Planned |
| E | [Explorer](specs/2026-11-01-pillar-e-explorer.md) | Planned |
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
