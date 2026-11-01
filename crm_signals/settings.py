"""Validated, site-configurable CRM Signals behavior.

Settings are a singleton so the first release has one coherent site policy.
Per-company overrides can be added later without changing signal identity.
"""

import datetime
import re

import frappe

PRESETS = {
    "Balanced": {
        "enable_quotation_signals": 1,
        "quotation_threshold": 200000,
        "enable_opportunity_signals": 1,
        "opportunity_trigger_statuses": "Replied",
        "enable_daily_digest": 1,
        "lead_stale_days": 3,
        "digest_time": "08:30:00",
    },
    "Sales Focused": {
        "enable_quotation_signals": 1,
        "quotation_threshold": 100000,
        "enable_opportunity_signals": 1,
        "opportunity_trigger_statuses": "Replied",
        "enable_daily_digest": 1,
        "lead_stale_days": 2,
        "digest_time": "08:00:00",
    },
    "Executive": {
        "enable_quotation_signals": 1,
        "quotation_threshold": 500000,
        "enable_opportunity_signals": 1,
        "opportunity_trigger_statuses": "Replied",
        "enable_daily_digest": 1,
        "lead_stale_days": 5,
        "digest_time": "08:30:00",
    },
}

DEFAULTS = {
    "enabled": 0,
    "enable_external_ingestion": 0,
    "enable_quotation_signals": 1,
    "quotation_threshold": 200000,
    "threshold_currency": None,
    "enable_opportunity_signals": 1,
    "opportunity_trigger_statuses": "Replied",
    "enable_daily_digest": 1,
    "lead_stale_days": 3,
    "digest_time": "08:30:00",
    "digest_extra_recipients": "",
}


@frappe.whitelist()
def get_preset_values(preset: str) -> dict:
    """Return one starter profile to an authorized Settings administrator."""
    if not frappe.has_permission("CRM Signals Settings", "write"):
        frappe.throw(
            frappe._("Only System Managers can read CRM Signals preset values."),
            frappe.PermissionError,
        )
    if preset not in PRESETS:
        frappe.throw(
            frappe._("Unknown CRM Signals preset: {0}").format(preset),
            frappe.ValidationError,
        )
    return dict(PRESETS[preset])


def parse_statuses(value: str | None) -> list[str]:
    """Split newline/comma-separated status values and remove duplicates."""
    result = []
    seen = set()
    for item in re.split(r"[,\n\r]+", str(value or "")):
        status = item.strip()
        normalized = status.casefold()
        if status and normalized not in seen:
            result.append(status)
            seen.add(normalized)
    return result


def parse_recipients(value: str | None) -> list[str]:
    """Split the configured list of additional System User IDs/emails."""
    result = []
    seen = set()
    for item in re.split(r"[,;\n\r]+", str(value or "")):
        address = item.strip()
        normalized = address.casefold()
        if address and normalized not in seen:
            result.append(address)
            seen.add(normalized)
    return result


def get_company_default_currency(company: str | None = None) -> str | None:
    """Return the configured Company's currency; never assume INR."""
    company_name = company or frappe.db.get_single_value("Global Defaults", "default_company")
    if not company_name:
        return None
    return frappe.db.get_value("Company", company_name, "default_currency")


def get_signal_settings() -> dict:
    """Read the singleton and apply safe defaults for fields added over time."""
    values = dict(DEFAULTS)
    try:
        doc = frappe.get_single("CRM Signals Settings")
    except Exception as error:
        # Keep app upgrades safe when hooks run before the singleton is migrated.
        if error.__class__.__name__ == "DoesNotExistError":
            values["threshold_currency"] = get_company_default_currency()
            values["opportunity_trigger_statuses"] = parse_statuses(
                values["opportunity_trigger_statuses"]
            )
            values["digest_extra_recipients"] = parse_recipients(
                values["digest_extra_recipients"]
            )
            for fieldname in (
                "enabled",
                "enable_external_ingestion",
                "enable_quotation_signals",
                "enable_opportunity_signals",
                "enable_daily_digest",
            ):
                values[fieldname] = bool(values[fieldname])
            return values
        raise

    for fieldname in DEFAULTS:
        value = doc.get(fieldname)
        if value is not None and value != "":
            values[fieldname] = value
    company_currency = get_company_default_currency()
    if company_currency:
        values["threshold_currency"] = company_currency
    values["opportunity_trigger_statuses"] = parse_statuses(
        values["opportunity_trigger_statuses"]
    )
    values["digest_extra_recipients"] = parse_recipients(
        values["digest_extra_recipients"]
    )
    for fieldname in (
        "enabled",
        "enable_external_ingestion",
        "enable_quotation_signals",
        "enable_opportunity_signals",
        "enable_daily_digest",
    ):
        values[fieldname] = bool(values[fieldname])
    return values


def _parse_time(value) -> datetime.time:
    if isinstance(value, datetime.time):
        return value.replace(second=0, microsecond=0)
    return datetime.time.fromisoformat(str(value).strip()[:8]).replace(second=0, microsecond=0)


def validate_settings_document(doc) -> None:
    """Validate admin-entered settings and populate the Company currency."""
    if doc.quotation_threshold is None or float(doc.quotation_threshold) < 0:
        frappe.throw(frappe._("Quotation threshold must be zero or greater."), frappe.ValidationError)

    company_currency = get_company_default_currency()
    if company_currency:
        doc.threshold_currency = company_currency
    if doc.enable_quotation_signals and not doc.threshold_currency:
        frappe.throw(
            frappe._("Set a default Company currency before enabling quotation threshold alerts."),
            frappe.ValidationError,
        )

    statuses = parse_statuses(doc.opportunity_trigger_statuses)
    if doc.enable_opportunity_signals and not statuses:
        frappe.throw(
            frappe._("Enter at least one Opportunity status when Opportunity signals are enabled."),
            frappe.ValidationError,
        )
    if len(statuses) > 20:
        frappe.throw(frappe._("Configure no more than 20 Opportunity statuses."), frappe.ValidationError)

    stale_days = int(doc.lead_stale_days or 0)
    if not 1 <= stale_days <= 365:
        frappe.throw(frappe._("Lead stale window must be between 1 and 365 days."), frappe.ValidationError)

    try:
        _parse_time(doc.digest_time)
    except (TypeError, ValueError):
        frappe.throw(frappe._("Digest time must be a valid site-local time."), frappe.ValidationError)

    for recipient in parse_recipients(doc.digest_extra_recipients):
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", recipient):
            frappe.throw(
                frappe._("Additional digest recipient must be a valid System User email address: {0}").format(
                    recipient
                ),
                frappe.ValidationError,
            )
        user = frappe.db.get_value(
            "User",
            {"email": recipient},
            ["enabled", "user_type"],
            as_dict=True,
        )
        if not user:
            frappe.throw(
                frappe._("Additional digest recipient is not a registered User: {0}").format(
                    recipient
                ),
                frappe.ValidationError,
            )
        if not user.get("enabled") or user.get("user_type") != "System User":
            frappe.throw(
                frappe._("Additional digest recipient must be an enabled System User: {0}").format(
                    recipient
                ),
                frappe.ValidationError,
            )
