import hashlib
import json

import frappe


def build_source_event_key(namespace, source_doctype, source_name, source_event_id):
    """Return a stable digest for one logical source event.

    A missing event ID deliberately disables deduplication for backward-compatible
    callers. New integrations should always supply a provider-stable event ID.
    """
    if not source_event_id:
        return None

    payload = {
        "namespace": str(namespace or "").strip(),
        "source_doctype": str(source_doctype or "").strip(),
        "source_name": str(source_name or "").strip(),
        "source_event_id": str(source_event_id).strip(),
    }
    if not payload["namespace"] or not payload["source_doctype"] or not payload["source_name"]:
        frappe.throw("Namespace, source DocType and source document are required for an idempotent signal.")

    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def get_signal_by_event_key(event_key):
    if not event_key:
        return None

    name = frappe.db.get_value("CRM Signal", {"source_event_key": event_key}, "name")
    return frappe.get_doc("CRM Signal", name) if name else None


def insert_signal_once(
    signal_values,
    *,
    namespace,
    source_doctype,
    source_name,
    source_event_id=None,
):
    """Insert a CRM Signal and return (document, created).

    The unique source_event_key field is the concurrency-safe final guard.
    Legacy callers without a source_event_id retain their original behavior.
    """
    values = dict(signal_values)
    event_key = build_source_event_key(
        namespace, source_doctype, source_name, source_event_id
    )
    if source_event_id:
        values.update(
            {
                "source_doctype": source_doctype,
                "source_name": source_name,
                "source_event_id": str(source_event_id),
                "source_event_key": event_key,
            }
        )

        existing = get_signal_by_event_key(event_key)
        if existing:
            return existing, False
    elif source_doctype or source_name:
        values.update(
            {
                "source_doctype": source_doctype,
                "source_name": source_name,
            }
        )

    signal = frappe.get_doc({"doctype": "CRM Signal", **values})
    try:
        signal.insert(ignore_permissions=True)
        return signal, True
    except frappe.DuplicateEntryError:
        # A concurrent worker may have inserted this event after the pre-check.
        existing = get_signal_by_event_key(event_key)
        if existing:
            return existing, False
        raise
