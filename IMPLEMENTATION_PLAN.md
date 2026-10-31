# CRM Signals — Product and Engineering Delivery Plan

**Last reviewed:** 2026-11-01  
**Repository:** [MitMike/crm_signals](https://github.com/MitMike/crm_signals)  
**Supported framework target:** Frappe / ERPNext v15 and v16

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
| Authenticated POST ingestion | Implemented | Test with a dedicated integration user and deployment rate limits |
| Quotation and Opportunity event hooks | Implemented | Confirm thresholds/statuses and add durable idempotency |
| Record-level Signal permissions | Implemented | Verify list, direct form, report, export and API on target roles |
| Recipient-scoped realtime notifications | Implemented | Validate target-site assignments/permissions and failure isolation |
| Daily CRM digest | Implemented | Confirm semantics, currency, timezone, recipients and retry safety |
| CRM Signals Desk Console | Implemented | Target-site permission and usability smoke test |
| D1 Sales Compass | Implemented | Harden missing-status handling and verify target-site status semantics |
| D2 Billing Realization | Implemented | Reconcile totals and currency basis against target-site reports |
| D3 Service Resolution/SLA | Not implemented | Discover and map the installed support/SLA source first |
| H Highlights | Partially present for quote events | Settings, source-event idempotency, VIP link tracking/privacy review |
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

**Status:** Merged in [PR #11](https://github.com/MitMike/crm_signals/pull/11) as [05ad767](https://github.com/MitMike/crm_signals/commit/05ad767f6b62814cca5b7d0c1e233a2f690baa77). All four gates passed on the PR head; post-merge Bench validation is being confirmed on main. The branch ruleset remains an administrator task tracked in [issue #12](https://github.com/MitMike/crm_signals/issues/12).

Work:
- Add weekly Dependabot checks for pip, npm and GitHub Actions.
- Keep npm development dependencies pinned and commit package-lock.json.
- Use npm ci in Quality Checks and Dependency Security Audit.
- Run pip-audit and npm audit --audit-level=moderate on relevant dependency pull requests, weekly and on manual dispatch.
- Keep Semgrep SARIF scanning and the Frappe v15/v16 Bench + Playwright matrix.
- Configure a main branch ruleset requiring the agreed CI checks and disabling ordinary direct pushes.

Exit criteria:
- [x] PR #11 merged after all checks passed on its latest head.
- [x] package-lock.json is committed and npm jobs use npm ci.
- [x] Quality Checks, Bench Integration/E2E (v15/v16 + Playwright), Security Scanning and Dependency Security Audit passed on the final PR head. Post-merge Quality Checks and Security Scanning also passed on main; the fresh post-merge Bench run was still completing v16 when this plan was updated.
- [ ] main ruleset is verified to require the checks. [Issue #12](https://github.com/MitMike/crm_signals/issues/12) tracks the administrator action because the connected GitHub integration cannot write/read repository rulesets.

### Stage 1 — Release readiness and CRM core hardening

**Priority:** P0  
**Dependencies:** Stage 0.

Work:
- Run a target-site preflight: framework versions, installed apps, Company default currency, timezone, roles, DocType metadata, workflows, custom fields and permissions.
- Configure a dedicated integration user, rotateable API credentials, HTTPS, gateway rate limiting and secret storage.
- Add source DocType, source document name and source event ID to CRM Signals; enforce idempotent inserts for identifiable events.
- Add a validated CRM Signals Settings singleton for the quotation threshold, Opportunity trigger statuses, Lead stale window, digest time and escalation recipients.
- Fix D1 active-count handling when a required status field is missing: mark status-dependent metrics unavailable, never count every row as active.
- Require is_return metadata for D2 measures whose contract says "exclude returns"; mark the relevant measure unavailable if the filter cannot be safely applied.
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

### Stage 2 — D3 Service Resolution/SLA

**Priority:** P1  
**Dependencies:** Stage 1 target-site discovery and source permission review.

Work:
- Inventory installed support applications and authoritative ticket/SLA DocTypes.
- Map ticket status, creation timestamp, resolution timestamp, SLA deadline/outcome, pause state, business calendar, timezone and permissions.
- Implement source-specific adapters behind a normalized D3 metric contract.
- Add permission-aware ticket volume, open backlog, resolutions, resolution duration and SLA compliance.
- Keep missing/unsupported sources visibly unavailable.

Exit criteria:
- [ ] D3 discovery map is completed against the target site.
- [ ] Business owner approves cohort and SLA definitions.
- [ ] Unit and Bench tests cover lifecycle, pause/calendar behavior, permissions and edge cases.
- [ ] Dashboard and Playwright tests cover values, unavailable and empty states.
- [ ] Frappe/ERPNext v15 and v16 CI remains green.

### Stage 3 — H Highlights

**Priority:** P1  
**Dependencies:** Stage 1 settings, recipient permissions and idempotency.

Work:
- Make high-value quotation threshold configurable in Company default currency.
- Reuse CRM Signals for the quote alert and preserve source links.
- Add VIP Customer allowlist and escalation routing.
- Add first-party proposal-link tokens stored as hashes; support expiry and revocation.
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
| CRM Signals data, ingestion and access | [Core and access](specs/2026-11-01-crm-signals-core-and-access.md) | Baseline implemented; hardening open |
| Document events and realtime routing | [Events and notifications](specs/2026-11-01-crm-signals-events-and-notifications.md) | Baseline implemented; idempotency/config open |
| Daily digest | [Digest](specs/2026-11-01-crm-signals-daily-digest.md) | Baseline implemented; site semantics open |
| D1 | [Sales Compass](specs/2026-11-01-pillar-d1-sales-compass.md) | Implemented; semantic hardening open |
| D2 | [Billing Realization](specs/2026-10-31-pillar-d2-billing-realization.md) | Implemented; target-site reconciliation open |
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
