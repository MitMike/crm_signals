"""Permission-conscious recipient resolution for CRM Signal notifications."""

import hashlib

import frappe


def _recipient_token(user):
    """Stable, non-reversible token for a Frappe username/email."""
    return hashlib.sha256(user.strip().lower().encode("utf-8")).hexdigest()


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


def set_recipient_tokens(signal):
    """Persist hashed recipients so list permission queries need no SQL subqueries."""
    recipients = get_signal_recipients(signal)
    tokens = sorted({_recipient_token(user) for user in recipients})
    signal.recipient_tokens = "|" + "|".join(tokens) + "|" if tokens else ""
    return recipients


def notify_signal(signal, recipients=None):
    """Publish a minimal signal event only to related enabled users."""
    recipients = get_signal_recipients(signal) if recipients is None else recipients
    payload = {
        "name": signal.name,
        "signal_type": signal.signal_type,
        "priority": signal.priority,
        "message": signal.message,
        "lead": signal.lead,
        "customer": signal.customer,
    }
    for user in recipients:
        frappe.publish_realtime(
            event="crm_signal_received",
            message=payload,
            user=user,
            after_commit=True,
        )
