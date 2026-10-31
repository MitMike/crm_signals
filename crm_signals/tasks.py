"""Site-local, configurable and date-idempotent CRM Signals digest."""

import html
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import frappe

from crm_signals.settings import get_signal_settings, parse_recipients


def _site_now():
    timezone = frappe.db.get_single_value("System Settings", "time_zone") or "UTC"
    try:
        return datetime.now(ZoneInfo(timezone))
    except ZoneInfoNotFoundError:
        frappe.throw(f"Invalid System Settings timezone: {timezone}")


def _resolve_digest_recipients(extra_recipients):
    """Return enabled System Users with Sales Manager role or explicit inclusion."""
    role_users = frappe.get_all(
        "Has Role",
        filters={"role": "Sales Manager", "parenttype": "User"},
        pluck="parent",
    )
    candidates = set(user for user in role_users if user and user != "Guest")

    for address in parse_recipients("\n".join(extra_recipients or [])):
        user = frappe.db.get_value("User", address, "name")
        if not user:
            user = frappe.db.get_value("User", {"email": address}, "name")
        if user and user != "Guest":
            candidates.add(user)

    if not candidates:
        return []
    enabled = frappe.get_all(
        "User",
        filters={
            "name": ["in", sorted(candidates)],
            "enabled": 1,
            "user_type": "System User",
        },
        pluck="name",
    )
    return sorted(set(enabled))


def _get_expiring_quotations(today):
    meta = frappe.get_meta("Quotation")
    fields = ["name", "party_name", "grand_total"]
    if meta.has_field("currency"):
        fields.append("currency")
    return frappe.get_all(
        "Quotation",
        filters={"valid_till": today, "docstatus": 1, "status": "Open"},
        fields=fields,
        order_by="valid_till asc",
    )


def _format_quote_amount(quotation):
    amount = float(quotation.grand_total or 0)
    currency = getattr(quotation, "currency", None)
    formatted = f"{amount:,.2f}"
    return f"{currency} {formatted}" if currency else formatted


def _render_digest(stale_lead_count, stale_days, quotations):
    quote_rows = "".join(
        "<li><b>{}</b>: {} ({})</li>".format(
            html.escape(quotation.party_name or "Unspecified party"),
            html.escape(_format_quote_amount(quotation)),
            html.escape(quotation.name),
        )
        for quotation in quotations
    )
    quote_summary = (
        f"<ul>{quote_rows}</ul>"
        if quote_rows
        else "<p>No quotations expiring today.</p>"
    )
    return f"""
    <div style="font-family: sans-serif; line-height: 1.5;">
        <h2>Daily CRM Signals Digest</h2>
        <p>Sales pipeline telemetry requiring attention:</p>
        <table style="border-collapse: collapse; width: 100%; max-width: 500px; margin-bottom: 20px;">
            <tr><td><b>Leads not modified in more than {stale_days} days</b></td><td>{stale_lead_count}</td></tr>
            <tr><td><b>Quotations expiring today</b></td><td>{len(quotations)}</td></tr>
        </table>
        <h4>Expiring quotations</h4>
        {quote_summary}
    </div>
    """


def send_daily_signals_digest():
    """Queue at most one daily digest per site-local date.

    The queue record and singleton date marker are saved in the same Frappe
    transaction. A sendmail exception leaves the marker untouched for retry.
    """
    settings = get_signal_settings()
    if not settings["enabled"] or not settings["enable_daily_digest"]:
        return {"status": "disabled"}

    site_now = _site_now()
    today = site_now.date()
    configured_time = settings["digest_time"]
    digest_hour, digest_minute = (int(part) for part in str(configured_time).split(":")[:2])
    if (site_now.hour, site_now.minute) < (digest_hour, digest_minute):
        return {"status": "not_due", "date": today.isoformat()}

    settings_doc = frappe.get_single("CRM Signals Settings")
    last_queued_date = str(settings_doc.get("last_digest_queued_date") or "")[:10]
    if last_queued_date == today.isoformat():
        return {"status": "already_queued", "date": today.isoformat()}

    recipients = _resolve_digest_recipients(settings["digest_extra_recipients"])
    if not recipients:
        return {"status": "no_recipients", "date": today.isoformat()}

    stale_days = int(settings["lead_stale_days"])
    from frappe.utils import add_days

    stale_before = add_days(today.isoformat(), -stale_days)
    stale_leads = frappe.db.count("Lead", {"modified": ["<", stale_before]})
    quotations = _get_expiring_quotations(today.isoformat())
    digest_html = _render_digest(stale_leads, stale_days, quotations)

    frappe.sendmail(
        recipients=recipients,
        subject=f"Daily CRM Signals Digest — {today.isoformat()}",
        message=digest_html,
        delayed=True,
    )
    settings_doc.last_digest_queued_date = today.isoformat()
    settings_doc.last_digest_status = f"Queued to {len(recipients)} enabled System User(s)"
    settings_doc.save(ignore_permissions=True)
    return {
        "status": "queued",
        "date": today.isoformat(),
        "recipient_count": len(recipients),
    }
