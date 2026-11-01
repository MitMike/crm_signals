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
