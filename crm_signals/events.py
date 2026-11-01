"""Event-driven CRM Signals with stable source identity and failure isolation."""

import frappe

from crm_signals.event_identity import build_source_event_key
from crm_signals.settings import get_company_default_currency, get_signal_settings


def _log_error(title):
    """Record hook failures without breaking the source transaction."""
    try:
        frappe.log_error(message=frappe.get_traceback(), title=title)
    except Exception:
        pass


def _party_links(doctype, party_name):
    """Return one validated Link field for a Quotation party."""
    if not party_name:
        return {"lead": None, "customer": None}
    if doctype == "Customer":
        if not frappe.db.exists("Customer", party_name):
            frappe.throw(f"Customer {party_name} does not exist", frappe.LinkValidationError)
        return {"lead": None, "customer": party_name}
    if doctype == "Lead":
        if not frappe.db.exists("Lead", party_name):
            frappe.throw(f"Lead {party_name} does not exist", frappe.LinkValidationError)
        return {"lead": party_name, "customer": None}
    frappe.throw(f"Unsupported quotation party type: {doctype}", frappe.ValidationError)


def _existing_signal_name(event_key, *, locking_read=False):
    """Find the persisted signal; use a locking read after a unique-key race."""
    if locking_read:
        # The production MariaDB backend supports locking reads. Keep simple
        # test doubles and alternate adapters compatible with their lookup
        # contract; the Bench race test exercises the real SQL path.
        sql = getattr(frappe.db, "sql", None)
        if not sql:
            return frappe.db.get_value(
                "CRM Signal", {"source_event_key": event_key}, "name"
            )
        rows = sql(
            """
            SELECT name
            FROM `tabCRM Signal`
            WHERE source_event_key = %s
            LIMIT 1
            FOR UPDATE
            """,
            (event_key,),
            as_dict=True,
        )
        return rows[0].name if rows else None

    return frappe.db.get_value(
        "CRM Signal", {"source_event_key": event_key}, "name"
    )


def insert_signal_once(
    signal_type,
    message,
    priority,
    lead=None,
    customer=None,
    source_doctype=None,
    source_name=None,
    source_event_id=None,
    ignore_permissions=True,
):
    """Insert one signal per stable source event; return (document, created)."""
    event_key = build_source_event_key(source_doctype, source_name, source_event_id)
    if event_key:
        existing_name = _existing_signal_name(event_key)
        if existing_name:
            return frappe.get_doc("CRM Signal", existing_name), False

    signal = frappe.get_doc({
        "doctype": "CRM Signal",
        "signal_type": signal_type,
        "lead": lead,
        "customer": customer,
        "message": message,
        "priority": priority,
        "is_read": 0,
        "source_doctype": source_doctype,
        "source_name": source_name,
        "source_event_id": source_event_id,
        "source_event_key": event_key,
    })
    try:
        signal.insert(ignore_permissions=ignore_permissions)
    except Exception as error:
        if event_key and error.__class__.__name__ in {
            "DuplicateEntryError",
            "UniqueValidationError",
        }:
            # MariaDB's duplicate-key exception is wrapped by Frappe as
            # UniqueValidationError on supported v15/v16 versions. A
            # locking read sees the winning row even under repeatable-read
            # transaction isolation.
            existing_name = _existing_signal_name(event_key, locking_read=True)
            if existing_name:
                return frappe.get_doc("CRM Signal", existing_name, for_update=True), False
        raise

    try:
        from crm_signals.notifications import notify_signal

        notify_signal(signal)
    except Exception:
        _log_error("CRM Signal notification dispatch failed")
    return signal, True


def _company_threshold_value(doc, settings):
    """Compare in the Company's base currency, not the Quote's transaction currency."""
    company_currency = get_company_default_currency(getattr(doc, "company", None))
    threshold_currency = settings.get("threshold_currency")
    if not company_currency or not threshold_currency or threshold_currency != company_currency:
        return None

    base_total = getattr(doc, "base_grand_total", None)
    if base_total is not None:
        return float(base_total)
    if getattr(doc, "currency", None) == company_currency:
        return float(getattr(doc, "grand_total", 0) or 0)
    return None


def on_quotation_submit(doc, method=None):
    """Emit an idempotent high-value Quote signal using the configured threshold."""
    try:
        settings = get_signal_settings()
        if not settings["enabled"] or not settings["enable_quotation_signals"]:
            return

        amount = _company_threshold_value(doc, settings)
        if amount is None or amount < float(settings["quotation_threshold"] or 0):
            return

        links = _party_links(
            getattr(doc, "quotation_to", None), getattr(doc, "party_name", None)
        )
        party = doc.party_name or "the selected party"
        currency = getattr(doc, "currency", None)
        value = float(doc.grand_total or 0)
        formatted_amount = f"{currency} {value:,.2f}" if currency else f"{value:,.2f}"
        from crm_signals.signal_outbox import enqueue_signal_event

        enqueue_signal_event(
            signal_type="High-Value Quote",
            message=f"High-value quotation {doc.name} submitted for {party} ({formatted_amount})",
            priority="High",
            source_doctype="Quotation",
            source_name=doc.name,
            source_event_id=f"submit:{getattr(doc, 'modified', None) or doc.name}",
            **links,
        )
    except Exception:
        _log_error("CRM Signals failed to process a submitted Quotation")


def on_opportunity_update(doc, method=None):
    """Emit a signal only when an Opportunity enters a configured status."""
    try:
        settings = get_signal_settings()
        if not settings["enabled"] or not settings["enable_opportunity_signals"]:
            return
        if not doc.has_value_changed("status"):
            return
        statuses = {status.casefold() for status in settings["opportunity_trigger_statuses"]}
        current_status = str(getattr(doc, "status", "") or "").strip()
        if current_status.casefold() not in statuses:
            return

        before = doc.get_doc_before_save()
        previous_status = str(getattr(before, "status", "") or "") if before else ""
        lead = getattr(doc, "party_name", None) if getattr(doc, "opportunity_from", None) == "Lead" else None
        customer = getattr(doc, "party_name", None) if getattr(doc, "opportunity_from", None) == "Customer" else None
        from crm_signals.signal_outbox import enqueue_signal_event

        enqueue_signal_event(
            signal_type="Opportunity Activity",
            message=f"Opportunity {doc.name} status updated to {current_status}",
            priority="Medium",
            lead=lead,
            customer=customer,
            source_doctype="Opportunity",
            source_name=doc.name,
            source_event_id=(
                f"status:{previous_status}->{current_status}:"
                f"{getattr(doc, 'modified', None) or ''}"
            ),
        )
    except Exception:
        _log_error("CRM Signals failed to process an Opportunity status change")
