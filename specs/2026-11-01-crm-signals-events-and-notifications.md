# CRM Signals — Document events and recipient routing

**Status:** Baseline implemented; PR #19 adds settings, idempotency and parent-read permission enforcement for realtime recipients.

## Problem and users

Sales teams need relevant signals when business records cross meaningful thresholds or stages. Alerts must be attributable to a source event, sent only to relevant users and safe under retries.

## Goals

- Generate signals from trusted Frappe document events.
- Map each event to exactly one Lead or Customer when the source party is known.
- Keep recipient selection server-controlled and permission-conscious.
- Prevent duplicate signals and duplicate alert delivery when the same event is retried.
- Make business thresholds and Opportunity trigger states configurable without changing Python source.

## Current baseline behavior

### Quotation submission

Hook: Quotation.on_submit.

The current event emits a High priority High-Value Quote signal when grand_total is at least 200,000. It maps quotation_to plus party_name to one Lead or Customer Link. Unsupported party types or missing linked records fail validation. The current message formats the amount with a rupee symbol.

### Opportunity status change

Hook: Opportunity.on_update.

The current event emits a Medium priority Opportunity Activity signal when status changes to Replied. party_name is mapped to Lead or Customer according to opportunity_from. The current trigger is deliberately narrow because ERPNext workflows and site customizations can differ.

### Recipient routing

Recipients are the owner of the linked Lead/Customer and users assigned through active ToDo records. The resolver deduplicates addresses and filters to enabled System Users. Realtime delivery is user-targeted and uses after_commit.

## Decisions and configuration

Create a CRM Signals Settings singleton (or equivalent site configuration) with validated fields:

- high-value quotation threshold: default 200,000 in the Company's default currency; never assume INR from a hard-coded symbol;
- Opportunity status trigger list: default Replied to preserve current behavior;
- stale-Lead window for digest: default 3 calendar days;
- digest delivery time: default 08:30 in the verified site timezone;
- optional additional escalation users/roles, each validated and enabled.

If Company or its default currency cannot be resolved, currency-sensitive threshold alerts are unavailable rather than silently interpreted as INR. Settings changes are permission-restricted to System Manager and audited.

## Event idempotency

Every internally generated event receives a deterministic source event key:
- Quotation submit: source DocType + document name + submit event identity.
- Opportunity update: source DocType + document name + the specific transition identity, including the document modification/version marker.

The CRM Signal stores source DocType, source document name and source event key. A unique constraint or transaction-safe lookup prevents the same event key from creating multiple signals. A new genuine transition can create a new event; a retry of the same transition cannot.

External ingestion accepts an idempotency key from the provider. When present, it uses the same uniqueness contract. Do not rely on in-memory dedupe or time-window-only suppression.

## Recipient contract

Default recipients:
1. owner of the linked Lead or Customer;
2. active ToDo assignees for that linked record;
3. optional recipients explicitly configured for the relevant signal type.

Only enabled System Users are eligible. Recipients are deduplicated. Do not include Guest, disabled users, arbitrary caller-supplied addresses or every user with a Sales role by default. Before delivery, verify that each resolved recipient can read the linked party under Frappe permissions. If no eligible recipients remain, create the signal without a realtime broadcast and record a non-sensitive diagnostic.

Realtime delivery happens after the signal transaction commits. A failed notification must not roll back the business document event or signal record. Notification failures must be logged with the source event key and without secrets.

## Acceptance criteria

| ID | Requirement | Validation |
|---|---|---|
| EVT-AC1 | Submitted quotation at or above configured threshold creates one High signal | Unit + Bench fixture below/at/above threshold |
| EVT-AC2 | Quotation party mapping handles Lead and Customer and rejects unsupported party types | Unit + Bench fixtures |
| EVT-AC3 | Opportunity emits only for configured status transitions | Unit + Bench old/new status fixtures |
| EVT-AC4 | Replaying the same source event produces one signal | Idempotency test with repeated hook invocation |
| EVT-AC5 | A distinct later transition is not confused with a retry | Two different event keys in one document lifecycle |
| EVT-AC6 | Recipients are owner/active assignees plus explicit configured escalation only | Extend tests/test_notifications.py |
| EVT-AC7 | Disabled, Guest and non-System Users are excluded | Unit + Bench user fixtures |
| EVT-AC8 | Recipient cannot receive a sensitive alert for a parent they cannot read | Permission integration test |
| EVT-AC9 | Alert is published only after commit and only to a user-specific room | Bench realtime hook test |
| EVT-AC10 | Notification failure does not prevent signal creation or the source document transaction | Failure isolation test and error logging assertion |
| EVT-AC11 | Currency threshold is interpreted in Company default currency and shown in that currency | Multi-currency Bench fixture |

## Validation mapping

- Extend tests/test_notifications.py for dedupe, disabled users, parent read checks and delivery failures. The current implementation branch now fails closed when an owner/assignee cannot read the linked Lead/Customer.
- Add tests/test_events.py for quotation threshold, party mapping, Opportunity transitions and retry behavior.
- Add Bench-backed tests invoking actual Frappe document hooks.
- Keep the existing Playwright E2E focused on the user-visible alert and Console state; test transaction and recipient rules on the server.

## Risks and rollout

- ERPNext workflow statuses can be customized. Keep the default Replied value configurable and validate it against the deployed site's Opportunity metadata/workflow.
- Company currency can differ from INR. Remove currency symbols from server-generated messages unless they are derived from the source currency.
- Add schema migrations with a backfill/nullable rollout for source event metadata. Preserve old signals with an empty source key; do not fabricate historical event identities.
- Enable idempotency before relying on third-party retries.
