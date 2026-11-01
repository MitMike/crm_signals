"""Validation for the internal, System Manager-visible signal delivery outbox."""

import frappe
from frappe.model.document import Document

from crm_signals.event_identity import build_source_event_key

ALLOWED_SIGNAL_TYPES = {
    "Website Visit",
    "Email Opened",
    "Link Clicked",
    "WhatsApp Interaction",
    "Inbound Call",
    "High-Value Quote",
    "Opportunity Activity",
}
ALLOWED_PRIORITIES = {"Low", "Medium", "High", "Urgent"}
ALLOWED_STATUSES = {"Pending", "Completed", "Failed"}


class CRMSignalOutbox(Document):
    def validate(self):
        if self.signal_type not in ALLOWED_SIGNAL_TYPES:
            frappe.throw("Invalid CRM Signal outbox event type.")
        if self.priority not in ALLOWED_PRIORITIES:
            frappe.throw("Invalid CRM Signal outbox priority.")
        if self.status not in ALLOWED_STATUSES:
            frappe.throw("Invalid CRM Signal outbox status.")
        if not (self.message or "").strip() or len(self.message) > 2000:
            frappe.throw("CRM Signal outbox message must contain 1 to 2000 characters.")
        if self.lead and self.customer:
            frappe.throw("A CRM Signal outbox event can reference either a Lead or a Customer, not both.")

        source_parts = tuple(
            str(value).strip() if value else None
            for value in (self.source_doctype, self.source_name, self.source_event_id)
        )
        if not all(source_parts):
            frappe.throw("Source type, source name and source event ID are required together.")
        self.source_doctype, self.source_name, self.source_event_id = source_parts
        self.source_event_key = build_source_event_key(*source_parts)


@frappe.whitelist()
def replay_failed_signal_outbox(name):
    """Audited, idempotent operator replay for a terminal Failed outbox row."""
    if "System Manager" not in frappe.get_roles():
        frappe.throw("Only System Managers can replay failed CRM Signal events.", frappe.PermissionError)

    outbox = frappe.get_doc("CRM Signal Outbox", name, for_update=True)
    if outbox.status != "Failed":
        frappe.throw("Only Failed CRM Signal outbox events can be replayed.")

    from frappe.utils import now_datetime

    now = now_datetime()
    outbox.db_set(
        {
            "status": "Pending",
            "next_retry_at": None,
            "replay_count": int(outbox.replay_count or 0) + 1,
            "last_replayed_at": now,
            "last_replayed_by": frappe.session.user,
        },
        update_modified=True,
    )
    outbox.add_comment(
        "Info",
        f"Manual replay requested by {frappe.session.user}. Previous attempt history retained.",
    )
    try:
        frappe.enqueue(
            "crm_signals.signal_outbox.process_signal_outbox_event",
            queue="short",
            enqueue_after_commit=True,
            outbox_name=outbox.name,
        )
    except Exception:
        # The Pending row is durable; the scheduled worker remains the fallback.
        try:
            frappe.log_error(
                message=frappe.get_traceback(),
                title=f"CRM Signals manual replay enqueue failed: {outbox.name}",
            )
        except Exception:
            pass
    return {"status": "Pending", "name": outbox.name}
