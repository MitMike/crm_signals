# CRM Signals — Target-Site Acceptance Kit

**Purpose:** collect reproducible evidence that CRM Signals is safe and correct on the intended Frappe/ERPNext site. The confirmed framework target is Frappe v16.5; this kit remains an evidence template, not proof that any target-site test has already passed.

**Release rule:** do not sign off production until every P0 gate has an owner, dated evidence and an explicit pass. CI on a disposable Bench does not replace site-specific acceptance.

## 1. Execution record

| Field | Value |
|---|---|
| Site / environment | |
| Business owner | |
| Technical owner | |
| Test date (with timezone) | |
| CRM Signals commit / tag | |
| Frappe version (exact v16.5 patch/build) | |
| ERPNext version | |
| Helpdesk version | |
| Database engine / version | |
| Installed app list and versions | |
| Backup identifier | |
| Rollback owner | |

Attach the output of `bench version`, the installed-app inventory and the deployment revision. Redact credentials, tokens, customer data and internal hostnames before sharing evidence.

## 2. Preflight inventory

Record, do not infer:

- [ ] Frappe reports the expected v16.5 patch/build; ERPNext and Helpdesk exact versions are recorded and compatible.
- [ ] CRM Signals is installed and migrated on the intended site.
- [ ] Installed support, helpdesk, telephony, email and activity apps are inventoried with exact versions.
- [ ] Every enabled Company and its default currency are recorded.
- [ ] System Settings timezone and scheduler status are recorded.
- [ ] Lead and Opportunity workflows, status values and terminal statuses are exported/reviewed.
- [ ] Relevant custom fields, custom scripts, server scripts and permission overrides are inventoried.
- [ ] Sales roles and representative users are identified for the permission matrix.
- [ ] Email account, sender policy, mail queue and realtime deployment topology are recorded.
- [ ] Current CRM Signals Settings values and enabled presets are captured.

| Company | Default currency | Company override threshold | Derived currency | Legacy fallback threshold (only on exact currency match) | Approved? |
|---|---|---:|---|---:|---|
| | | | | | |

**Multi-company rule:** a Company-specific threshold row takes precedence and derives its currency from that Company's default currency. If no row exists, the legacy site-wide threshold is used only when its currency exactly matches the Quotation Company's base currency. No implicit FX conversion occurs. Record a row or explicitly approve the fallback for every enabled Company.

## 3. Deployment, migration and rollback

- [ ] Confirm the exact app revision and dependency lock state.
- [ ] Take a database and private/public files backup using the site's approved process.
- [ ] Record backup location, timestamp, retention and restore operator.
- [ ] Deploy to staging first.
- [ ] Run `bench --site <site> migrate` and capture complete output.
- [ ] Verify DocType schema, roles, fixtures, hooks, scheduler registrations and installed app state.
- [ ] Run CRM Signals tests appropriate to the environment.
- [ ] Perform a smoke test of Desk, CRM Signals Settings, dashboard/report routes and API access.
- [ ] Rehearse restore into an isolated environment; verify database and files are mutually consistent.
- [ ] Rehearse rollback to the prior app revision and restore point.
- [ ] Obtain technical and business approval before production deployment.

| Step | Command / evidence reference | Result | Owner | Date |
|---|---|---|---|---|
| Backup | | | | |
| Staging migrate | | | | |
| Smoke tests | | | | |
| Restore rehearsal | | | | |
| Rollback rehearsal | | | | |

Do not paste secrets or full customer records into this document.

## 4. Permission parity matrix

Test with real representative users, not only Administrator. Check each path independently because list visibility, direct document access and downstream report/export paths can differ.

| Role / persona | Signal list | Direct signal form | Dashboard/report | API read | Export/print | Digest email | Realtime |
|---|---|---|---|---|---|---|---|
| Sales User | | | | | | | |
| Sales Manager | | | | | | | |
| System Manager | | | | | | | |
| Non-sales user | | | | | | | |
| Disabled user | | | | | | | |

