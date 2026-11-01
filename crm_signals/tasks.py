"""Permission-aware, site-local CRM Signals digest with per-recipient queue tracking."""

import html
import json
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import frappe

from crm_signals.settings import get_signal_settings, parse_recipients

MAX_EXPIRING_QUOTATIONS = 100


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


def _dashboard_count_field():
    """Use aggregate syntax compatible with the supported Frappe major versions."""
    from crm_signals.api import _dashboard_aggregate_field

    return _dashboard_aggregate_field("COUNT", "name", "total")


def _get_stale_lead_count(stale_before):
    """Count stale Leads using the current recipient's permission context."""
    try:
        if not frappe.db.exists("DocType", "Lead"):
            return None
        meta = frappe.get_meta("Lead")
        if not meta.has_field("modified"):
            return None
        rows = frappe.get_list(
            "Lead",
            fields=[_dashboard_count_field()],
            filters={"modified": ["<", stale_before]},
            limit_page_length=1,
        )
        return int((rows[0].get("total") if rows else 0) or 0)
    except Exception:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="CRM Signals digest could not read recipient-visible Leads",
        )
        return None


def _get_expiring_quotations(today):
    """Fetch only Quotations the current digest recipient can read."""
    try:
        if not frappe.db.exists("DocType", "Quotation"):
            return None
        meta = frappe.get_meta("Quotation")
        required_fields = ("valid_till", "docstatus", "status", "party_name", "grand_total", "currency")
        if not all(meta.has_field(field) for field in required_fields):
            return None
        return frappe.get_list(
            "Quotation",
            filters={"valid_till": today, "docstatus": 1, "status": "Open"},
            fields=["name", "party_name", "grand_total", "currency"],
            order_by="name asc",
            limit_page_length=MAX_EXPIRING_QUOTATIONS + 1,
        )
    except Exception:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="CRM Signals digest could not read recipient-visible Quotations",
        )
        return None


def _format_quote_amount(quotation):
    amount = float(quotation.grand_total or 0)
    currency = getattr(quotation, "currency", None)
    formatted = f"{amount:,.2f}"
    return f"{currency} {formatted}" if currency else formatted


def _render_digest(stale_lead_count, stale_days, quotations):
    stale_value = (
        str(stale_lead_count)
        if stale_lead_count is not None
        else "Unavailable (permission or source configuration)"
    )
    if quotations is None:
        quote_count = "Unavailable"
        quote_summary = "<p>Quotation data is unavailable for your user permissions or site configuration.</p>"
    else:
        truncated = len(quotations) > MAX_EXPIRING_QUOTATIONS
        displayed_quotations = quotations[:MAX_EXPIRING_QUOTATIONS]
        quote_count = (
            f"{MAX_EXPIRING_QUOTATIONS}+"
            if truncated
            else str(len(displayed_quotations))
        )
        quote_rows = "".join(
            "<li><b>{}</b>: {} ({})</li>".format(
                html.escape(quotation.party_name or "Unspecified party"),
                html.escape(_format_quote_amount(quotation)),
                html.escape(quotation.name),
            )
            for quotation in displayed_quotations
        )
        if truncated:
            quote_rows += (
                "<li>Additional quotations are not shown. "
                "Review the full list in ERPNext.</li>"
            )
        quote_summary = (
            f"<ul>{quote_rows}</ul>"
            if quote_rows
            else "<p>No quotations expiring today.</p>"
        )

    return f"""
    <div style="font-family: sans-serif; line-height: 1.5;">
        <h2>Daily CRM Signals Digest</h2>
        <p>Sales pipeline telemetry visible to your ERPNext user account:</p>
        <table style="border-collapse: collapse; width: 100%; max-width: 500px; margin-bottom: 20px;">
            <tr><td><b>Leads not modified in more than {stale_days} days</b></td><td>{stale_value}</td></tr>
            <tr><td><b>Quotations expiring today</b></td><td>{quote_count}</td></tr>
        </table>
        <h4>Expiring quotations</h4>
        {quote_summary}
    </div>
    """


def _build_recipient_digest(recipient, today, stale_before, stale_days):
    """Run every source query as the actual recipient, then restore scheduler identity."""
    original_user = frappe.session.user
    try:
        frappe.set_user(recipient)
        stale_leads = _get_stale_lead_count(stale_before)
        quotations = _get_expiring_quotations(today)
        return _render_digest(stale_leads, stale_days, quotations)
    finally:
        frappe.set_user(original_user)


def _queued_recipients_for_date(settings_doc, today):
    saved_date = str(settings_doc.get("last_digest_queued_date") or "")[:10]
    if saved_date != today.isoformat():
        return set()
    try:
        recipients = json.loads(settings_doc.get("last_digest_queued_recipients") or "[]")
        return set(recipients) if isinstance(recipients, list) else set()
    except (TypeError, ValueError):
        return set()


def send_daily_signals_digest():
    """Queue a separate permission-filtered digest for each recipient.

    Each recipient is recorded only after their Email Queue request and Settings
    marker are saved in the same transaction. A later scheduler run can retry
    recipients whose queue request failed without resending already queued mail.
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
    recipients = _resolve_digest_recipients(settings["digest_extra_recipients"])
    if not recipients:
        return {"status": "no_recipients", "date": today.isoformat()}

    queued_recipients = _queued_recipients_for_date(settings_doc, today)
    pending_recipients = [recipient for recipient in recipients if recipient not in queued_recipients]
    if not pending_recipients:
        return {"status": "already_queued", "date": today.isoformat()}

    stale_days = int(settings["lead_stale_days"])
    from frappe.utils import add_days

    stale_before = add_days(today.isoformat(), -stale_days)
    failed_recipients = []
    for recipient in pending_recipients:
        try:
            digest_html = _build_recipient_digest(
                recipient,
                today.isoformat(),
                stale_before,
                stale_days,
            )
            frappe.sendmail(
                recipients=[recipient],
                subject=f"Daily CRM Signals Digest — {today.isoformat()}",
                message=digest_html,
                delayed=True,
            )
            next_queued = queued_recipients | {recipient}
            settings_doc.last_digest_queued_date = today.isoformat()
            settings_doc.last_digest_queued_recipients = json.dumps(sorted(next_queued))
            settings_doc.last_digest_status = (
                f"Queued to {len(next_queued)} of {len(recipients)} enabled System User(s)"
            )
            settings_doc.save(ignore_permissions=True)
            frappe.db.commit()
            queued_recipients = next_queued
        except Exception:
            frappe.db.rollback()
            failed_recipients.append(recipient)
            try:
                frappe.log_error(
                    message=frappe.get_traceback(),
                    title=f"CRM Signals digest queue failed for {recipient}",
                )
            except Exception:
                pass
            settings_doc = frappe.get_single("CRM Signals Settings")

    return {
        "status": "queued" if not failed_recipients else "partial",
        "date": today.isoformat(),
        "recipient_count": len(queued_recipients),
        "failed_recipient_count": len(failed_recipients),
    }
