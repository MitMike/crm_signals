"""Record-level access policy for CRM Signal documents."""

import frappe

MANAGER_ROLES = {"Sales Manager", "System Manager"}


def _has_manager_role(user):
    return bool(set(frappe.get_roles(user) or []) & MANAGER_ROLES)


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
        is_related = parent_owner == user or is_assigned
        assigned = assigned or is_assigned
        if is_related and frappe.has_permission(
            doctype, ptype="read", doc=name, user=user
        ):
            related_and_readable = True

    if not links:
        related_and_readable = doc.owner == user

    if permission_type == "read":
        return bool(related_and_readable)
    if permission_type in {"write", "delete", "submit", "cancel"}:
        owns_related_party = any(
            frappe.db.get_value(doctype, name, "owner") == user
            for doctype, name in links
        )
        return bool(related_and_readable and (doc.owner == user or owns_related_party or assigned))
    return None


def _get_visible_party_names(doctype, user):
    """Return only owned/assigned party records the current user can read."""
    owned = frappe.get_list(
        doctype,
        filters={"owner": user},
        pluck="name",
        limit_page_length=0,
    )

    assigned_names = frappe.get_all(
        "ToDo",
        filters={
            "reference_type": doctype,
            "allocated_to": user,
            "status": ["not in", ["Cancelled", "Closed"]],
        },
        pluck="reference_name",
    )
    assigned = []
    if assigned_names:
        assigned = frappe.get_list(
            doctype,
            filters={"name": ["in", sorted(set(assigned_names))]},
            pluck="name",
            limit_page_length=0,
        )

    return sorted(set(owned or []) | set(assigned or []))


def crm_signal_query(user=None):
    """Build a simple list filter from currently readable owned/assigned records.

    The resulting SQL contains only literal IN lists, not nested query constructs,
    and party name lookup uses permission-aware get_list calls.
    """
    user = user or frappe.session.user
    if _has_manager_role(user):
        return ""

    clauses = [f"(`tabCRM Signal`.owner = {frappe.db.escape(user)})"]
    for doctype, fieldname in (("Lead", "lead"), ("Customer", "customer")):
        try:
            names = _get_visible_party_names(doctype, user)
        except frappe.PermissionError:
            names = []
        if names:
            escaped_names = ", ".join(frappe.db.escape(name) for name in names)
            clauses.append(f"(`tabCRM Signal`.`{fieldname}` IN ({escaped_names}))")

    return "(" + " OR ".join(clauses) + ")"
