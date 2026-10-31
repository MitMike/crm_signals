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
