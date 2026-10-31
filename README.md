# CRM Signals for Frappe & ERPNext

A Frappe app that adds event-driven CRM signals, Desk notifications and a scheduled sales digest. **This is an extension to ERPNext CRM, not a complete CRM implementation.**

## Frappe app packaging

The repository root contains a pyproject.toml with a [project].name of crm_signals, allowing Frappe Pilot to identify the app. The default Crm Signals module and DocType are stored under crm_signals/crm_signals/.

See [FRAPPE_PILOT_IMPORT.md](FRAPPE_PILOT_IMPORT.md) for the import fix and [pyproject.toml](pyproject.toml) for supported framework ranges.

## CRM Signals Desk Console

The native Desk dashboard is available at /app/crm-signals-dashboard and from the CRM Signals workspace. It shows total, unread, high-priority and last-seven-day signal counts, a signal-type breakdown and the 12 most recent signals. Selecting a linked item opens its Lead or Customer. Dashboard queries use permission-aware Frappe list APIs.

The is_read field is currently one shared team-level acknowledgement, not a personal per-recipient read receipt. Per-user inboxes require a separate data model and are not implied by the current unread count.

## S.A.H.D.E.V. Executive Compass

The executive dashboard is available at /app/sahdev-dashboard from the CRM Signals workspace.

- **D1 — Sales Compass:** Leads created in the rolling 30-day window, active Leads, active Opportunities, stage counts, pipeline totals grouped by transaction currency and recent Opportunities.
- **D2 — Billing Realization:** submitted Sales Invoice totals, customer receipts from submitted Receive Payment Entries, separate POS receipt totals, current positive receivables grouped by party-account currency and overdue invoice drill-down.
- **D3 — Service Resolution/SLA:** specified, but not implemented until the installed ticketing application and SLA source/field semantics are verified on the target site.

All dashboard data reads use permission-aware Frappe APIs. Missing permissions or unavailable source fields must be represented as unavailable, not as successful zero values. Unlike currencies are never summed together.

Billing semantics are explicit: Payment Entry receipts are grouped by receiving-account currency and include allocated and advance/unallocated receipts; POS receipts use Sales Invoice paid_amount and stay separate. Open receivables use the party-account currency, which may differ from invoice currency. Target-site reconciliation is required before operational reliance.

## Implemented CRM Signal behavior

- CRM Signal DocType for signal type, priority, Lead/Customer reference, message and read state.
- Authenticated POST endpoint at /api/method/crm_signals.api.ingest_signal.
- Quotation submit signal for the current high-value threshold default.
- Opportunity signal for the current configured-in-code status transition (currently Replied).
- Realtime notifications routed to related document owners and active ToDo assignees; no site-wide fallback.
- Record-level read/write permission hooks for linked-party owners and assignees.
- Scheduled digest for Leads not modified in more than three calendar days and submitted quotations expiring today; enabled System User Sales Managers receive it.

The current quotation threshold of 200,000, Opportunity status and digest stale window are defaults in source, not verified business policy. The threshold and message formatter must use the actual Company currency rather than assuming INR. The digest's Lead condition means "not modified"; it does not prove there was no call, email or meeting.

## Project records

- [Implementation plan](IMPLEMENTATION_PLAN.md) — delivery order, dependencies, milestones, acceptance gates and exit criteria.
- [Progress](docs/PROGRESS.md) — merged work, current CI evidence, blockers and target-site gates.
- [Decision register](docs/DECISIONS.md) — durable product and engineering decisions with rationale.
- [Specifications](specs/README.md) — CRM Signals core, events, digest, D1/D2/D3 and H/A/E/V contracts.
- [S.A.H.D.E.V. roadmap](docs/SAHDEV_VERTICAL_SLICES.md) — vertical-slice status and dependencies.
- [Changelog](CHANGELOG.md) — user-visible and operationally significant changes.
- [Quality gates](docs/QUALITY_GATES.md) and [security scanning](docs/SECURITY_SCANNING.md).

## Compatibility

The source declares intended Frappe/ERPNext v15 and v16 compatibility. GitHub Actions Bench validation has passed on both version lines (v15/Python 3.11 and v16/Python 3.14), with authenticated Playwright E2E in the v16 lane. CI is not a substitute for validation on the intended site's roles, customizations, currency, timezone and financial data.

## Installation

\`\`\`bash
bench get-app https://github.com/MitMike/crm_signals --branch main
bench --site <site-name> install-app crm_signals
bench --site <site-name> migrate
bench build --app crm_signals
bench restart
\`\`\`

## Webhook authentication

Use a dedicated integration user and Frappe API key/secret over HTTPS. The endpoint rejects Guest access. Grant only the create permission required by the integration. Do not use Administrator credentials. Enforce TLS and gateway rate limiting, rotate credentials and never put secrets in source control or logs. See [SECURITY.md](SECURITY.md).

Example:

\`\`\`bash
curl -X POST 'https://<site>/api/method/crm_signals.api.ingest_signal' \\
  -H 'Authorization: token <api_key>:<api_secret>' \\
  -H 'Content-Type: application/x-www-form-urlencoded' \\
  --data-urlencode 'signal_type=Website Visit' \\
  --data-urlencode 'message=Visited product pricing page' \\
  --data-urlencode 'lead=LEAD-00001'
\`\`\`

## Configuration still required

- Confirm Company default currency and configure the high-value quotation threshold in that currency.
- Confirm Opportunity statuses that should generate signals.
- Confirm Lead stale-window meaning and whether Lead modification date is an acceptable digest proxy.
- Confirm site timezone and digest delivery time.
- Verify record-level permissions in Desk/list/report/export/API workflows on both supported versions.
- Confirm installed support/SLA app and source DocTypes before D3 implementation.
- Confirm retention/source-visibility policy before enabling Vault snapshots.
- Complete target-site financial reconciliation, integration credentials, TLS/rate limit and rollback validation.

## Engineering quality and dependency checks

See [docs/QUALITY_GATES.md](docs/QUALITY_GATES.md) for Ruff, ESLint, Oxlint, Prettier, Python tests, Bench compatibility and Playwright E2E. JavaScript dependencies are pinned in package.json and package-lock.json; use npm ci for clean installs. [Dependency Security Audit](docs/SECURITY_SCANNING.md) runs Python pip-audit and npm audit at moderate severity or higher. New behavior starts with a spec and must map acceptance criteria to unit, Bench integration and browser tests.

\`\`\`bash
python -m pip install -e .
python -m compileall -q crm_signals
python -m pytest -q
npm ci
npm run lint:js
npm run format:check
npm audit --audit-level=moderate
\`\`\`
