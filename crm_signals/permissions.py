"""Record-level access policy for CRM Signal documents."""

import frappe

MANAGER_ROLES = {"Sales Manager", "System Manager"}


def _has_manager_role(user):
    return bool(set(frappe.get_roles(user) or []) & MANAGER_ROLES)


def _field_value(doc, fieldname):
    if isinstance(doc, dict):
        return doc.get(fieldname)
    return getattr(doc, fieldname, None)


def _doctype_permission(permission_type, user):
    """Check role-level permission without invoking this document's row hook."""
    return bool(
        frappe.has_permission(
            "CRM Signal",
            ptype=permission_type,
            user=user,
        )
    )


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


def crm_signal_has_permission(
    doc,
    user=None,
    permission_type=None,
    ptype=None,
):
    """Enforce CRM Signal row access on Frappe v15 and v16.

    Frappe v15 passes `permission_type`; v16 passes `ptype` and requires
    permission hooks to return an explicit boolean. Role-level DocType
    permissions remain authoritative for every permission type.
    """
    user = user or frappe.session.user
    permission_type = ptype or permission_type

    if not permission_type or not _doctype_permission(permission_type, user):
        return False

    if _has_manager_role(user):
        return True

    links = []
    lead = _field_value(doc, "lead")
    customer = _field_value(doc, "customer")
    if lead:
        links.append(("Lead", lead))
    if customer:
        links.append(("Customer", customer))

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
        related_and_readable = _field_value(doc, "owner") == user

    if permission_type == "read":
        return bool(related_and_readable)

    if permission_type in {"write", "delete", "submit", "cancel"}:
        owns_related_party = any(
            frappe.db.get_value(doctype, name, "owner") == user
            for doctype, name in links
        )
        return bool(
            related_and_readable
            and (
                _field_value(doc, "owner") == user
                or owns_related_party
                or assigned
            )
        )

    # Create, share, export, print and other actions are governed by the
    # role-level DocType permission checked above.
    return True


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

    escaped_user = frappe.db.escape(user)
    clauses = [
        f"(`tabCRM Signal`.owner = {escaped_user} AND "
        "`tabCRM Signal`.lead IS NULL AND `tabCRM Signal`.customer IS NULL)"
    ]
    for doctype, fieldname in (("Lead", "lead"), ("Customer", "customer")):
        try:
            names = _get_visible_party_names(doctype, user)
        except frappe.PermissionError:
            names = []
        if names:
            escaped_names = ", ".join(frappe.db.escape(name) for name in names)
            clauses.append(f"(`tabCRM Signal`.`{fieldname}` IN ({escaped_names}))")

    return "(" + " OR ".join(clauses) + ")"
