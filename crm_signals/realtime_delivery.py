"""Durable per-recipient retry for CRM Signal realtime notifications."""

from datetime import timedelta
from hashlib import sha256

import frappe

MAX_SIGNAL_NOTIFICATION_ATTEMPTS = 10
MAX_SIGNAL_NOTIFICATION_RETRY_MINUTES = 60
SIGNAL_NOTIFICATION_BATCH_SIZE = 100
ACTIVE_DELIVERY_STATUSES = {"Pending", "Attempted"}


def build_delivery_key(signal_name, recipient):
    """Return a stable identifier for one signal and one recipient."""
    return sha256(f"{signal_name}\x1f{recipient}".encode("utf-8")).hexdigest()


def _load_delivery_by_key_for_update(delivery_key):
    rows = frappe.db.sql(
        """
        SELECT name
        FROM `tabCRM Signal Notification Delivery`
        WHERE delivery_key = %s
        LIMIT 1
        FOR UPDATE
        """,
        (delivery_key,),
        as_dict=True,
    )
    if not rows:
        return None
    return frappe.get_doc(
        "CRM Signal Notification Delivery", rows[0].name, for_update=True
    )


def _get_or_create_delivery(signal_name, recipient):
    delivery_key = build_delivery_key(signal_name, recipient)
    existing_name = frappe.db.get_value(
        "CRM Signal Notification Delivery",
        {"delivery_key": delivery_key},
        "name",
    )
    if existing_name:
        return frappe.get_doc(
            "CRM Signal Notification Delivery", existing_name, for_update=True
        )

    delivery = frappe.get_doc({
        "doctype": "CRM Signal Notification Delivery",
        "signal": signal_name,
        "recipient": recipient,
        "delivery_key": delivery_key,
        "status": "Pending",
        "attempt_count": 0,
    })
    try:
        return delivery.insert(ignore_permissions=True)
    except Exception as error:
        if error.__class__.__name__ in {
            "DuplicateEntryError",
            "UniqueValidationError",
        }:
            winner = _load_delivery_by_key_for_update(delivery_key)
            if winner:
                return winner
        raise


def _retry_delay_minutes(attempt_count):
    exponent = max(int(attempt_count) - 1, 0)
    return min(2**exponent, MAX_SIGNAL_NOTIFICATION_RETRY_MINUTES)


def _log_delivery_error(delivery_name):
    try:
        frappe.log_error(
            message=frappe.get_traceback(),
            title=f"CRM Signal notification delivery failed: {delivery_name}",
        )
    except Exception:
        pass


def _record_delivery_failure(delivery, attempts, error, now):
    status = "Failed" if attempts >= MAX_SIGNAL_NOTIFICATION_ATTEMPTS else "Pending"
    retry_at = (
        None
        if status == "Failed"
        else now + timedelta(minutes=_retry_delay_minutes(attempts))
    )
    delivery.db_set(
        {
            "status": status,
            "attempt_count": attempts,
            "last_attempt_at": now,
            "last_error": error.__class__.__name__,
            "next_retry_at": retry_at,
        },
        update_modified=True,
    )
    _log_delivery_error(delivery.name)
    return {"status": status.lower(), "name": delivery.name}


def _cancel_delivery(delivery, reason):
    delivery.db_set(
        {"status": "Cancelled", "last_error": reason, "next_retry_at": None},
        update_modified=True,
    )
    return {"status": "cancelled", "name": delivery.name}


def _notification_payload(signal, delivery):
    return {
        "delivery_id": delivery.delivery_key,
        "name": signal.name,
        "signal_type": signal.signal_type,
        "priority": signal.priority,
        "message": signal.message,
        "lead": signal.lead,
        "customer": signal.customer,
    }


def process_signal_notification_delivery(delivery_name):
    """Publish one due delivery; Attempted never means human-delivered."""
    from frappe.utils import get_datetime, now_datetime

    delivery = frappe.get_doc(
        "CRM Signal Notification Delivery", delivery_name, for_update=True
    )
    if delivery.status not in ACTIVE_DELIVERY_STATUSES:
        return {"status": "skipped", "name": delivery.name}

    now = now_datetime()
    retry_at = get_datetime(delivery.next_retry_at) if delivery.next_retry_at else None
    if retry_at and retry_at > now:
        return {"status": "not_due", "name": delivery.name}
    if not frappe.db.exists("CRM Signal", delivery.signal):
        return _cancel_delivery(delivery, "SignalUnavailable")

    signal = frappe.get_doc("CRM Signal", delivery.signal)
    from crm_signals.notifications import get_signal_recipients

    attempts = int(delivery.attempt_count or 0)
    try:
        if delivery.recipient not in get_signal_recipients(signal):
            return _cancel_delivery(delivery, "RecipientNoLongerEligible")
    except Exception as error:
        return _record_delivery_failure(delivery, attempts + 1, error, now)

    if attempts >= MAX_SIGNAL_NOTIFICATION_ATTEMPTS:
        delivery.db_set(
            {"status": "Failed", "next_retry_at": None},
            update_modified=True,
        )
        return {"status": "failed", "name": delivery.name}

    attempts += 1
    delivery.db_set(
        {
            "status": "Attempted",
            "attempt_count": attempts,
            "last_attempt_at": now,
            "last_error": None,
            "next_retry_at": now
            + timedelta(minutes=_retry_delay_minutes(attempts)),
        },
        update_modified=True,
    )
    try:
        frappe.publish_realtime(
            event="crm_signal_received",
            message=_notification_payload(signal, delivery),
            user=delivery.recipient,
            after_commit=True,
        )
    except Exception as error:
        return _record_delivery_failure(delivery, attempts, error, now)
    return {"status": "attempted", "name": delivery.name}


def dispatch_signal_notifications(signal):
    """Persist each eligible recipient before attempting its realtime publish."""
    from crm_signals.notifications import get_signal_recipients

    results = {"attempted": 0, "failed": 0, "skipped": 0}
    for recipient in get_signal_recipients(signal):
        try:
            delivery = _get_or_create_delivery(signal.name, recipient)
            result = process_signal_notification_delivery(delivery.name)
            if result["status"] == "attempted":
                results["attempted"] += 1
            elif result["status"] in {"pending", "failed"}:
                results["failed"] += 1
            else:
                results["skipped"] += 1
        except Exception:
            results["failed"] += 1
            _log_delivery_error(signal.name)
    return results


def process_pending_signal_notification_deliveries(
    limit=SIGNAL_NOTIFICATION_BATCH_SIZE,
):
    """Retry due Pending/Attempted rows in bounded, committed batches."""
    from frappe.utils import now_datetime

    rows = frappe.get_all(
        "CRM Signal Notification Delivery",
        filters={"status": ["in", sorted(ACTIVE_DELIVERY_STATUSES)]},
        or_filters=[
            ["next_retry_at", "is", "not set"],
            ["next_retry_at", "<=", now_datetime()],
        ],
        fields=["name"],
        order_by="creation asc",
        limit_page_length=max(1, min(int(limit), SIGNAL_NOTIFICATION_BATCH_SIZE)),
    )
    results = {
        "attempted": 0,
        "pending": 0,
        "failed": 0,
        "cancelled": 0,
        "skipped": 0,
        "not_due": 0,
    }
    for row in rows:
        try:
            result = process_signal_notification_delivery(row.name)
            status = result["status"]
            results[status] = results.get(status, 0) + 1
            frappe.db.commit()
        except Exception:
            frappe.db.rollback()
            _log_delivery_error(row.name)
    return results
