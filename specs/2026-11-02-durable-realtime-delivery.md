# Durable realtime notification delivery

**Status:** Code/test implementation is CI-verified in PR #54; target-site Redis/worker/scheduler acceptance remains pending.

## Problem

Frappe v16 `publish_realtime(after_commit=True)` queues a callback and returns before Redis publication. Its after-commit Redis emitter suppresses connection errors. A successful Python call therefore does not prove Redis publication or browser receipt, and retrying without an idempotency key can create duplicate alerts.

## Contract

- Persist one delivery row per CRM Signal and eligible recipient before attempting publication.
- Derive a stable SHA-256 delivery ID from the signal name and recipient. Enforce uniqueness in the database.
- Store only the CRM Signal link, recipient, stable ID and operational status. Do not duplicate message text or source-document content in the ledger.
- Rebuild the payload from the CRM Signal only after re-resolving the current recipient set. Re-check CRM Signal, linked Lead/Customer and source-document read permissions through the existing recipient resolver on every attempt.
- If the signal no longer exists or the recipient is no longer eligible, mark the row Cancelled and do not publish.
- Use bounded at-least-once publish attempts with exponential backoff and a terminal Failed state. The minute scheduler recovers Pending/Attempted rows.
- `Attempted` means the Frappe publish callback was queued; it does not mean Redis delivery, browser receipt or human acknowledgement.
- Include the stable delivery ID in the realtime payload. The Desk client suppresses duplicate IDs within the active browser session.
- A publish attempt may be repeated after an unobservable Redis failure or worker crash. Client deduplication makes repeated attempts safe within the active session; this is not an exactly-once or human-delivery guarantee.

## Acceptance criteria

| ID | Requirement | Validation |
|---|---|---|
| RT-AC1 | One stable ledger row exists per signal/recipient pair | Bench idempotency test |
| RT-AC2 | Ledger is committed with the signal transaction and contains no copied message body | DocType/Bench test |
| RT-AC3 | Publish is user-targeted and includes the stable delivery ID | Bench test |
| RT-AC4 | Scheduler retries due Pending/Attempted rows and skips future rows using the same stable ID | Bench scheduler batch recovery test |
| RT-AC5 | Redis/publish exceptions back off and exhaust to Failed | Bench failure test |
| RT-AC6 | Permission revocation or relationship removal cancels delivery | Bench permission test |
| RT-AC7 | Duplicate IDs do not create duplicate toasts in one Desk session | Playwright test |
| RT-AC8 | v15, v16 and exact v16.5.0/Helpdesk reference lanes remain green | Required CI |
| RT-AC9 | Pilot confirms Redis outage recovery, worker restart, scheduler and permission revocation | Target-site acceptance |

## Operational limits

- Bounded batch size: 100 due rows per scheduler run.
- Maximum publish attempts: 10.
- Retry delay doubles from one minute and is capped at 60 minutes.
- System Managers can inspect status and error class; message payloads are not copied into the ledger.
- No UI action claims a notification was read or human-delivered. Acknowledgement would require a separate product decision and client/server contract.
