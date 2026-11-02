"""Validation for the internal realtime notification delivery ledger."""

import frappe
from frappe.model.document import Document

from crm_signals.realtime_delivery import build_delivery_key

ALLOWED_STATUSES = {"Pending", "Attempted", "Failed", "Cancelled"}


class CRMSignalNotificationDelivery(Document):
    def validate(self):
        if self.status not in ALLOWED_STATUSES:
            frappe.throw("Invalid CRM Signal notification delivery status.")
        if not self.signal or not self.recipient:
            frappe.throw("A CRM Signal and recipient are required.")
        self.delivery_key = build_delivery_key(self.signal, self.recipient)
