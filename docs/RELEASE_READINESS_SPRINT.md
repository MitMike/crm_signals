# CRM Signals — Release-readiness completion sprint

**Started:** 2026-11-01  
**Baseline:** `main` at `9c0ecb1013311909041aebb687fef850ea084869`  
**Decision register:** [ADR-046](DECISIONS.md#adr-046--run-release-readiness-as-an-evidence-gated-sprint)  
**Operating rule:** no item is complete without the evidence listed here. CI evidence and target-site evidence are separate.

## Sprint sequence

### 0. Active PR triage — first

- [ ] Repair [PR #26](https://github.com/MitMike/crm_signals/pull/26) before merge.
- [ ] Fix the MariaDB concurrent-enqueue lock-wait timeout in `test_two_workers_enqueue_the_same_source_event_once`; preserve the actual two-transaction race and prove one outbox row, one CRM Signal and one notification dispatch.
- [ ] Fix test fixture creation in `test_two_workers_process_one_outbox_event_once` and `test_worker_filters_future_retries_before_applying_batch_limit` by supplying the deterministic `source_event_key` required by the DocType's field-based autoname, or use the production enqueue helper where appropriate.
- [ ] Run the complete Bench v15 and v16 suites, quality checks, security scanning and Playwright on the final PR head.
- [ ] Keep terminal Failed-row operator replay and realtime notification retry as explicitly separate follow-ups unless implemented and tested in a distinct scope.

**Merge gate:** all required checks pass on the final PR head; review threads resolved; no target-site claims inferred from CI.

### 1. Target-site acceptance kit — source-independent preparation

- [ ] Prepare a site inventory template for Frappe/ERPNext versions, installed apps, Company currencies, timezone, workflows, custom fields and roles.
- [ ] Prepare a role matrix for Sales User, Sales Manager, System Manager and non-sales users across list, direct form, API, report, export and print.
- [ ] Prepare D1/D2 reconciliation worksheets with native ERPNext report names, date ranges, currency grouping and evidence fields.
- [ ] Prepare webhook operational checklist: dedicated least-privilege integration user, TLS, gateway rate limiting, monitoring, secure secret storage and rotation.
- [ ] Prepare scheduler/mail/realtime smoke tests and a target-site deployment record.
- [ ] Prepare backup/restore/rollback evidence checklist using the site's actual Bench/process manager and off-host backup policy.

**Gate:** kit is documented and executable, but no target-site item is closed until performed on the intended site.

### 2. Target-site acceptance — requires intended environment and business owners

- [ ] Run Frappe Pilot import and record installed versions/apps.
- [ ] Confirm Company currency and quotation-threshold policy, including multi-company behavior.
- [ ] Confirm Opportunity statuses, terminal Lead statuses, stale-Lead semantics, timezone, digest time and recipients.
- [ ] Execute permission parity tests for all relevant roles and access paths.
- [ ] Reconcile invoices, Payment Entry receipts, POS receipts and receivables against native reports, grouped by currency.
- [ ] Validate webhook credentials, rate limits, monitoring and rotation.
- [ ] Validate scheduler, mail queue, realtime routing and per-recipient permissions.
- [ ] Execute backup, restore, migration and rollback rehearsal; record exact revisions and outputs.

**Gate:** all P0 evidence recorded and reviewed; exceptions have owner, mitigation and due date.

### 3. D3 Service Resolution/SLA

- [ ] Discover installed support app(s), exact ticket DocType and owning app/version.
- [ ] Map authoritative status, resolution timestamp, SLA record, deadline, pause behavior, business calendar, timezone, permissions and retention.
- [ ] Obtain business-owner approval of cohort definitions and metric semantics.
- [ ] Implement isolated source adapter(s) only for observed apps.
- [ ] Add unit, Bench v15/v16 and Playwright coverage, including unavailable/permission-denied states and privacy-safe aggregate payloads.

**Gate:** D3 acceptance criteria in its specification pass against the mapped source. No assumed Issue/HD Ticket schema.

### 4. H Highlights

- [ ] Complete configurable quote threshold behavior with explicit Company currency semantics and idempotent submission events.
- [ ] Validate escalation recipient permissions and cooldown behavior.
- [ ] Keep proposal-link tracking disabled until privacy/consent, retention and first-party link behavior are approved.
- [ ] If tracking is approved, implement opaque expiring/revocable tokens, stable event IDs, scanner classification and non-invasive diagnostics.
- [ ] Add Bench v15/v16 and Playwright coverage.

### 5. E, V and A roadmap

- [ ] E Explorer only after installed activity integrations and source identities are inventoried.
- [ ] V Vault only after metric definitions, source visibility and retention are approved.
- [ ] A Analysis only after a versioned server-owned metric registry exists; generated SQL/Python remains prohibited.

## Current blockers and known evidence

- `main` is at `9c0ecb1`; it contains the merged PR #23 concurrency hardening and associated documentation.
- PR #26 is open at head `a63b3b60f909ebc0e62d5bfde383aa6224ba36b2`.
- Python, lint/static and Semgrep checks passed on the PR's merge-synced head.
- Frappe v15/v16 Bench checks failed in:
  - `test_two_workers_enqueue_the_same_source_event_once`: MariaDB `1205 Lock wait timeout exceeded` while inserting the competing outbox row.
  - `test_two_workers_process_one_outbox_event_once`: DocType validation reports `Source Event Key is required`.
  - `test_worker_filters_future_retries_before_applying_batch_limit`: same missing source-event key fixture failure.
- PR #26 must remain open until the actual concurrent-enqueue failure is understood and fixed, not merely skipped or weakened.

## Evidence log

| Date | Work | Evidence | Status |
|---|---|---|---|
| 2026-11-01 | Baseline audit | `main` `9c0ecb1`; no open standalone issues; PR #26 is active | Complete |
| 2026-11-01 | PR #26 validation review | Frappe v15/v16 logs inspected; three failing tests recorded above | Blocked |
| 2026-11-01 | Sprint sequencing | ADR-046 and progress/follow-up records updated on sprint docs branch | In progress |
