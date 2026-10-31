# Project Progress

**Last reviewed:** 2026-11-01  
**Repository:** [MitMike/crm_signals](https://github.com/MitMike/crm_signals)  
**Main baseline observed:** [b8aa7cc](https://github.com/MitMike/crm_signals/commit/b8aa7cc97a0ae2b6d5eef2dd9a074d3bf7dd27f7)  
**Active delivery branches:** automation/dependency-security-scans (PR #11), docs/full-specifications-and-roadmap (documentation/specification work)

This is the operational status record. IMPLEMENTATION_PLAN.md is the delivery roadmap; DECISIONS.md is the durable decision register; specs/ contains the feature contracts.

## Current status

The mainline baseline contains CRM Signals core, the Signals Console, S.A.H.D.E.V. D1 Sales Compass and D2 Billing Realization. The latest repository-hardening and documentation work is being delivered through pull requests; it is not described as merged until GitHub reports the merge.

| Workstream | Status | Evidence / next step |
|---|---|---|
| CRM Signals core | Implemented baseline | Target-site permissions, deployment controls and idempotency hardening remain |
| Signals Console | Implemented baseline | Target-site role and workflow smoke tests remain |
| D1 Sales Compass | Implemented baseline | Fix missing-status fallback and validate target workflow/status meanings |
| D2 Billing Realization | Implemented baseline | Require return metadata and reconcile values against native reports |
| D3 Service Resolution/SLA | Specified; implementation gated | Complete target-site support/SLA discovery before selecting source adapter |
| H Highlights | Specified; partial quote event exists | Settings, idempotency, verified proposal events and privacy approval remain |
| E Explorer | Specified; planned | Inventory actual installed integrations and implement source adapters |
| V Vault | Specified; planned | Approve metric registry, source visibility and retention before scheduling |
| A Analysis | Specified; planned | Build approved metric/query registry; no model-generated SQL |
| Dependency/security hardening | PR #11 open | Complete all four CI workflows on the latest head, then merge |
| Full specifications and roadmap | Documentation branch prepared | Open PR after the security PR is merged, validate, then merge |
| Main branch ruleset | Not verified by current GitHub connection | Prior 2026-10-31 check reported protection disabled; current read endpoint is denied to the connected integration |

## Repository hardening — PR #11

[PR #11 — automated dependency security monitoring](https://github.com/MitMike/crm_signals/pull/11) includes:
- weekly Dependabot for pip, npm and GitHub Actions;
- patched JavaScript tooling: Playwright 1.64.1 and ESLint 10.14.0;
- a direct override to patched minimatch 11.0.1;
- a complete committed npm lockfile v3;
- Python pip-audit and npm audit with moderate-or-higher failures;
- Semgrep SARIF scanning and the existing v15/v16 Bench + Playwright gates;
- security and quality guide updates.

The first committed lockfile transfer was accidentally truncated to 1,000 lines. That was identified from the failed npm ci run and replaced with the complete runner-generated lockfile (50,138 bytes, 105 packages). The current branch head has a valid parsed lockfile. Latest workflow runs are being checked:

| Workflow | Run | Status at this snapshot |
|---|---|---|
| Quality Checks | [41232087717](https://github.com/MitMike/crm_signals/actions/runs/41232087717) | Queued |
| Bench Integration and E2E | [41232087747](https://github.com/MitMike/crm_signals/actions/runs/41232087747) | Pending |
| Security Scanning | [41232087776](https://github.com/MitMike/crm_signals/actions/runs/41232087776) | Pending |
| Dependency Security Audit | [41232087748](https://github.com/MitMike/crm_signals/actions/runs/41232087748) | In progress |

Do not merge PR #11 until all four workflows pass on its latest head.

## Specifications and plan

The documentation branch adds full feature specs for:
- CRM Signals core, ingestion, permissions and Console;
- Quotation/Opportunity event routing and realtime notifications;
- daily sales digest;
- D1 Sales Compass;
- D3 Service Resolution/SLA discovery and adapter contract;
- H Highlights;
- A Analysis;
- E Explorer;
- V Vault.

The existing D2 Billing Realization spec remains the D2 contract. The new specifications catalogue links all ten specs. IMPLEMENTATION_PLAN.md now sequences repository security, core/release hardening, D3, H, E, V and A with dependencies, acceptance criteria and exit gates. These documentation changes are on the separate documentation branch and are not yet on main.

## Delivered on the observed main baseline

- Frappe app packaging metadata and the documented Pilot discovery/module layout.
- CRM Signal DocType, authenticated signal ingestion endpoint, Quotation and Opportunity hooks, recipient-scoped realtime notifications, linked-party permissions and scheduled digest.
- Native CRM Signals Desk Console.
- D1 Sales Compass: Lead and Opportunity metrics, stage distribution, currency-grouped pipeline and recent Opportunities.
- D2 Billing Realization: submitted invoice totals, customer Receive Payment Entry receipts, separate POS receipts, current positive receivables and overdue invoice drill-down.
- Quality workflows: Ruff, ESLint, Oxlint, Prettier checks, Python unit tests/compile, pre-commit, Frappe Bench compatibility and Playwright E2E.
- Security workflows: Semgrep scanning and Dependabot configuration.

These are code/CI baselines. They do not prove acceptance on a particular customer or production site.

## Outstanding gates

### Repository governance

- [ ] Verify a main ruleset/branch protection exists.
- [ ] Require Quality Checks, Bench Integration and E2E, Security Scanning and Dependency Security Audit.
- [ ] Disable ordinary direct pushes to main while retaining an approved emergency path.

The previously observed state on 2026-10-31 was unprotected. The current linked GitHub integration cannot read the protection endpoint (403), so the present state is explicitly unverified rather than assumed unchanged. An administrator must verify/configure it in repository settings.

### Target-site and operational acceptance

- [ ] Run Frappe Pilot import on the intended site.
- [ ] Record installed Frappe/ERPNext versions, apps, Company default currency, site timezone, workflows, DocType metadata and custom fields.
- [ ] Validate Sales User, Sales Manager, System Manager and non-sales role behavior in list, direct form, API, report and export paths.
- [ ] Reconcile D2 invoice, payment receipt and receivable groups against native ERPNext reports.
- [ ] Confirm the configured high-value quotation threshold and currency; the current source constant is a default only and its message formatting must not assume INR.
- [ ] Confirm Opportunity signal trigger statuses and Lead digest interpretation.
- [ ] Configure dedicated integration user, credential rotation, TLS, rate limiting and secret storage.
- [ ] Complete runbook, backup, rollback, migration and release checks.

### Product delivery

- [ ] Complete Stage 1 CRM core hardening: idempotency, validated settings, permission parity, event failure isolation, D1 missing-status behavior, D2 required return metadata and digest currency/timezone behavior.
- [ ] Complete D3 support/SLA discovery against the target site before implementation.
- [ ] Deliver H only after idempotency, recipient access and privacy/consent controls are accepted.
- [ ] Deliver E only for integrations verified as installed/configured.
- [ ] Keep Vault scheduling disabled until metric provenance, source visibility and retention are approved.
- [ ] Deliver Analysis only against an approved metric registry and server-owned permission-aware queries.

## Update protocol

Update this file when code is merged, validation changes, a blocker is found or a target-site gate is completed. Record the commit SHA and CI evidence. Never mark work complete based only on source code existing or mocked unit tests passing.

For every feature delivery:
1. Update the spec before implementation.
2. Define source fields, metric semantics, permission rules, unavailable states and edge cases.
3. Map acceptance criteria to unit, Bench integration and browser E2E tests as applicable.
4. Record consequential choices in DECISIONS.md.
5. Update CHANGELOG.md for user-visible or operationally significant changes.
6. Reconcile this status document after merge and validation.
