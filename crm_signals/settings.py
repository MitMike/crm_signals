import frappe
from frappe import _
from frappe.utils import flt


DEFAULT_HIGH_VALUE_THRESHOLD = 200000
DEFAULT_OPPORTUNITY_SIGNAL_STATUSES = ("Replied",)
DEFAULT_LEAD_STALE_DAYS = 3
DEFAULT_DIGEST_TIME = "08:30:00"


def get_settings():
    """Return the singleton settings document, or None before the first migration."""
    if not frappe.db.exists("DocType", "CRM Signals Settings"):
        return None
    return frappe.get_single("CRM Signals Settings")


def get_company_currency(company=None):
    company = company or frappe.defaults.get_global_default("company")
    if not company or not frappe.db.exists("Company", company):
        return None
    return frappe.db.get_value("Company", company, "default_currency")


def get_high_value_threshold(company=None):
    """Return (amount, currency, configured_company) in the company's base currency."""
    settings = get_settings()
    configured_company = (settings.company if settings else None) or company
    if not configured_company:
        configured_company = frappe.defaults.get_global_default("company")

    currency = get_company_currency(configured_company)
    if not currency:
        return None, None, configured_company

    if settings and settings.company and company and settings.company != company:
        # v1 settings apply to one company only. Never compare another company's
        # base-currency amount with this company's threshold.
        return None, None, configured_company

    threshold = (
        flt(settings.high_value_quotation_threshold)
        if settings and settings.high_value_quotation_threshold is not None
        else DEFAULT_HIGH_VALUE_THRESHOLD
    )
    return threshold, currency, configured_company


def get_opportunity_signal_statuses():
    settings = get_settings()
    value = settings.opportunity_signal_statuses if settings else None
    statuses = tuple(line.strip() for line in (value or "").splitlines() if line.strip())
    return statuses or DEFAULT_OPPORTUNITY_SIGNAL_STATUSES


def get_lead_stale_days():
    settings = get_settings()
    value = settings.lead_stale_days if settings else None
    return max(1, int(value or DEFAULT_LEAD_STALE_DAYS))


def get_digest_time():
    settings = get_settings()
    value = settings.digest_time if settings else None
    return str(value or DEFAULT_DIGEST_TIME)[:8]


def is_digest_enabled():
    settings = get_settings()
    return bool(settings.enable_digest) if settings else True


def get_additional_digest_recipients():
    settings = get_settings()
    if not settings:
        return []

    recipients = []
    for row in settings.additional_digest_recipients or []:
        if not row.enabled or not row.user:
            continue
        user = frappe.db.get_value("User", row.user, ["enabled", "user_type"], as_dict=True)
        if user and user.enabled and user.user_type == "System User":
            recipients.append(row.user)
    return sorted(set(recipients))


def format_currency(amount, currency):
    """Format money with the ISO currency; never assume a rupee symbol."""
    if not currency:
        return None
    return frappe.utils.fmt_money(amount, currency=currency)
