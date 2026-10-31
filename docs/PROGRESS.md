# Project Progress

**Last reviewed:** 2026-10-31  
**Repository:** [MitMike/crm_signals](https://github.com/MitMike/crm_signals)  
**Branch:** `main`  
**Baseline commit:** [`b55cce6`](https://github.com/MitMike/crm_signals/commit/b55cce6469bbe7c1603c49175651eafa7259d879)

This file records the delivery state, validation evidence, open risks and next actions. It is the operational status document; product scope remains in `IMPLEMENTATION_PLAN.md` and `docs/SAHDEV_VERTICAL_SLICES.md`.

## Current status

The repository contains the CRM Signals Frappe extension, its Signals Console, the S.A.H.D.E.V. executive dashboard through Pillar D2 (Billing Realization), feature specifications, automated quality checks, Bench integration/E2E workflows and security scanning.

The latest `main` commit checked for this update is `b55cce6`. Its three primary GitHub Actions workflows all completed successfully:

| Workflow | Result | Run |
|---|---|---|
| Quality Checks | Success | [Run 41227467943](https://github.com/MitMike/crm_signals/actions/runs/41227467943) |
| Bench Integration and E2E | Success | [Run 41227467937](https://github.com/MitMike/crm_signals/actions/runs/41227467937) |
| Security Scanning | Success | [Run 41227467867](https://github.com/MitMike/crm_signals/actions/runs/41227467867) |

The Bench workflow reported successful Frappe/ERPNext v15 validation on Python 3.11 and v16 validation on Python 3.14. The v16 lane includes the authenticated Playwright dashboard E2E run. These are CI results for the recorded commit; they do not prove that the app has been installed and accepted on a particular customer or production site.

## Delivered and present on main

- **Frappe app packaging:** root project metadata and module/DocType placement now follow the Pilot discovery and Frappe module layout contract. The repository audit documents the fix; running the actual Pilot import remains a separate verification.
- **CRM Signals core:** CRM Signal DocType, authenticated ingest endpoint, document event hooks, scoped realtime notifications, linked-party permissions and scheduled digest are documented in the README and implementation plan.
- **Signals Console:** native Desk page with signal KPIs, type breakdown and recent linked records.
- **S.A.H.D.E.V. D1 — Sales Compass:** Lead and Opportunity metrics, stage breakdown, currency-grouped pipeline and recent Opportunities.
- **S.A.H.D.E.V. D2 — Billing Realization:** invoiced totals, Payment Entry receipts, separate POS receipts, open receivables and overdue invoices, with explicit currency and permission semantics.
- **Engineering checks:** Ruff, ESLint, Oxlint, Prettier checks, Python tests/compile checks, pre-commit hooks, Frappe Bench validation and Playwright E2E are configured.
- **Security checks:** Semgrep workflow, SARIF upload and Dependabot update checks are configured.
- **Project documentation:** implementation plan, vertical-slice roadmap, D2 specification, quality-gate guide, security-scanning guide and packaging audit are present.

## Outstanding actions

### Repository protection

- [ ] Enable branch protection or a ruleset for `main`.
- [ ] Require Quality Checks, Bench Integration and E2E, and Security Scanning before merge.
- [ ] Disable direct pushes to the protected branch, while retaining an appropriate emergency/break-glass process.

**Observed state on 2026-10-31:** GitHub reported `main` as unprotected, with required status checks disabled and no required contexts configured. The workflows passing does not itself enforce merge policy.

### Target-site and operational validation

- [ ] Run the Frappe Pilot import flow against this repository; the resolver contract is fixed, but the audit does not claim that Pilot itself was run.
- [ ] Install/migrate on the intended target site and verify site-specific Frappe/ERPNext customizations.
- [ ] Validate Sales User, Sales Manager and non-sales access in the actual target site's role configuration.
- [ ] Reconcile billing totals against the target site's Sales Invoice and Payment Entry reports before operational use.
- [ ] Confirm the quotation threshold, Opportunity trigger statuses, Lead inactivity semantics and company-currency display policy documented in the README.
- [ ] Verify webhook credentials, integration-user permissions, TLS and gateway rate limiting in the deployment environment.
- [ ] Complete production runbook, rollback and release checks.

### Product roadmap

- [ ] **D3 — Service resolution/SLA:** confirm the installed ticketing DocTypes, SLA configuration and resolution timestamp semantics before defining metrics.
- [ ] **H — Highlights:** configurable high-value quotation and proposal-link-open alerts with tested recipient routing and duplicate handling.
- [ ] **A — Analysis:** approved natural-language sales questions backed by a metric/field registry and permission-aware query definitions; no model-generated SQL.
- [ ] **E — Explorer:** permission-safe customer interaction timeline across only the integrations actually available.
- [ ] **V — Vault:** versioned historical metric snapshots with retention, correction and audit rules.

See [the vertical-slice roadmap](SAHDEV_VERTICAL_SLICES.md) and [the implementation plan](../IMPLEMENTATION_PLAN.md) for scope and acceptance details.

## Update protocol

Update this file when a meaningful feature is merged, a validation gate changes, a rollout/production check is completed, or a material blocker is discovered. Record the commit SHA and link the relevant CI run or issue. Do not mark work complete based only on code existing or mocked unit tests passing.

For every new feature:
1. Add or update a specification in `specs/` before implementation.
2. Define measurable behavior, source-of-truth fields, permission behavior, unavailable states and acceptance criteria.
3. Link acceptance criteria to unit, Bench integration and browser E2E tests as applicable.
4. Update this progress file when the work is merged and its validation evidence is known.
5. Add consequential architecture, product, data, security or compatibility choices to [DECISIONS.md](DECISIONS.md).
6. Add user-visible or operational changes to [CHANGELOG.md](../CHANGELOG.md).
