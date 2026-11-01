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
    frappe.clear_cache(doctype="CRM Signal")
    frappe.db.commit()
    return {\n        "legacy_records": len(LEGACY_SIGNAL_MESSAGES),\n        "schema": "pre-source-event-identity",\n    }


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
