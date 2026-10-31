import frappe
from frappe.model.document import Document


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
