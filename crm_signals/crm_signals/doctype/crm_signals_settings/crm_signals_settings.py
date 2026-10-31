import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint


class CRMSignalsSettings(Document):
    def validate(self):
        if flt(self.high_value_quotation_threshold) < 0:
            frappe.throw(_("High-value quotation threshold cannot be negative."))

        if cint(self.lead_stale_days) < 1:
            frappe.throw(_("Lead stale days must be at least one."))

        statuses = [
            value.strip()
            for value in (self.opportunity_signal_statuses or "").splitlines()
            if value.strip()
        ]
        if not statuses:
            frappe.throw(_("Configure at least one Opportunity signal status."))

        self.opportunity_signal_statuses = "\n".join(dict.fromkeys(statuses))

        if self.company:
            currency = frappe.db.get_value("Company", self.company, "default_currency")
            if not currency:
                frappe.throw(_("The selected Company has no default currency."))
            self.company_currency = currency

        seen_users = set()
        for row in self.additional_digest_recipients or []:
            if not row.user or row.user in seen_users:
                frappe.throw(_("Digest recipients must be unique System Users."))
            seen_users.add(row.user)
            user = frappe.db.get_value("User", row.user, ["enabled", "user_type"], as_dict=True)
            if not user or not user.enabled or user.user_type != "System User":
                frappe.throw(_("Additional digest recipients must be enabled System Users."))
