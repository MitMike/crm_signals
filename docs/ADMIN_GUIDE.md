# CRM Signals — Administrator and user guide

## Purpose and scope

CRM Signals is an extension to ERPNext CRM. It creates contextual signal records, sends recipient-scoped Desk notifications, and provides a daily sales digest. It does not replace ERPNext Leads, Opportunities, Quotations, Communications or a support application.

For release, backup, migration, smoke-test and rollback procedures, follow the [Deployment and rollback runbook](DEPLOYMENT_RUNBOOK.md).

## Target version

The deployment owner confirmed **Frappe v16.5** as the target baseline. PR #48 is validating the exact reference stack Frappe v16.5.0 + ERPNext v16.5.0 + Helpdesk v1.30.2 (with Telephony). The first attempt with Helpdesk v1.31.1 failed during its post-install Notification Type setup because that controller is absent from the exact Frappe v16.5.0 tag; ADR-057 records the evidence and the narrower compatible reference choice. Do not install or upgrade Helpdesk based on this CI lane alone. Before installation, capture the exact patch/build from `bench version`, plus ERPNext and Helpdesk versions from `bench --site <site-name> list-apps`. The repository retains Frappe/ERPNext v15 and moving v16 CI coverage. PR #48's v1.30.2 rerun is pending; CI does not prove the live site's permissions or configuration.

## Installation and upgrade

Install from the app repository using the site's normal Bench/Pilot process:

```bash
bench get-app https://github.com/MitMike/crm_signals --branch main
bench --site <site-name> install-app crm_signals
bench --site <site-name> migrate
bench build --app crm_signals
bench restart
```

For an existing installation, deploy the approved app revision and run `bench --site <site-name> migrate`, then build assets and restart workers. Take a database and files backup first. Follow your site's normal maintenance window and rollback process.

For the pilot, install only after the required pull requests are merged and CI is green. Record the exact CRM Signals revision with `git -C apps/crm_signals rev-parse HEAD` and attach it to the acceptance record. Do not leave a production deployment tracking a moving `main` branch; use an approved release tag or pinned commit. After installation, capture `bench version` and `bench --site <site-name> list-apps` again so the installed state is evidenced.

## Configure CRM Signals

1. Sign in as a System Manager.
2. Open **CRM Signals Settings** from the Desk search/awesome bar.
3. Select a starter preset: **Balanced**, **Sales Focused** or **Executive**.
4. Review every value. Presets are starting points, not recommended policy for every company.
5. Configure a threshold for each enabled Company: add a Company-specific row where needed, or use the legacy site-wide threshold only when its currency exactly matches that Company's base currency.
6. Replace Opportunity trigger statuses with exact values used by the site's workflow.
7. Set the Lead not-modified window and site-local digest time.
8. Add optional additional recipients using enabled System User email addresses, one per line.
9. Save and verify the resulting settings before enabling the feature.

The master switch and external ingestion are off by default. Complete the site preflight and save the reviewed settings before explicitly enabling CRM Signals. External ingestion remains separately disabled until an administrator turns it on for a provisioned integration user.

### Preset starting values

| Setting | Balanced | Sales Focused | Executive |
|---|---:|---:|---:|
| Quotation threshold | 200,000 | 100,000 | 500,000 |
| Opportunity trigger status | Replied | Replied | Replied |
| Lead not-modified window | 3 days | 2 days | 5 days |
| Digest time | 08:30 | 08:00 | 08:30 |

Each Company-specific row requires an explicitly entered approved threshold; it does not inherit the site-wide numeric default. The amount is interpreted in that Company's base currency and the row's currency is derived from Company metadata. If a Company has no override, the legacy site-wide threshold is used only when its currency exactly matches that Company's base currency. There is no implicit FX conversion. If a Company's default currency changes, its old row is stale: alerts are suppressed and Settings cannot be saved until an administrator removes/re-adds the row and enters a newly approved amount. The starter values do not imply INR or any other currency.

Selecting a preset applies its starting values. You can edit any field afterwards; the preset indicator changes to **Custom**. Selecting another preset again replaces the preset-controlled fields.

## What the settings mean

