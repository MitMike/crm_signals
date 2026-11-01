"""Test-only bootstrap helpers for the clean Bench CI site.

These functions are invoked explicitly by GitHub Actions through bench execute.
They are not whitelisted and are not part of the application runtime.
"""

import os

import frappe
from frappe.utils.password import update_password


def _ensure_system_user(email, first_name, role, password):
    if not frappe.db.exists("Role", role):
        frappe.get_doc({"doctype": "Role", "role_name": role}).insert(ignore_permissions=True)

    if not frappe.db.exists("User", email):
        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": email,
                "first_name": first_name,
                "enabled": 1,
                "user_type": "System User",
                "send_welcome_email": 0,
                "roles": [{"role": role}],
            }
        )
        user.flags.no_welcome_mail = True
        user.insert(ignore_permissions=True)
    else:
        user = frappe.get_doc("User", email)
        user.enabled = 1
        user.user_type = "System User"
        user.set("roles", [{"role": role}])
        user.save(ignore_permissions=True)

    update_password(email, password)


def prepare_e2e_site():
    """Complete first-run ERPNext setup and create deterministic E2E users."""
    if not frappe.is_setup_complete():
        from frappe.desk.page.setup_wizard.setup_wizard import setup_complete

        result = setup_complete(
            {
                "language": "English",
                "timezone": "Asia/Kolkata",
                "country": "India",
                "currency": "INR",
                "enable_telemetry": 0,
                "fy_start_date": "2026-04-01",
                "fy_end_date": "2027-03-31",
                "company_name": "CRM Signals CI Company",
                "company_abbr": "CSCI",
                "chart_of_accounts": "Standard",
                "domain": "Services",
            }
        )
        if result and result.get("status") != "ok":
            frappe.throw("ERPNext Setup Wizard did not complete successfully")

    if not frappe.is_setup_complete():
        frappe.throw("ERPNext Setup Wizard still reports an incomplete site")

    sales_password = os.environ.get("E2E_SALES_PASSWORD")
    employee_password = os.environ.get("E2E_EMPLOYEE_PASSWORD")
    if not sales_password or not employee_password:
        frappe.throw("E2E user passwords must be supplied by the CI environment")

    _ensure_system_user(
        "e2e-sales-user@example.com", "E2E Sales User", "Sales User", sales_password
    )
    _ensure_system_user(
        "e2e-employee@example.com", "E2E Employee", "Employee", employee_password
    )

    frappe.db.commit()
    return {
        "setup_complete": True,
        "company": "CRM Signals CI Company",
        "users": ["e2e-sales-user@example.com", "e2e-employee@example.com"],
    }


LEGACY_SIGNAL_MESSAGES = (
    "CRM Signals upgrade fixture: legacy row one",
    "CRM Signals upgrade fixture: legacy row two",
)


def prepare_upgrade_site():
    """Create pre-idempotency records, then restore the legacy table shape.

    This runs only in the disposable CI site. It models an installation whose
    CRM Signal table predates source-event identity fields while retaining real
    historical rows and their original document names.
    """
    for message in LEGACY_SIGNAL_MESSAGES:
        if not frappe.db.exists("CRM Signal", {"message": message}):
            frappe.get_doc(
                {
                    "doctype": "CRM Signal",
                    "signal_type": "Website Visit",
                    "priority": "Medium",
                    "message": message,
                }
            ).insert(ignore_permissions=True)
    frappe.db.commit()

    # Revert both physical columns and field metadata to the pre-feature
    # shape. The following bench migrate must recreate DocFields and columns
    # from the current app's JSON definition. Dropping the unique-key column
    # also removes its database index.
    legacy_fields = (
        "source_doctype",
        "source_name",
        "source_event_id",
        "source_event_key",
    )
    for fieldname in legacy_fields:
        if frappe.db.has_column("CRM Signal", fieldname):
            frappe.db.sql(
                f"ALTER TABLE `tabCRM Signal` DROP COLUMN `{fieldname}`"
            )
    frappe.db.sql(
        "DELETE FROM `tabDocField` "
        "WHERE parent = %s AND fieldname IN (%s, %s, %s, %s)",
        ("CRM Signal", *legacy_fields),
    )
    # Frappe skips unchanged DocType JSON when its stored modified timestamp
    # is newer than the file. Rewind it so migrate performs the real JSON sync.
    # Frappe stores a migration_hash for DocTypes and skips importing the JSON
    # when that hash matches the current file, regardless of the modified time.
    # Clear it to model an older installed DocType definition and force sync.
    frappe.db.sql(
        "UPDATE `tabDocType` SET modified = %s, migration_hash = NULL WHERE name = %s",
        ("2000-01-01 00:00:00", "CRM Signal"),
    )
    frappe.clear_cache(doctype="CRM Signal")
    frappe.db.commit()
    return {
        "legacy_records": len(LEGACY_SIGNAL_MESSAGES),
        "schema": "pre-source-event-identity",
    }


