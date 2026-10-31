import frappe
from frappe.model.document import Document


class CRMSignal(Document):
    def validate(self):
        if self.lead and self.customer:
            frappe.throw("A CRM Signal can reference either a Lead or a Customer, not both.")
        if self.priority and self.priority not in {"Low", "Medium", "High", "Urgent"}:
            frappe.throw("Invalid CRM Signal priority.")
