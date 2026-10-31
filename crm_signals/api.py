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


def _read_text(value, fieldname, *, required=False, max_length=None):
    if value is None:
        value = ""
    if not isinstance(value, str):
        frappe.throw(_("{0} must be text").format(fieldname), frappe.ValidationError)
    value = value.strip()
    if required and not value:
        frappe.throw(_("{0} is mandatory").format(fieldname), frappe.MandatoryError)
    if max_length is not None and len(value) > max_length:
        frappe.throw(
            _("{0} cannot exceed {1} characters").format(fieldname, max_length),
            frappe.ValidationError,
        )
    return value or None


@frappe.whitelist(methods=["POST"])
def ingest_signal():
    """Create a CRM Signal from an authenticated server-to-server integration.

    Authenticate with Frappe API key/secret as a dedicated integration user.
    The caller must have permission to create CRM Signal documents.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication is required"), frappe.AuthenticationError)

    data = frappe.local.form_dict
    signal_type = _read_text(data.get("signal_type"), "signal_type", required=True)
    message = _read_text(
        data.get("message"), "message", required=True, max_length=MAX_MESSAGE_LENGTH
    )
    lead = _read_text(data.get("lead"), "lead")
    customer = _read_text(data.get("customer"), "customer")
    priority = _read_text(data.get("priority") or "Medium", "priority", required=True)

    if signal_type not in ALLOWED_SIGNAL_TYPES:
        frappe.throw(_("Unsupported signal_type"), frappe.ValidationError)
    if priority not in ALLOWED_PRIORITIES:
        frappe.throw(_("Unsupported priority"), frappe.ValidationError)
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



@frappe.whitelist()
def get_dashboard_data():
    """Return permission-filtered CRM Signal metrics for the Desk dashboard.

    All reads use frappe.get_list so DocType permissions and the app's
    permission_query_conditions hook are applied to the requesting user.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication is required"), frappe.AuthenticationError)
    if not frappe.has_permission("CRM Signal", ptype="read"):
        frappe.throw(_("You do not have permission to view CRM Signals"), frappe.PermissionError)

    from frappe.utils import add_days, nowdate

    def count_signals(filters=None):
        rows = frappe.get_list(
            "CRM Signal",
            fields=["count(name) as total"],
            filters=filters or {},
            limit_page_length=1,
        )
        return int((rows[0].get("total") if rows else 0) or 0)

    stats = {
        "total": count_signals(),
        "unread": count_signals({"is_read": 0}),
        "high_priority": count_signals({"priority": ["in", ["High", "Urgent"]]}),
        "last_7_days": count_signals({"creation": [">=", add_days(nowdate(), -7)]}),
    }

    by_type = frappe.get_list(
        "CRM Signal",
        fields=["signal_type", "count(name) as total"],
        group_by="signal_type",
        order_by="signal_type asc",
        limit_page_length=20,
    )

    recent = frappe.get_list(
        "CRM Signal",
        fields=[
            "name", "creation", "signal_type", "priority",
            "message", "lead", "customer", "is_read",
        ],
        order_by="creation desc",
        limit_page_length=12,
    )

    return {
        "stats": stats,
        "by_type": [
            {"signal_type": row.signal_type, "total": int(row.total or 0)}
            for row in by_type
        ],
        "recent": recent,
    }
