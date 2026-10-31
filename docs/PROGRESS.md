# Project Progress

**Last reviewed:** 2026-11-01  
**Repository:** [MitMike/crm_signals](https://github.com/MitMike/crm_signals)  
**Main baseline observed:** [fed496f](https://github.com/MitMike/crm_signals/commit/fed496f230f5ca88af25d663bc61fe4d748f5f83)  
**Active delivery branches:** none confirmed for product delivery

This is the operational status record. IMPLEMENTATION_PLAN.md is the delivery roadmap; DECISIONS.md is the durable decision register; specs/ contains the feature contracts.

## Current status

Main includes CRM Signals core, the Signals Console, D1 Sales Compass, D2 Billing Realization, the complete specification catalogue and the D1/D2 metric correctness corrections. PR #17 merged as [fed496f](https://github.com/MitMike/crm_signals/commit/fed496f230f5ca88af25d663bc61fe4d748f5f83).

| Workstream | Status | Evidence / next step |
|---|---|---|
| CRM Signals core | Implemented baseline | Target-site permissions, deployment controls and idempotency hardening remain |
| Signals Console | Implemented baseline | Target-site role and workflow smoke tests remain |
| D1 Sales Compass | Implemented; correctness fix merged | Missing status/amount/currency metadata produces explicit unavailable states; target-site status validation remains |
| D2 Billing Realization | Implemented; return guard merged | Return-sensitive Sales Invoice metrics require `is_return`; target-site financial reconciliation remains |
| D3 Service Resolution/SLA | Specified; implementation gated | Complete target-site support/SLA discovery before selecting source adapter |
| H Highlights | Specified; partial quote event exists | Settings, idempotency, verified proposal events and privacy approval remain |
| E Explorer | Specified; planned | Inventory actual installed integrations and implement source adapters |
| V Vault | Specified; planned | Approve metric registry, source visibility and retention before scheduling |
| A Analysis | Specified; planned | Build approved metric/query registry; no model-generated SQL |
| Dependency/security hardening | Merged | PR #11 merged; all four PR checks passed; post-merge Quality, Security and Bench/E2E passed |
| Full specifications and roadmap | Merged | PR #16 merged; ten feature specifications catalogued |
| Main branch ruleset | Verified active | Ruleset Protect main (ID 26282133) targets refs/heads/main. Full details are recorded below; issue #12 closed after verification |

## Repository hardening — PR #11

[PR #11 — automated dependency security monitoring](https://github.com/MitMike/crm_signals/pull/11) merged as [05ad767](https://github.com/MitMike/crm_signals/commit/05ad767f6b62814cca5b7d0c1e233a2f690baa77). It includes:
- weekly Dependabot for pip, npm and GitHub Actions;
- patched JavaScript tooling: Playwright 1.64.1 and ESLint 10.14.0;
- a direct override to patched minimatch 11.0.1;
- a complete committed npm lockfile v3;
- Python pip-audit and npm audit with moderate-or-higher failures;
- Semgrep SARIF scanning and the existing v15/v16 Bench + Playwright gates;
- security and quality guide updates.

The first committed lockfile transfer was accidentally truncated to 1,000 lines. That was identified from the failed npm ci run and replaced with the complete runner-generated lockfile (50,138 bytes, 105 packages). The complete lockfile is committed on main. The final PR-head checks all passed:

| Workflow | Run | Status at this snapshot |
|---|---|---|
| Quality Checks | [41232087717](https://github.com/MitMike/crm_signals/actions/runs/41232087717) | Passed |
| Bench Integration and E2E | [41232087747](https://github.com/MitMike/crm_signals/actions/runs/41232087747) | Passed (v15 and v16 + Playwright) |
| Security Scanning | [41232087776](https://github.com/MitMike/crm_signals/actions/runs/41232087776) | Passed |
| Dependency Security Audit | [41232087748](https://github.com/MitMike/crm_signals/actions/runs/41232087748) | Passed (npm and Python) |

Post-merge validation on main: Quality Checks [41232593555](https://github.com/MitMike/crm_signals/actions/runs/41232593555) and Security Scanning [41232593543](https://github.com/MitMike/crm_signals/actions/runs/41232593543) passed. The fresh post-merge Bench run [41232593526](https://github.com/MitMike/crm_signals/actions/runs/41232593526) passed both v15 and v16 lanes. The final merged-main validation is green for Quality Checks [41232593555](https://github.com/MitMike/crm_signals/actions/runs/41232593555), Security Scanning [41232593543](https://github.com/MitMike/crm_signals/actions/runs/41232593543) and Bench Integration/E2E [41232593526](https://github.com/MitMike/crm_signals/actions/runs/41232593526). Dependency Security Audit passed on PR #11 [41232087748](https://github.com/MitMike/crm_signals/actions/runs/41232087748).

## Specifications and plan

PR #16 merged as [b4ee3cf](https://github.com/MitMike/crm_signals/commit/b4ee3cfacf0b3aeee31789af6732d400fb455f95). The ten feature specifications are present in `specs/`; see [specs/README.md](../specs/README.md). The delivery roadmap is `IMPLEMENTATION_PLAN.md`, durable decisions are in `DECISIONS.md`, and this file is the operational status source.

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

Verified complete: active ruleset Protect main (ID 26282133), PR-only updates, eight strict required contexts, review-thread resolution, blocked deletion/force-push, no bypass actors. Dependency Security Audit remains active but is not one of the eight required contexts. See the governance record below.



#### Repository governance — verified 2026-11-01

GitHub API confirms branch \`main\` is protected by active repository ruleset [Protect main](https://github.com/MitMike/crm_signals/rules/26282133), ID \`26282133\`, targeting only \`refs/heads/main\`.

- Pull requests required; direct updates to main are disallowed by the PR rule. No bypass actors are configured.
- Required status checks use strict/up-to-date enforcement:
  - Lint and static checks
  - Python unit tests (3.10), (3.11), (3.12), (3.14)
  - Semgrep static security analysis
  - bench-validation (version-15, 3.11, false)
  - bench-validation (version-16, 3.14, true)
- Review threads must be resolved. Required approving review count is 0, matching the single-maintainer repository; code-owner and last-push approval are not required.
- Deletion and non-fast-forward updates (force pushes) are blocked.
- Allowed merge methods: merge, squash and rebase.
- No bypass actors; current user cannot bypass. Emergency recovery therefore requires an authorized administrator to edit the ruleset temporarily, with the change documented and reverted.

Dependency Security Audit is active and passing on relevant PRs, weekly and manually, but is not among the eight required status contexts in this ruleset.

[Issue #12](https://github.com/MitMike/crm_signals/issues/12) was closed after this verification.


## Target-site and operational acceptance

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


## Stage 1 metric correctness — merged

PR #17 merged into main as [fed496f](https://github.com/MitMike/crm_signals/commit/fed496f230f5ca88af25d663bc61fe4d748f5f83).

- D1 active Lead/Opportunity counts, stage distribution and active pipeline become unavailable when required metadata is missing.
- D1 pipeline additionally requires amount and currency metadata; currencies remain separate.
- D2 invoiced, POS receipt, outstanding and overdue Sales Invoice measures require `is_return`; no unsafe aggregate runs without the return filter.
- Payment Entry customer receipts remain independent of Sales Invoice return metadata.
- Regression tests cover missing Lead status, Opportunity status and Sales Invoice return metadata.

Final PR-head validation on commit [efec6cd](https://github.com/MitMike/crm_signals/commit/efec6cdb34aea2b280d4f2c2e10ad31c7d774b8c):
- [Quality Checks #452](https://github.com/MitMike/crm_signals/actions/runs/41234960564) — passed.
- [Security Scanning #88](https://github.com/MitMike/crm_signals/actions/runs/41234960558) — passed.
- [Bench Integration and E2E #270](https://github.com/MitMike/crm_signals/actions/runs/41234960576) — passed, including v15 and v16 validation.

These results establish CI acceptance for the merged change, not acceptance on a customer site.

## Update protocol

Update this file when code is merged, validation changes, a blocker is found or a target-site gate is completed. Record the commit SHA and CI evidence. Never mark work complete based only on source code existing or mocked unit tests passing.

For every feature delivery:
1. Update the spec before implementation.
2. Define source fields, metric semantics, permission rules, unavailable states and edge cases.
3. Map acceptance criteria to unit, Bench integration and browser E2E tests as applicable.
4. Record consequential choices in DECISIONS.md.
5. Update CHANGELOG.md for user-visible or operationally significant changes.
6. Reconcile this status document after merge and validation.
