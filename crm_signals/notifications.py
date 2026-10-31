"""Permission-conscious recipient resolution for CRM Signal notifications."""

import frappe


def get_signal_recipients(signal):
    """Return enabled document owners and active assignees for a signal."""
    recipients = set()
    linked = []
    if signal.lead:
        linked.append(("Lead", signal.lead))
    if signal.customer:
        linked.append(("Customer", signal.customer))

    for doctype, name in linked:
        owner = frappe.db.get_value(doctype, name, "owner")
        if owner:
            recipients.add(owner)
        assignments = frappe.get_all(
            "ToDo",
            filters={
                "reference_type": doctype,
                "reference_name": name,
                "status": ["not in", ["Cancelled", "Closed"]],
            },
            pluck="allocated_to",
        )
        recipients.update(user for user in assignments if user)

    if not recipients:
        return []

    enabled = frappe.get_all(
        "User",
        filters={"name": ["in", sorted(recipients)], "enabled": 1, "user_type": "System User"},
        pluck="name",
    )
    return sorted(set(enabled))


def notify_signal(signal):
    """Publish to each related user; isolate one failed recipient from all others."""
    payload = {
        "name": signal.name,
        "signal_type": signal.signal_type,
        "priority": signal.priority,
        "message": signal.message,
        "lead": signal.lead,
        "customer": signal.customer,
    }
    sent = 0
    failed = 0
    for user in get_signal_recipients(signal):
        try:
            frappe.publish_realtime(
                event="crm_signal_received",
                message=payload,
                user=user,
                after_commit=True,
            )
            sent += 1
        except Exception:
            failed += 1
            try:
                frappe.log_error(
                    message=frappe.get_traceback(),
                    title=f"CRM Signal notification failed for {user}",
                )
            except Exception:
                pass
    return {"sent": sent, "failed": failed}