- **Enable CRM Signals:** master switch for event-generated signals.
- **Enable authenticated external ingestion:** enables the POST endpoint for approved integrations.
- **High-value Quotation threshold:** compares a submitted Quotation's base total with the matching Company's base-currency threshold. A Company-specific row takes precedence; the legacy threshold is a fallback only for an exact currency match. The message displays the Quotation's own transaction currency.
- **Opportunity trigger statuses:** exact status names that generate an event when an Opportunity transitions into one of them.
- **Lead not-modified window:** reports Leads whose modified timestamp is older than the configured number of days. It does not prove there was no call, email or meeting.
- **Digest time:** evaluated against the timezone in System Settings. The scheduler checks each minute; delivery can be delayed by worker/scheduler load.
- **Digest quotation list:** at most 100 Quotations are shown. If more are due, the digest displays `100+` and a notice to review the full list in ERPNext.
- **Additional digest recipients:** additional email addresses are resolved to enabled System Users. Arbitrary external email addresses, Guest users and disabled users are not accepted.

## Using the Signals Console

Open **CRM Signals** workspace, then select **CRM Signals Dashboard** (route `/app/crm-signals-dashboard`). The console displays visible signal totals, shared unread state, high-priority signals, recent signal types and the latest records. A linked Lead or Customer opens through the normal Desk permission checks.

The `is_read` flag is a shared team acknowledgement in this release, not an individual read receipt or private inbox.

Realtime notifications are best-effort. Frappe queues the Redis publish after the database commit and does not provide a client receipt; a queued event is not proof that a user saw it. This release does not automatically retry missed realtime events. Use the CRM Signals console and configured digest as the durable places to review signals.

## S.A.H.D.E.V. dashboards

Open **S.A.H.D.E.V. Executive Compass** (route `/app/sahdev-dashboard`). D1 shows Lead and Opportunity indicators. D2 shows invoice, customer receipt, POS receipt, receivable and overdue measures. Monetary values remain grouped by their source currency. Missing schema or permissions must show as unavailable rather than zero.

D3 Service Resolution/SLA is implemented for the standard Frappe Helpdesk schema. It reads aggregate-only metrics from `HD Ticket` and checks `HD Service Level Agreement` read access. It requires ticket DocType read permission and field-level read permission for the fields used by each measure: `status_category`, `resolution_date`, `resolution_time`, `sla` and `agreement_status`. Inspect the installed Helpdesk version's actual field permlevels and current user's permitted fields; do not hardcode a permlevel map or grant access automatically. A measure whose fields are not readable is shown as unavailable, not zero. The active Helpdesk SLA policy's working hours, holiday list and timezone remain authoritative; Monday–Saturday is the agreed initial working-week assumption to verify against the site.

For the Helpdesk v1.30.2 reference schema used with exact Frappe v16.5.0, the D3 fields listed above are all at permlevel 0. HD Ticket read is granted to System Manager, Agent, Agent Manager, HD Customer and HD Customer Manager; HD Service Level Agreement read is limited to System Manager and Agent Manager. ERPNext Sales User/Manager are not default Helpdesk readers. Do not assign Agent/Agent Manager just for dashboard visibility because they also grant ticket mutation privileges. If Sales needs D3, create a dedicated read-only role with only the required HD Ticket and, if approved, SLA read permissions. If the pilot uses another Helpdesk release, inspect its actual field permlevels and DocType role permissions before applying a policy.

## Pilot validation checklist

Run these tests on staging with synthetic records before enabling the app on production:

1. **Settings:** save a reviewed preset, confirm the master and external-ingestion switches remain off until explicitly enabled, and verify the saved values after reload.
2. **Quotation thresholds:** create test Quotations above and below the configured threshold for each enabled Company. Include two Companies with different base currencies. Verify the matching Company override is used, each new row requires an explicit amount, and a currency mismatch without an override creates no signal. In disposable staging, change a Company's default currency and confirm the stale row blocks Settings save until it is removed/re-added with a newly approved amount. Do not expect FX conversion.
3. **Opportunity signals:** move a test Opportunity into one configured trigger status and confirm one signal. Move it between unconfigured statuses and confirm no signal. Repeat a transition/retry with the same source event and confirm no duplicate.
4. **D1/D2 dashboard:** verify Lead/Opportunity counts against the site's workflow values. Reconcile invoice totals, Payment Entry receipts, separate POS receipts and open receivables against native ERPNext reports by Company and currency. Never add unlike currencies.
5. **Permissions:** test Sales User, Sales Manager, System Manager and a non-sales user in list, direct form, dashboard/API, report, export and print. A notification is not permission to read a record.
6. **Digest:** verify site timezone, scheduled time, recipient list, per-recipient content and duplicate-run behavior. Check the scheduler, workers and mail queue.
7. **D3 Helpdesk:** use the [Support & SLA setup guide](CRM_SIGNALS_SUPPORT_CONFIGURATION_GUIDE.html). Test Open, Paused, Resolved, no-SLA, Fulfilled and Failed fixtures; verify the SLA denominator excludes due/paused states and that field-level permission gaps display as unavailable.
8. **External ingestion:** use a dedicated integration System User over HTTPS, test authentication failure, rate limiting and duplicate `source_event_id`, and prove credential rotation rejects the old secret.
9. **Operations:** rehearse migrate, scheduler, mail, realtime, backup, restore and rollback using the [Target-Site Acceptance Kit](TARGET_SITE_ACCEPTANCE.md) and [Deployment runbook](DEPLOYMENT_RUNBOOK.md).