Acceptance criteria:
- [ ] A user cannot read signal content when they cannot read the linked Lead/Customer.
- [ ] List-query and direct-document access produce equivalent authorization outcomes.
- [ ] API access does not bypass document or linked-party permissions.
- [ ] Digest content is generated under each recipient's user context.
- [ ] Realtime delivery excludes users without the required read permissions.
- [ ] Export and print do not expose rows unavailable in the corresponding report/list.
- [ ] Helpdesk HD Ticket field-level read access is checked independently for `status_category`, `resolution_date`, `resolution_time`, `sla` (permlevel 7) and `agreement_status` (permlevel 8).
- [ ] Disabled or unapproved recipients receive no digest or realtime content.

Record user IDs/roles only in the site's secured test record; do not add personal data here.

## 5. D1/D2 data correctness and finance reconciliation

Use a fixed, approved date range and the site's native ERPNext reports as the comparison source. Record filters, company, currency, timezone and report run time. Reconcile by Company and currency; do not sum unlike currencies.

| Metric | CRM Signals result | Native ERPNext report/result | Company/currency | Difference | Explanation / sign-off |
|---|---:|---:|---|---:|---|
| Active Leads | | | | | |
| Active Opportunities | | | | | |
| Pipeline value | | | | | |
| Sales Invoice value excluding returns | | | | | |
| Payment Entry receipts | | | | | |
| POS receipts | | | | | |
| Party-account-currency receivables | | | | | |

- [ ] Confirm the selected Lead/Opportunity statuses match actual workflows.
- [ ] Confirm terminal Lead statuses and stale-Lead semantics with Sales.
- [ ] Confirm Sales Invoice returns/credit notes are excluded exactly as intended.
- [ ] Confirm Payment Entry receipt treatment independently of Sales Invoice return metadata.
- [ ] Confirm POS receipts are not double-counted with Sales Invoices.
- [ ] Confirm receivables are grouped by party account currency and reconcile to the native report.
- [ ] Explain every non-zero variance; finance owner signs off.

## 6. Webhook and integration security

- [ ] Create a dedicated integration System User; do not use Administrator.
- [ ] Grant only the required CRM Signal create/API permissions.
- [ ] Generate unique credentials per environment and store them in an approved secret manager.
- [ ] Enforce HTTPS/TLS at the public endpoint and reverse proxy.
- [ ] Apply gateway rate limits, request-size limits and abuse monitoring.
- [ ] Confirm authentication failures are logged without logging secrets.
- [ ] Verify stable `source_event_id` is supplied by each producer for retry idempotency.
- [ ] Test duplicate delivery, malformed payload, unauthorized user and rate-limit behavior.
- [ ] Document credential owner, rotation interval, revocation procedure and incident contact.
- [ ] Rotate a test credential and prove the old credential is rejected.

| Integration / producer | Service user | Permission scope | Rate limit | Secret owner | Rotation date |
|---|---|---|---|---|---|
| | | | | | |

## 7. Scheduler, email and realtime operations

- [ ] Confirm scheduler is enabled and workers are healthy.
- [ ] Confirm digest time is interpreted in the intended System Settings timezone.
- [ ] Confirm the configured recipient list contains only active, approved System Users.
- [ ] Trigger a controlled digest and inspect the queued email as each recipient.
- [ ] Confirm per-recipient failures do not block other recipients.
- [ ] Confirm duplicate scheduler execution does not queue duplicate recipient/date digests.
- [ ] Confirm mail provider delivery, bounce and suppression behavior.
- [ ] Confirm realtime notifications reach only authorized users.
- [ ] Record monitoring, alert thresholds, log locations and on-call owner.

Note: recipient-level failure isolation and digest queue idempotency are code-level safeguards; actual scheduler topology, mail-provider behavior and live realtime routing still require this site test.

