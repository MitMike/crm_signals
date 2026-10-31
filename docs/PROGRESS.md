# Project Progress

**Last reviewed:** 2026-11-01  
**Repository:** [MitMike/crm_signals](https://github.com/MitMike/crm_signals)  
**Main baseline observed:** [05ad767](https://github.com/MitMike/crm_signals/commit/05ad767f6b62814cca5b7d0c1e233a2f690baa77)  
**Active delivery branches:** fix/stage1-metric-correctness (PR #17 — D1/D2 metric correctness)

This is the operational status record. IMPLEMENTATION_PLAN.md is the delivery roadmap; DECISIONS.md is the durable decision register; specs/ contains the feature contracts.

## Current status

The mainline baseline contains CRM Signals core, the Signals Console, S.A.H.D.E.V. D1 Sales Compass and D2 Billing Realization. The latest repository-hardening and documentation work is being delivered through pull requests; it is not described as merged until GitHub reports the merge.

| Workstream | Status | Evidence / next step |
|---|---|---|
| CRM Signals core | Implemented baseline | Target-site permissions, deployment controls and idempotency hardening remain |
| Signals Console | Implemented baseline | Target-site role and workflow smoke tests remain |
| D1 Sales Compass | Implemented baseline; correctness fix in review | Active count, stages and pipeline now become unavailable when status metadata is missing; target-site status validation remains |
| D2 Billing Realization | Implemented baseline; return guard in review | Return-sensitive invoice metrics now require `is_return`; target-site financial reconciliation remains |
| D3 Service Resolution/SLA | Specified; implementation gated | Complete target-site support/SLA discovery before selecting source adapter |
| H Highlights | Specified; partial quote event exists | Settings, idempotency, verified proposal events and privacy approval remain |
| E Explorer | Specified; planned | Inventory actual installed integrations and implement source adapters |
| V Vault | Specified; planned | Approve metric registry, source visibility and retention before scheduling |
| A Analysis | Specified; planned | Build approved metric/query registry; no model-generated SQL |
| Dependency/security hardening | Merged | PR #11 merged as 05ad767; all four PR checks passed; post-merge Bench verification in progress |
| Full specifications and roadmap | Merged | PR #16 merged; all CI checks passed on the final head |
| Main branch ruleset | <badge>Verified active</badge> | Ruleset Protect main (ID 26282133) targets refs/heads/main. Full details are recorded below; issue #12 closed after verification |

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

The full spec catalogue and delivery roadmap were merged to main in PR #16 (merge commit 7a8ee4354a9d62ffa706c5b77be948186e6a7306 is the PR head; merge commit b4ee3cf).

The documentation branch docs/complete-specifications-roadmap adds full feature specs for:
- CRM Signals core, ingestion, permissions and Console;
- Quotation/Opportunity event routing and realtime notifications;
- daily sales digest;
- D1 Sales Compass;
- D3 Service Resolution/SLA discovery and adapter contract;
- H Highlights;
- A Analysis;
- E Explorer;
- V Vault.

The existing D2 Billing Realization spec remains the D2 contract. The new specifications catalogue links all ten specs. IMPLEMENTATION_PLAN.md now sequences repository security, core/release hardening, D3, H, E, V and A with dependencies, acceptance criteria and exit gates. These documentation changes are on docs/complete-specifications-roadmap and are not yet on main.

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


## Stage 1 metric correctness — active branch

Branch: \`fix/stage1-metric-correctness\` (based on the documentation/specification branch so its contracts and decisions are carried forward).

Changes in review:
- D1 Lead active count is unavailable when Lead.status metadata is missing; Lead creation count remains available.
- D1 Opportunity active count, stage distribution and active pipeline are unavailable when Opportunity.status is missing. Total count and recent Opportunities remain available.
- D1 active pipeline additionally requires amount and currency metadata; unlike currencies remain separate.
- D2 invoiced, POS receipt, current outstanding and overdue Sales Invoice metrics do not run without is_return. Each remains unavailable rather than dropping the safety filter.
- Payment Entry customer receipts continue independently of Sales Invoice return metadata.
- The Desk page explains missing metadata rather than rendering false zero/all-active values.
- Regression tests cover missing Lead status, missing Opportunity status and missing Sales Invoice is_return.

Latest push validation is running on the current code branch:
- Quality Checks: [41233382583](https://github.com/MitMike/crm_signals/actions/runs/41233382583) — Python 3.10/3.11/3.12/3.14 passed; lint/static job was completing.
- Security Scanning: [41233382608](https://github.com/MitMike/crm_signals/actions/runs/41233382608) — queued at this snapshot.
- Bench Integration and E2E: [41233382641](https://github.com/MitMike/crm_signals/actions/runs/41233382641) — v15/v16 in progress at this snapshot.

Do not mark Stage 1 code complete until all three workflows pass and the pull request is merged. Target-site semantics remain separate acceptance gates.

## Update protocol

Update this file when code is merged, validation changes, a blocker is found or a target-site gate is completed. Record the commit SHA and CI evidence. Never mark work complete based only on source code existing or mocked unit tests passing.

For every feature delivery:
1. Update the spec before implementation.
2. Define source fields, metric semantics, permission rules, unavailable states and edge cases.
3. Map acceptance criteria to unit, Bench integration and browser E2E tests as applicable.
4. Record consequential choices in DECISIONS.md.
5. Update CHANGELOG.md for user-visible or operationally significant changes.
6. Reconcile this status document after merge and validation.