Record exact app versions, the tested commit, test user roles, date/timezone, expected and observed values, and evidence links. Do not copy customer or ticket content into the evidence record. CI success is not pilot acceptance.

## External signal ingestion

Use the authenticated POST method:

`/api/method/crm_signals.api.ingest_signal`

Use a dedicated Frappe integration user with only the required CRM Signal create permission. Send API key/secret over HTTPS. Configure TLS, gateway rate limiting, secret rotation and secure secret storage outside this app.

Example:

```bash
curl -X POST 'https://<site>/api/method/crm_signals.api.ingest_signal' \
  -H 'Authorization: token <api_key>:<api_secret>' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'signal_type=Website Visit' \
  --data-urlencode 'priority=Medium' \
  --data-urlencode 'message=Visited product pricing page' \
  --data-urlencode 'lead=LEAD-00001' \
  --data-urlencode 'source_event_id=web-visit-evt-123'
```

A stable `source_event_id` is strongly recommended. When `source_doctype` and `source_name` are omitted, the server uses `API Integration` plus the authenticated integration user as the source namespace. When callers supply both fields, that pair becomes the namespace and must be stable and unique across integrations. Reuse the same integration account, source namespace and event ID for retries. Requests without an event ID retain legacy at-least-once behavior and can create duplicates on retries.

## Troubleshooting

- **No Quotation alert:** verify the master/Quotation switches, Company currency, Quotation company, base total and configured threshold.
- **No Opportunity alert:** verify the switch and exact status spelling; only transitions into configured statuses generate signals.
- **No digest:** verify scheduler and workers, site timezone, enabled System User Sales Managers, additional recipients and the last queued date.
- **No realtime notification:** verify the linked Lead/Customer owner and active ToDo assignees, and confirm each recipient can read the linked party, CRM Signal and originating source DocType (for example, Quotation or Opportunity). There is intentionally no site-wide broadcast; realtime publication is best-effort, not a delivery receipt.
- **Signal not visible:** check CRM Signal role permissions and linked-party ownership/assignment. A notification is not an authorization grant.
- **Duplicate external event:** send a stable source event ID and use the same integration user for retries.

## Signal outbox and failed events

Quotation and Opportunity events are recorded in the CRM Signal Outbox as part of the source document transaction. If CRM Signal creation fails after that record is saved, the app retries automatically from the minute scheduler. Retries use bounded exponential backoff: 1, 2, 4, 8, 16, 32 and then at most 60 minutes. The worker processes at most 100 due events per run. After ten failed attempts, the event is marked **Failed**.

The **CRM Signal Outbox** DocType is restricted to System Managers. Review its status, source document, attempt count, last-attempt time and last error type. The detailed exception is recorded in Error Log. A Failed row is not automatically retried. A System Manager with CRM Signal Outbox read permission can use **Replay Failed Event** on the row; the action requires confirmation, accepts only Failed rows, preserves the original attempt count/last error, increments replay count, records actor/time and an audit Comment, and queues the existing idempotent worker after commit. If queueing is unavailable, the row remains Pending for the scheduled worker. Do not edit outbox rows or database tables manually to force a retry.

Outbox persistence is part of the source transaction. If the app cannot persist the outbox row, the Quotation submit or Opportunity update is rejected rather than silently losing the event. A failure to create the downstream CRM Signal after the outbox row exists does not block the source document; it is retried asynchronously. Realtime notification dispatch is separate and is not retried by the outbox. Frappe v16's after-commit Redis emitter suppresses Redis connection errors, so the app cannot confirm Redis publication or client receipt; treat realtime as best-effort and use the CRM Signals console/digest for durable review.

## Production acceptance checklist

Before enabling this app on a live site, record the installed Frappe/ERPNext versions and apps; confirm Company currencies, timezone, Opportunity workflows, terminal Lead statuses, and role assignments; test list/form/API/report/export access for Sales User, Sales Manager, System Manager and non-sales users; reconcile D2 results against native ERPNext reports; exercise webhook authentication/rate limiting; and rehearse backup, migration and rollback. CI is not a substitute for these target-site checks.
