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


class CRMSignal(Document):
    def validate(self):
        if self.signal_type not in ALLOWED_SIGNAL_TYPES:
            frappe.throw("Invalid CRM Signal type.")
        if self.priority not in ALLOWED_PRIORITIES:
            frappe.throw("Invalid CRM Signal priority.")
        if self.lead and self.customer:
            frappe.throw("A CRM Signal can reference either a Lead or a Customer, not both.")
        if not (self.message or "").strip():
            frappe.throw("A CRM Signal message is required.")
        if len(self.message) > 2000:
            frappe.throw("CRM Signal message cannot exceed 2000 characters.")

        source_parts = tuple(
            str(value).strip() if value else None
            for value in (self.source_doctype, self.source_name, self.source_event_id)
        )
        if any(source_parts) and not all(source_parts):
            frappe.throw("Source type, source name and source event ID must be supplied together.")

        if all(source_parts):
            self.source_doctype, self.source_name, self.source_event_id = source_parts
            # Never trust a hash supplied by a Desk/API caller. The server owns
            # the source-event namespace and must derive the unique key itself.
            self.source_event_key = build_source_event_key(*source_parts)
        else:
            self.source_event_key = None
