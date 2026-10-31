"""Record-level access policy for CRM Signal documents."""

import hashlib

import frappe

MANAGER_ROLES = {"Sales Manager", "System Manager"}


def _has_manager_role(user):
    return bool(set(frappe.get_roles(user) or []) & MANAGER_ROLES)


def _recipient_token(user):
    return hashlib.sha256(user.strip().lower().encode("utf-8")).hexdigest()


def _has_recipient_token(doc, user):
    tokens = getattr(doc, "recipient_tokens", "") or ""
    return f"|{_recipient_token(user)}|" in tokens


def _is_assigned(doctype, name, user):
    if not doctype or not name or not user:
        return False
    return bool(
        frappe.db.exists(
            "ToDo",
            {
                "reference_type": doctype,
                "reference_name": name,
                "allocated_to": user,
                "status": ["not in", ["Cancelled", "Closed"]],
            },
        )
    )


def crm_signal_has_permission(doc, user=None, permission_type=None):
    """Restrict Sales User access to related, owned/assigned CRM records."""
    user = user or frappe.session.user
    if _has_manager_role(user):
        return None

    recipient = _has_recipient_token(doc, user)
    links = []
    if doc.lead:
        links.append(("Lead", doc.lead))
    if doc.customer:
        links.append(("Customer", doc.customer))

    related_and_readable = False
    assigned = False
    for doctype, name in links:
        parent_owner = frappe.db.get_value(doctype, name, "owner")
        is_assigned = _is_assigned(doctype, name, user)
        is_related = parent_owner == user or is_assigned or recipient
        assigned = assigned or is_assigned
        if is_related and frappe.has_permission(
            doctype, ptype="read", doc=name, user=user
        ):
            related_and_readable = True

    if not links:
        related_and_readable = doc.owner == user or recipient

    if permission_type == "read":
        return bool(related_and_readable)
    if permission_type in {"write", "delete", "submit", "cancel"}:
        owns_related_party = any(
            frappe.db.get_value(doctype, name, "owner") == user
            for doctype, name in links
        )
        return bool(
            related_and_readable
            and (doc.owner == user or owns_related_party or assigned or recipient)
        )
    return None


def crm_signal_query(user=None):
    """Filter list queries by owner or the recipient token stored on each signal.

    The generated condition contains no subqueries or UNION, which keeps it
    compatible with Frappe v16's generated-list-query validation.
    """
    user = user or frappe.session.user
    if _has_manager_role(user):
        return ""

    escaped_user = frappe.db.escape(user)
    escaped_token_pattern = frappe.db.escape(f"%|{_recipient_token(user)}|%")
    own_signal = f"(`tabCRM Signal`.owner = {escaped_user})"
    recipient_signal = (
        f"(`tabCRM Signal`.recipient_tokens LIKE {escaped_token_pattern})"
    )
    return f"({own_signal} OR {recipient_signal})"
