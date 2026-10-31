import frappe
from frappe import _


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
MAX_MESSAGE_LENGTH = 2000


@frappe.whitelist()
def ingest_signal():
    """Create a CRM Signal from an authenticated server-to-server integration.

    Authenticate with Frappe API key/secret as a dedicated integration user.
    The caller must have permission to create CRM Signal documents.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication is required"), frappe.AuthenticationError)

    data = frappe.local.form_dict
    signal_type = (data.get("signal_type") or "").strip()
    message = (data.get("message") or "").strip()
    lead = (data.get("lead") or "").strip() or None
    customer = (data.get("customer") or "").strip() or None
    priority = (data.get("priority") or "Medium").strip()

    if not signal_type or not message:
        frappe.throw(_("signal_type and message are mandatory fields"), frappe.MandatoryError)
    if signal_type not in ALLOWED_SIGNAL_TYPES:
        frappe.throw(_("Unsupported signal_type"), frappe.ValidationError)
    if priority not in ALLOWED_PRIORITIES:
        frappe.throw(_("Unsupported priority"), frappe.ValidationError)
    if len(message) > MAX_MESSAGE_LENGTH:
        frappe.throw(_("message cannot exceed {0} characters").format(MAX_MESSAGE_LENGTH), frappe.ValidationError)
    if lead and customer:
        frappe.throw(_("Provide either lead or customer, not both"), frappe.ValidationError)
    if lead and not frappe.db.exists("Lead", lead):
        frappe.throw(_("Lead {0} does not exist").format(lead), frappe.LinkValidationError)
    if customer and not frappe.db.exists("Customer", customer):
        frappe.throw(_("Customer {0} does not exist").format(customer), frappe.LinkValidationError)

    # Recipient selection is never caller-controlled; the resolver uses related
    # document ownership and active ToDo assignments only.
    doc = frappe.get_doc({
        "doctype": "CRM Signal",
        "signal_type": signal_type,
        "lead": lead,
        "customer": customer,
        "message": message,
        "priority": priority,
        "is_read": 0,
    })
    doc.insert()  # Enforces normal Frappe permissions; framework owns transaction.

    from crm_signals.notifications import notify_signal

    notify_signal(doc)
    return {"status": "success", "signal": doc.name}
