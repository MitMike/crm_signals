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


def crm_signal_query(user=None):
    """Filter CRM Signal list queries for non-manager users."""
    user = user or frappe.session.user
    if _has_manager_role(user):
        return ""

    escaped_user = frappe.db.escape(user)
    lead_match = f"""(`tabCRM Signal`.lead IN (
        SELECT `tabLead`.name FROM `tabLead`
        WHERE `tabLead`.owner = {escaped_user}
        UNION
        SELECT `tabToDo`.reference_name FROM `tabToDo`
        WHERE `tabToDo`.reference_type = 'Lead'
          AND `tabToDo`.allocated_to = {escaped_user}
          AND `tabToDo`.status NOT IN ('Cancelled', 'Closed')
    ))"""
    customer_match = f"""(`tabCRM Signal`.customer IN (
        SELECT `tabCustomer`.name FROM `tabCustomer`
        WHERE `tabCustomer`.owner = {escaped_user}
        UNION
        SELECT `tabToDo`.reference_name FROM `tabToDo`
        WHERE `tabToDo`.reference_type = 'Customer'
          AND `tabToDo`.allocated_to = {escaped_user}
          AND `tabToDo`.status NOT IN ('Cancelled', 'Closed')
    ))"""
    own_signal = f"(`tabCRM Signal`.owner = {escaped_user})"
    return f"({lead_match} OR {customer_match} OR {own_signal})"
