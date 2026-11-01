"""Transactional outbox for retryable Quotation and Opportunity signal events."""

from datetime import timedelta
from uuid import uuid4

import frappe

from crm_signals.event_identity import build_source_event_key

MAX_SIGNAL_OUTBOX_ATTEMPTS = 10
MAX_SIGNAL_OUTBOX_RETRY_MINUTES = 60
SIGNAL_OUTBOX_BATCH_SIZE = 100


class SignalOutboxPersistenceError(RuntimeError):
    """Raised when the event cannot be durably recorded with its source transaction."""


def _is_duplicate_key_error(error):
    return error.__class__.__name__ in {"DuplicateEntryError", "UniqueValidationError"}


def _load_outbox_by_key_for_update(event_key):
    """Read the winner using a current locking read after an insert race."""
    rows = frappe.db.sql(
        """
        SELECT name
        FROM `tabCRM Signal Outbox`
        WHERE source_event_key = %s
        LIMIT 1
        FOR UPDATE
        """,
        (event_key,),
        as_dict=True,
    )
    if not rows:
        return None
    return frappe.get_doc("CRM Signal Outbox", rows[0].name, for_update=True)


def _find_outbox_name(event_key):
    return frappe.db.get_value(
        "CRM Signal Outbox", {"source_event_key": event_key}, "name"
    )


def _get_or_create_outbox(payload):
    event_key = build_source_event_key(
        payload["source_doctype"],
        payload["source_name"],
        payload["source_event_id"],
    )
    if not event_key:
        raise ValueError("A stable source event identity is required for outbox delivery.")

    existing_name = _find_outbox_name(event_key)
    if existing_name:
        return frappe.get_doc("CRM Signal Outbox", existing_name, for_update=True)

    outbox = frappe.get_doc({
        "doctype": "CRM Signal Outbox",
        **payload,
        "source_event_key": event_key,
        "status": "Pending",
        "attempt_count": 0,
    })
    try:
        return outbox.insert(ignore_permissions=True)
    except Exception as error:
        if _is_duplicate_key_error(error):
            winner = _load_outbox_by_key_for_update(event_key)
            if winner:
                return winner
        raise


def _retry_delay_minutes(attempt_count):
    exponent = max(int(attempt_count) - 1, 0)
    return min(2**exponent, MAX_SIGNAL_OUTBOX_RETRY_MINUTES)


def _record_delivery_failure(outbox_name, error):
    from frappe.utils import now_datetime

    outbox = frappe.get_doc("CRM Signal Outbox", outbox_name, for_update=True)
    attempts = int(outbox.attempt_count or 0) + 1
    exhausted = attempts >= MAX_SIGNAL_OUTBOX_ATTEMPTS
    now = now_datetime()
    values = {
        "attempt_count": attempts,
        "last_attempt_at": now,
        "last_error": error.__class__.__name__,
        "status": "Failed" if exhausted else "Pending",
        "next_retry_at": (
            None
            if exhausted
            else now + timedelta(minutes=_retry_delay_minutes(attempts))
        ),
    }
    outbox.db_set(values, update_modified=True)
    try:
        frappe.log_error(
            message=frappe.get_traceback(),
            title=f"CRM Signals outbox delivery failed: {outbox_name}",
        )
    except Exception:
        pass
    return values["status"]


def process_signal_outbox_event(outbox_name):
    """Attempt one pending outbox event under a row lock; never raise delivery errors."""
    from frappe.utils import get_datetime, now_datetime

    outbox = frappe.get_doc("CRM Signal Outbox", outbox_name, for_update=True)
    if outbox.status != "Pending":
        return {"status": "skipped", "name": outbox.name}

    now = now_datetime()
    retry_at = get_datetime(outbox.next_retry_at) if outbox.next_retry_at else None
    if retry_at and retry_at > now:
        return {"status": "not_due", "name": outbox.name}

    save_point = f"crm_signal_outbox_{uuid4().hex[:12]}"
    frappe.db.savepoint(save_point)
    try:
        from crm_signals.events import insert_signal_once

        signal, _created = insert_signal_once(
            signal_type=outbox.signal_type,
            message=outbox.message,
            priority=outbox.priority,
            lead=outbox.lead,
            customer=outbox.customer,
            source_doctype=outbox.source_doctype,
            source_name=outbox.source_name,
            source_event_id=outbox.source_event_id,
            ignore_permissions=True,
        )
        outbox.db_set(
            {
                "status": "Completed",
                "signal": signal.name,
                "completed_at": now_datetime(),
                "last_attempt_at": now_datetime(),
                "last_error": None,
                "next_retry_at": None,
            },
            update_modified=True,
        )
        frappe.db.release_savepoint(save_point)
        return {"status": "completed", "name": outbox.name, "signal": signal.name}
    except Exception as error:
        frappe.db.rollback(save_point=save_point)
        status = _record_delivery_failure(outbox.name, error)
        return {"status": status.lower(), "name": outbox.name}


def enqueue_signal_event(
    *,
    signal_type,
    message,
    priority,
    source_doctype,
    source_name,
    source_event_id,
    lead=None,
    customer=None,
):
    """Persist the event in the source transaction, then attempt immediate delivery."""
    payload = {
        "signal_type": signal_type,
        "message": message,
        "priority": priority,
        "source_doctype": source_doctype,
        "source_name": source_name,
        "source_event_id": source_event_id,
        "lead": lead,
        "customer": customer,
    }
    try:
        outbox = _get_or_create_outbox(payload)
    except Exception as error:
        raise SignalOutboxPersistenceError(
            "CRM Signal event could not be persisted to the transactional outbox."
        ) from error

    if outbox.status == "Pending":
        # The outbox row must commit with the source document before delivery
        # starts. Running the worker inside this transaction makes competing
        # idempotent inserts wait on a row whose owner is still doing delivery.
        # The periodic scheduler remains the recovery path if queueing fails.
        try:
            frappe.enqueue(
                "crm_signals.signal_outbox.process_signal_outbox_event",
                queue="short",
                enqueue_after_commit=True,
                outbox_name=outbox.name,
            )
        except Exception:
            try:
                frappe.log_error(
                    message=frappe.get_traceback(),
                    title=f"CRM Signals outbox enqueue failed: {outbox.name}",
                )
            except Exception:
                pass
    return outbox.name


def process_pending_signal_outbox(limit=SIGNAL_OUTBOX_BATCH_SIZE):
    """Retry due events in small committed batches without allowing old retries to starve new ones."""
    from frappe.utils import now_datetime

    names = frappe.get_all(
        "CRM Signal Outbox",
        filters={"status": "Pending"},
        or_filters=[
            ["next_retry_at", "is", "not set"],
            ["next_retry_at", "<=", now_datetime()],
        ],
        fields=["name"],
        order_by="creation asc",
        limit_page_length=max(1, min(int(limit), SIGNAL_OUTBOX_BATCH_SIZE)),
    )
    results = {"completed": 0, "pending": 0, "failed": 0, "skipped": 0, "not_due": 0}
    for row in names:
        try:
            result = process_signal_outbox_event(row.name)
            status = result["status"]
            results[status] = results.get(status, 0) + 1
            frappe.db.commit()
        except Exception:
            frappe.db.rollback()
            try:
                frappe.log_error(
                    message=frappe.get_traceback(),
                    title=f"CRM Signals outbox worker failed: {row.name}",
                )
            except Exception:
                pass
    return results
