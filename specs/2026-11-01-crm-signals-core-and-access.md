# CRM Signals Core — Data, ingestion, access and console

**Status:** Implemented baseline; release hardening and operational acceptance remain.
**Scope:** CRM Signal records, authenticated ingestion, record permissions, realtime delivery and the Signals Console.

## Problem and users

Sales users need reliable, actionable activity signals connected to Leads or Customers. Sales Managers need team visibility. External systems need a controlled write API without Administrator credentials or anonymous access.

## Goals

- Maintain one normalized CRM Signal record for supported activity types.
- Accept authenticated server-to-server POST requests with strict validation.
- Enforce record access consistently in list, direct-document and API workflows.
- Notify only relevant, enabled system users.
- Provide permission-filtered totals, type breakdown and recent activity in Desk.
- Keep data semantics clear: a signal can be linked to one Lead, one Customer, or neither; it cannot be linked to both.

## Non-goals

- Replacing ERPNext CRM, Communication, email, calling or WhatsApp systems.
- Tracking arbitrary website behavior without a registered integration.
- Broadcasting notifications to all logged-in users.
- Per-user read receipts in this first version; read state is a shared signal-level team acknowledgement.
- Treating a signal as proof that a recipient acted on the underlying business record.

## Data contract

### CRM Signal DocType

The existing DocType contains:

| Field | Meaning | Rule |
|---|---|---|
| signal_type | Kind of event | Required; allowlisted |
| priority | Triage priority | Required; Low, Medium, High or Urgent |
| is_read | Shared team acknowledgement | Boolean; defaults to 0 |
| lead | Related Lead | Optional; mutually exclusive with Customer |
| customer | Related Customer | Optional; mutually exclusive with Lead |
| message | Human-readable event description | Required; trimmed; maximum 2,000 characters |
| owner / creation | Frappe audit metadata | Framework-managed |

Allowed signal types are Website Visit, Email Opened, Link Clicked, WhatsApp Interaction, Inbound Call, High-Value Quote and Opportunity Activity. New types require a spec update, select-option migration, tests and a consumer review.

Validation belongs in the DocType as well as the API. Direct Desk creation must not bypass the allowlist, priority validation, link exclusivity or message constraints.

### Ingestion API

Endpoint: POST /api/method/crm_signals.api.ingest_signal

| Input | Requirement |
|---|---|
| signal_type | Required string from the allowlist |
| message | Required non-empty string; maximum 2,000 characters |
| lead | Optional Lead name |
| customer | Optional Customer name |
| priority | Optional; defaults to Medium; allowlisted |

The request must provide no more than one of lead and customer. A supplied link must resolve to an existing record. Recipient lists, owner, read state, creation time and permission flags are never accepted from the caller.

Authentication is Frappe API key/secret for a dedicated integration user over HTTPS. Guest is rejected. The integration user receives only the CRM Signal create permission needed to insert records. The endpoint uses normal Frappe insertion and lets the framework own the transaction. TLS, rate limiting, secret rotation and monitoring are deployment responsibilities.

For backward compatibility, an idempotency key is optional for existing callers. New integrations must send a stable source event ID; when present, the server stores and enforces it as unique. The next schema hardening change adds source DocType, source name and source event ID fields so retries can be identified and reconciled. Without an idempotency key, duplicate external POSTs cannot be guaranteed to collapse into one record.

## Permission contract

- Sales Manager and System Manager access continues to fall back to the DocType role permissions.
- A Sales User can read a linked signal only when they own the linked Lead/Customer or have an active ToDo assignment to it, and they can read the parent record under Frappe permissions.
- An unlinked signal is visible only to its owner and users otherwise granted DocType-level access.
- Write access for Sales Users requires a readable relationship plus ownership of the signal, ownership of the parent party or an active assignment.
- List-query conditions and direct-document checks must enforce equivalent rules.
- An owner-only list condition applies only to unlinked signals; linked signals require an owned/assigned, permission-readable parent relationship.
- Realtime alerts are sent only when the recipient can read both the CRM Signal and its linked Lead/Customer; a notification is not an authorization grant.
- Report, export, print, API and Desk list access must be tested; hiding a page link is not an authorization control.

An active assignment is a ToDo referencing the Lead/Customer where status is neither Cancelled nor Closed. Disabled users are never notification recipients.

## Realtime contract

Recipient resolution uses the related Lead/Customer owner plus active ToDo assignees. The resolved list is deduplicated and filtered to enabled System Users. The server publishes a user-targeted crm_signal_received event after commit. There is no site-wide fallback and no caller-controlled recipient parameter.

The current alert contains signal type, priority, message and linked party references. It is an alert, not an authorization grant; opening the CRM Signal must still pass Frappe read permissions. Do not put API credentials, secrets or arbitrary payloads in the realtime message.

## Signals Console

Route: /app/crm-signals-dashboard

The endpoint returns:
- total visible signals;
- unread signals using the shared is_read state;
- High and Urgent signals;
- signals created in the last seven days;
- visible signal counts grouped by signal type;
- the 12 most recent visible records.

All data reads use permission-aware Frappe APIs. A denied or missing source is not converted into a successful zero. A user without CRM Signal read permission receives an authorization error and the UI shows an access message.

The shared read flag is intentionally a team-level acknowledgement. If personal inboxes or per-user unread counts become a requirement, replace this policy with a separate per-user acknowledgement model in a new spec; do not silently reinterpret the current Boolean.

## Acceptance criteria

| ID | Requirement | Validation |
|---|---|---|
| CORE-AC1 | Guest cannot call the ingestion endpoint | Bench integration test for unauthenticated POST |
| CORE-AC2 | Authenticated integration user with create permission can insert a valid signal | Bench integration test using a non-Administrator user |
| CORE-AC3 | Unsupported type/priority, empty or oversized message, both party links, and invalid links are rejected | Parameterized API and DocType validation tests |
| CORE-AC4 | API caller cannot select notification recipients, owner or read state | API contract and permission tests |
| CORE-AC5 | Sales User access requires ownership/assignment and parent read permission | Extend tests/test_permissions.py |
| CORE-AC6 | List and direct-document access apply equivalent rules | Bench tests for List, Form, report/export and API reads |
| CORE-AC7 | Only enabled related users receive a user-targeted after-commit event | Extend tests/test_notifications.py |
| CORE-AC8 | Unlinked signals do not trigger a site-wide notification | Existing notification test plus Bench assertion |
| CORE-AC9 | Console metrics and recent rows obey the current user's signal permissions | Bench API test and e2e/crm-signals-dashboard.spec.ts |
| CORE-AC10 | Shared read flag is described and rendered consistently | UI test and role-level Desk smoke test |

## Implementation and verification notes

Existing code is in crm_signals/api.py, crm_signals/permissions.py, crm_signals/notifications.py, crm_signals/crm_signals/doctype/crm_signal/ and crm_signals/crm_signals/page/crm_signals_dashboard/. Existing focused unit coverage includes tests/test_permissions.py and tests/test_notifications.py. The live console E2E is part of the Bench workflow.

Remaining hardening:
1. Add source-event metadata and idempotent insert behavior.
2. Exercise read, write, list, report, export and direct-document rules on a real site with Sales User, Sales Manager and non-sales users.
3. Confirm the integration user's exact role and permission setup on the target site.
4. Confirm whether the shared read acknowledgement is acceptable to the sales team before adding personal inbox behavior.
