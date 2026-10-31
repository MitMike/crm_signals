import frappe
from frappe.model.document import Document

from crm_signals.settings import validate_settings_document


class CRMSignalsSettings(Document):
    def validate(self):
        validate_settings_document(self)
