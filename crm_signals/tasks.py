import html

import frappe
from frappe.utils import add_days, nowdate


def send_daily_signals_digest():
    """Email Sales Managers a conservative daily CRM attention digest.

    Lead status semantics and inactivity definition must be confirmed against
    the target ERPNext site's schema before production sign-off.
    """
    three_days_ago = add_days(nowdate(), -3)

    # Do not guess at a status value. This metric currently means records not
    # modified in the last 3 days; it does not necessarily mean stalled deals.
    stalled_leads = frappe.db.count("Lead", {
        "modified": ["<", three_days_ago],
    })

    expiring_quotes = frappe.get_all(
        "Quotation",
        filters={"valid_till": nowdate(), "docstatus": 1, "status": "Open"},
        fields=["name", "party_name", "grand_total"],
        order_by="valid_till asc",
    )

    rows = "".join(
        "<li><b>{}</b>: ₹{:,.2f} ({})</li>".format(
            html.escape(q.party_name or "Unspecified party"),
            q.grand_total or 0,
            html.escape(q.name),
        )
        for q in expiring_quotes
    )
    quote_summary = f"<ul>{rows}</ul>" if rows else "<p>No quotations expiring today.</p>"

    digest_html = f"""
    <div style="font-family: sans-serif; line-height: 1.5;">
        <h2>Daily CRM Signals Digest</h2>
        <p>Sales pipeline telemetry requiring attention:</p>
        <table style="border-collapse: collapse; width: 100%; max-width: 500px; margin-bottom: 20px;">
            <tr><td><b>Leads not modified in more than 3 days</b></td><td>{stalled_leads}</td></tr>
            <tr><td><b>Quotations expiring today</b></td><td>{len(expiring_quotes)}</td></tr>
        </table>
        <h4>Expiring quotations</h4>
        {quote_summary}
    </div>
    """

    recipients = frappe.get_all(
        "Has Role",
        filters={"role": "Sales Manager", "parenttype": "User"},
        pluck="parent",
    )
    recipients = sorted({user for user in recipients if user and user != "Guest"})
    if recipients:
        frappe.sendmail(
            recipients=recipients,
            subject=f"Daily CRM Signals Digest — {nowdate()}",
            message=digest_html,
            delayed=True,
        )
