"""Permission-conscious recipient resolution for CRM Signal notifications."""

import frappe


def get_signal_recipients(signal):
    """Return enabled document owners and active assignees for a signal."""
    candidate_links = {}
    linked = []
    if signal.lead:
        linked.append(("Lead", signal.lead))
    if signal.customer:
        linked.append(("Customer", signal.customer))

    for doctype, name in linked:
        owner = frappe.db.get_value(doctype, name, "owner")
        if owner:
            candidate_links.setdefault(owner, set()).add((doctype, name))
        assignments = frappe.get_all(
            "ToDo",
            filters={
                "reference_type": doctype,
                "reference_name": name,
                "status": ["not in", ["Cancelled", "Closed"]],
            },
            pluck="allocated_to",
        )
        for user in assignments:
            if user:
                candidate_links.setdefault(user, set()).add((doctype, name))

    if not candidate_links:
        return []

    enabled = frappe.get_all(
        "User",
        filters={
            "name": ["in", sorted(candidate_links)],
            "enabled": 1,
            "user_type": "System User",
        },
        pluck="name",
    )
    eligible = []
    for user in sorted(set(enabled)):
        for doctype, name in candidate_links.get(user, set()):
            try:
                can_read_party = frappe.has_permission(
                    doctype, ptype="read", doc=name, user=user
                )
                can_read_signal = frappe.has_permission(
                    "CRM Signal", ptype="read", doc=signal.name, user=user
                )
            except Exception:
                can_read_party = False
                can_read_signal = False
            if can_read_party and can_read_signal:
                eligible.append(user)
                break
    return eligible


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
