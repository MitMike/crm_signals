import os

import frappe


def prepare_e2e_sales_api_credentials():
    """Write ephemeral Sales User API credentials to a private runner file."""
    import json

    credential_path = os.environ.get("E2E_SALES_API_CREDENTIAL_FILE")
    if not credential_path:
        frappe.throw("E2E API credential file path must be supplied by CI")

    previous_user = frappe.session.user
    try:
        frappe.set_user("Administrator")
        from frappe.core.doctype.user.user import generate_keys

        credentials = generate_keys("e2e-sales-user@example.com")
        frappe.db.commit()

        descriptor = os.open(
            credential_path,
            os.O_WRONLY | os.O_TRUNC | os.O_CREAT,
            0o600,
        )
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            os.fchmod(handle.fileno(), 0o600)
            json.dump(credentials, handle)

        return {"credentials_written": True}
    finally:
        frappe.set_user(previous_user)