def verify_helpdesk_schema():
    """Verify the pinned Helpdesk metric contract without reading ticket records."""
    required_fields = {
        "status_category": 7,
        "resolution_date": 7,
        "resolution_time": 7,
        "sla": 7,
        "agreement_status": 8,
    }
    for doctype in ("HD Ticket", "HD Service Level Agreement"):
        if not frappe.db.exists("DocType", doctype):
            frappe.throw(f"Pinned Helpdesk app did not install required DocType: {doctype}")

    ticket_meta = frappe.get_meta("HD Ticket")
    if not ticket_meta.has_field("creation"):
        frappe.throw("HD Ticket is missing the standard creation timestamp")

    mismatches = []
    for fieldname, expected_permlevel in required_fields.items():
        field = ticket_meta.get_field(fieldname)
        if not field:
            mismatches.append(f"{fieldname}: missing")
            continue
        actual_permlevel = int(field.permlevel or 0)
        if actual_permlevel != expected_permlevel:
            mismatches.append(
                f"{fieldname}: expected permlevel {expected_permlevel}, found {actual_permlevel}"
            )
    if mismatches:
        frappe.throw("Pinned Helpdesk field contract changed: " + "; ".join(mismatches))

    permitted_fields = set(
        ticket_meta.get_permitted_fieldnames(
            user="Administrator",
            permission_type="read",
        )
    )
    missing_permitted = sorted(set(required_fields) - permitted_fields)
    if missing_permitted:
        frappe.throw(
            "Administrator cannot read required HD Ticket fields: " + ", ".join(missing_permitted)
        )

    sla_meta = frappe.get_meta("HD Service Level Agreement")
    if not sla_meta.has_field("service_level"):
        frappe.throw("HD Service Level Agreement is missing service_level")

    def read_roles(meta, permlevel):
        return {
            permission.role
            for permission in meta.permissions
            if permission.read and int(permission.permlevel or 0) == permlevel
        }

    expected_ticket_roles = {
        0: {"System Manager", "Agent", "Agent Manager", "HD Customer", "HD Customer Manager"},
        7: {"System Manager", "Agent", "Agent Manager", "HD Customer", "HD Customer Manager"},
        8: {"System Manager", "Agent", "Agent Manager"},
    }
    for permlevel, expected_roles in expected_ticket_roles.items():
        actual_roles = read_roles(ticket_meta, permlevel)
        if actual_roles != expected_roles:
            frappe.throw(
                f"HD Ticket read roles changed at permlevel {permlevel}: "
                f"expected {sorted(expected_roles)}, found {sorted(actual_roles)}"
            )

    expected_sla_roles = {"System Manager", "Agent Manager"}
    actual_sla_roles = read_roles(sla_meta, 0)
    if actual_sla_roles != expected_sla_roles:
        frappe.throw(
            "HD Service Level Agreement read roles changed: "
            f"expected {sorted(expected_sla_roles)}, found {sorted(actual_sla_roles)}"
        )

    return {
        "status": "passed",
        "ticket_fields": sorted(required_fields),
        "field_permlevels": required_fields,
        "ticket_read_roles": {level: sorted(roles) for level, roles in expected_ticket_roles.items()},
        "sla_read_roles": sorted(expected_sla_roles),
        "sla_doctype": "HD Service Level Agreement",
    }


def verify_upgrade_site():
    """Assert migrate restored new fields without losing legacy signal rows."""
    missing = [
        fieldname
        for fieldname in (
            "source_doctype",
            "source_name",
            "source_event_id",
            "source_event_key",
        )
        if not frappe.db.has_column("CRM Signal", fieldname)
    ]
    if missing:
        frappe.throw("CRM Signal upgrade did not restore fields: " + ", ".join(missing))

    for message in LEGACY_SIGNAL_MESSAGES:
        rows = frappe.get_all(
            "CRM Signal",
            filters={"message": message},
            fields=["name", "source_event_key"],
        )
        if len(rows) != 1:
            frappe.throw(f"Expected exactly one preserved legacy CRM Signal for: {message}")
        if rows[0].source_event_key:
            frappe.throw(f"Legacy CRM Signal unexpectedly acquired an event key: {rows[0].name}")

    return {"status": "passed", "preserved_legacy_records": len(LEGACY_SIGNAL_MESSAGES)}
