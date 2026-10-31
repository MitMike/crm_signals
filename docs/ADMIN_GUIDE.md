# CRM Signals — Administrator and user guide

## Purpose and scope

CRM Signals is an extension to ERPNext CRM. It creates contextual signal records, sends recipient-scoped Desk notifications, and provides a daily sales digest. It does not replace ERPNext Leads, Opportunities, Quotations, Communications or a support application.

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

## Configure CRM Signals

1. Sign in as a System Manager.
2. Open **CRM Signals Settings** from the Desk search/awesome bar.
3. Select a starter preset: **Balanced**, **Sales Focused** or **Executive**.
4. Review every value. Presets are starting points, not recommended policy for every company.
5. Confirm the threshold currency matches the default Company's currency.
6. Replace Opportunity trigger statuses with exact values used by the site's workflow.
7. Set the Lead not-modified window and site-local digest time.
8. Add optional additional recipients using enabled System User email addresses, one per line.
9. Save and verify the resulting settings before enabling the feature.

### Preset starting values

| Setting | Balanced | Sales Focused | Executive |
|---|---:|---:|---:|
| Quotation threshold | 200,000 | 100,000 | 500,000 |
| Opportunity trigger status | Replied | Replied | Replied |
| Lead not-modified window | 3 days | 2 days | 5 days |
| Digest time | 08:30 | 08:00 | 08:30 |

The amount is interpreted in the threshold currency shown in Settings. The starter values do not imply INR or any other currency. The first release uses one site-wide threshold currency; multi-company sites with different base currencies need a separate per-company policy before enabling threshold alerts for all companies.

Selecting a preset applies its starting values. You can edit any field afterwards; the preset indicator changes to **Custom**. Selecting another preset again replaces the preset-controlled fields.

## What the settings mean

- **Enable CRM Signals:** master switch for event-generated signals.
- **Enable authenticated external ingestion:** enables the POST endpoint for approved integrations.
- **High-value Quotation threshold:** compares a submitted Quotation's base total with the configured Company-currency threshold. The message displays the Quotation's own transaction currency.
- **Opportunity trigger statuses:** exact status names that generate an event when an Opportunity transitions into one of them.
- **Lead not-modified window:** reports Leads whose modified timestamp is older than the configured number of days. It does not prove there was no call, email or meeting.
- **Digest time:** evaluated against the timezone in System Settings. The scheduler checks each minute; delivery can be delayed by worker/scheduler load.
- **Additional digest recipients:** additional email addresses are resolved to enabled System Users. Arbitrary external email addresses, Guest users and disabled users are not accepted.

## Using the Signals Console

Open **CRM Signals** workspace, then select **CRM Signals Dashboard** (route `/app/crm-signals-dashboard`). The console displays visible signal totals, shared unread state, high-priority signals, recent signal types and the latest records. A linked Lead or Customer opens through the normal Desk permission checks.

The `is_read` flag is a shared team acknowledgement in this release, not an individual read receipt or private inbox.

## S.A.H.D.E.V. dashboards

Open **S.A.H.D.E.V. Executive Compass** (route `/app/sahdev-dashboard`). D1 shows Lead and Opportunity indicators. D2 shows invoice, customer receipt, POS receipt, receivable and overdue measures. Monetary values remain grouped by their source currency. Missing schema or permissions must show as unavailable rather than zero.

D3 Service Resolution/SLA is not enabled until the installed support application's DocTypes, SLA lifecycle and permissions are discovered and verified.

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
- **No realtime notification:** verify the linked Lead/Customer owner and active ToDo assignees; there is intentionally no site-wide broadcast.
- **Signal not visible:** check CRM Signal role permissions and linked-party ownership/assignment. A notification is not an authorization grant.
- **Duplicate external event:** send a stable source event ID and use the same integration user for retries.

## Production acceptance checklist

Before enabling this app on a live site, record the installed Frappe/ERPNext versions and apps; confirm Company currencies, timezone, Opportunity workflows, terminal Lead statuses, and role assignments; test list/form/API/report/export access for Sales User, Sales Manager, System Manager and non-sales users; reconcile D2 results against native ERPNext reports; exercise webhook authentication/rate limiting; and rehearse backup, migration and rollback. CI is not a substitute for these target-site checks.