## 8. Settings and business semantics

- [ ] System Manager reviews Balanced, Sales Focused and Executive presets before enabling.
- [ ] Master enable and external ingestion remain off until approved.
- [ ] Each enabled Company has an approved override or a currency-matched legacy fallback; no cross-currency comparison or implicit conversion is used.
- [ ] Opportunity status list matches actual workflow values.
- [ ] Stale-day window and timestamp semantics are approved.
- [ ] Digest time, timezone and extra recipients are approved.
- [ ] Each setting is tested after save and after a worker/scheduler restart.
- [ ] Non-System Manager users cannot modify settings or outbox records.

## 9. D3 Frappe Helpdesk adapter acceptance

The initial adapter is implemented for standard Frappe Helpdesk. Verify the installed app and schema rather than assuming that the target site's patch level exactly matches upstream. Record the observed metadata and policy:

| Question | Observed answer / evidence |
|---|---|
| Installed Helpdesk app and exact version | |
| `HD Ticket` and `HD Service Level Agreement` DocTypes present | |
| Required fields present: `creation`, `status_category`, `resolution_date`, `resolution_time`, `sla`, `agreement_status` | |
| Sales User permitted fields at read level (including permlevels 7/8) | |
| Sales Manager permitted fields at read level (including permlevels 7/8) | |
| Ticket DocType read permission for each role | |
| SLA DocType read permission for each role | |
| Active SLA working days/hours and timezone | |
| Active SLA holiday list | |
| Confirmed Monday–Saturday calendar match or documented exception | |
| Native pause/resume and Fulfilled/Failed behavior | |
| Retention/deletion policy and business-approved KPI interpretation | |

Do not automatically grant permlevel 7 or 8. Review all Helpdesk fields at those levels with the security owner. A field-level permission gap should make the affected metric unavailable, not zero.

### D3 staging test matrix

Create synthetic tickets only in staging. Allow the Helpdesk SLA engine to set native outcomes.

| Fixture | Expected dashboard behavior |
|---|---|
| Open ticket | Included in current Open backlog |
| Paused ticket | Included in current Paused backlog; not an SLA-compliance outcome |
| Resolved in last 30 days | Included in resolved cohort when `resolution_date` and status_category are readable |
| Ticket with Fulfilled SLA | Included in eligible denominator and fulfilled numerator |
| Ticket with Failed SLA | Included in eligible denominator and failed count |
| First Response Due / Resolution Due / Paused | Excluded from Fulfilled/Failed compliance denominator |
| Ticket without an SLA | Counted separately; excluded from compliance denominator |
| User without HD Ticket read | D3 unavailable |
| User without required field-level permission | Only affected measures unavailable; never displayed as zero |

Expected compliance is `Fulfilled / (Fulfilled + Failed)`. With no eligible outcomes, show unavailable (—), not 0%. Average resolution duration uses positive Helpdesk `resolution_time` values converted from seconds to business hours; it is not elapsed time from ticket creation. SLA policy working hours, holiday list and timezone are authoritative.

## 10. Release decision

| Gate | Status (Pass / Fail / Blocked) | Evidence link / artifact | Owner | Date |
|---|---|---|---|---|
| Supported versions and installed apps | | | | |
| Migration and schema verification | | | | |
| Backup / restore / rollback | | | | |
| Permission parity | | | | |
| D1/D2 finance reconciliation | | | | |
| Webhook security | | | | |
| Scheduler / email / realtime | | | | |
| Settings and business semantics | | | | |
| D3 Helpdesk version/schema/field permissions and SLA calendar acceptance | | | | |

**Decision:** Not approved / Approved for limited pilot / Approved for production

**Approvers:** Technical owner: ______  Business owner: ______  Finance/security (as applicable): ______

A blocked or failed P0 gate means no production sign-off. Record remediation as an issue with an owner and retest evidence.
