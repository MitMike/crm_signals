# D1 — Sales Compass

**Status:** Implemented baseline; status-metadata safety fix is in branch `fix/stage1-metric-correctness` and awaiting CI/merge. Target-site workflow/status validation remains.

## Problem and user

Sales Managers and business owners need a quick view of Lead inflow and active Opportunity pipeline, with drill-down to source records and no exposure beyond their Frappe permissions.

## Goals

- Count new Leads over the rolling 30-day window.
- Count active Leads using an explicit terminal-status policy.
- Show all Opportunity count, active Opportunity count and active stage distribution.
- Show active pipeline amount grouped by transaction currency.
- Show the eight most recently created Opportunities with direct Desk links.
- Treat missing permissions or required fields as unavailable, not as zero or an invented metric.

## Sources and calculation contract

### Leads

Source: Lead.

- Created last 30 days: count records with creation >= current site date minus 30 days.
- Active: count Leads whose status is not in the configured terminal-status list. Initial defaults preserve the current code set: Cancelled, Closed, Converted, Do Not Contact, Lost, Obsolete, and values beginning with Lost (case-insensitive).
- The active metric requires a readable Lead DocType and a readable status field. If status is unavailable, the active count is unavailable; do not classify every Lead as active.
- The created count does not depend on status and may remain available if the date field and permission are available.

### Opportunities

Source: Opportunity.

- Total count: all permission-visible Opportunity records; no date filter.
- Active count: records whose status is not terminal under the same normalized terminal-status policy, unless an Opportunity-specific list is configured.
- Stage breakdown: count of active Opportunities grouped by status.
- Pipeline: sum of opportunity_amount for active records, grouped by transaction currency. Never add unlike currencies together.
- Recent list: top eight records ordered by creation descending. Include only fields that exist and the requesting user can read; links resolve to the Opportunity Desk form.
- Active count, stages and active pipeline require a readable status field. Pipeline additionally requires readable opportunity_amount and currency fields. If any semantic requirement is absent, mark the affected metric unavailable rather than treating all records as active or using an unspecified currency total.

## Permissions and access

Use permission-aware frappe.get_list for all aggregates and recent records. Check DocType read permission independently for Lead and Opportunity. The Desk Page is limited to Sales User, Sales Manager and System Manager roles, while the API still enforces authentication and underlying DocType permissions. A route restriction is not a replacement for server-side authorization.

## UI contract

Route: /app/sahdev-dashboard.

The Executive Compass presents Lead creation and active Lead metrics; Opportunity total/active counts; active stage distribution; active pipeline per currency; and recent Opportunities. Each monetary group displays its currency. A source-specific unavailable state must identify the missing permission or configuration without leaking record names. Empty successful results are displayed as zero/empty state, distinct from unavailable.

## Acceptance criteria

| ID | Requirement | Validation |
|---|---|---|
| D1-AC1 | 30-day Lead inflow uses inclusive date boundary | Unit test for boundary dates |
| D1-AC2 | Active Lead count excludes the configured terminal statuses | Unit tests for each default and mixed-case status |
| D1-AC3 | Active Lead is unavailable when status semantics cannot be resolved | Regression test; current fallback-to-all behavior must be removed |
| D1-AC4 | Opportunity total includes all visible statuses; active count excludes terminal statuses | Unit test with open, won, lost, closed and custom statuses |
| D1-AC5 | Stage distribution includes active Opportunities only | Unit test |
| D1-AC6 | Pipeline amount is grouped by transaction currency and excludes terminal stages | Multi-currency unit test |
| D1-AC7 | Missing status, amount or currency fields mark dependent measures unavailable | Metadata/permission tests |
| D1-AC8 | Sales User sees only records admitted by Frappe permissions and role access | Bench integration test |
| D1-AC9 | Recent Opportunity links open the correct source form | Playwright E2E |
| D1-AC10 | Empty and unavailable states render differently | Playwright E2E |

## Existing implementation and tests

Implementation is in crm_signals.api.get_sales_compass_data and crm_signals/crm_signals/page/sahdev_dashboard/. The existing Playwright suite is e2e/sahdev-dashboard.spec.ts and includes role, permission, currency and empty-state flows. The D2 spec also references test_sales_compass_returns_permission_filtered_lead_and_opportunity_metrics; keep the source-level test mapping aligned with the actual test module when making changes.

## Known correctness hardening

The baseline code treated every Lead/Opportunity as active when the corresponding status field was absent. The Stage 1 correction now marks Lead active count, Opportunity active count, stage distribution and active pipeline unavailable when their required status metadata is missing; total/created counts and recent Opportunity rows remain available where their independent fields/permissions permit. Confirm the terminal-status list with the target site and allow explicit configuration for custom workflows.


### Multi-company quotation thresholds

The Settings singleton supports optional per-company threshold rows. Each row derives its currency from Company metadata and is evaluated against the Quotation's base total. If a Company has no override, the legacy site-wide threshold is applied only when its currency matches that Company's base currency. No automatic currency conversion is performed. Administrators must validate each Company's threshold before enabling its quotation alerts.
