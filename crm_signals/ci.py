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
    """Verify the pinned Helpdesk v1.28.0 metric contract without reading ticket records."""
    required_fields = {
        "status_category": 0,
        "resolution_date": 0,
        "resolution_time": 0,
        "sla": 0,
        "agreement_status": 0,
    }
    for doctype in ("HD Ticket", "HD Service Level Agreement"):
        if not frappe.db.exists("DocType", doctype):
            frappe.throw(f"Pinned Helpdesk app did not install required DocType: {doctype}")

    ticket_meta = frappe.get_meta("HD Ticket")
    if not frappe.db.has_column("HD Ticket", "creation"):
        frappe.throw("HD Ticket is missing the standard creation timestamp column")

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

    # Exercise the real D3 aggregate path on the pinned Frappe/Helpdesk stack.
    # The API returns only aggregate metrics; no ticket rows or identifiers are emitted.
    from crm_signals.api import get_sales_compass_data

    # bench execute does not guarantee an Administrator session; make the
    # reference-stack smoke test's permission context explicit.
    frappe.set_user("Administrator")
    service_metrics = get_sales_compass_data().get("service", {})
    required_metrics = (
        "available",
        "backlog_available",
        "resolved_available",
        "resolution_time_available",
        "sla_available",
    )
    unavailable = [key for key in required_metrics if not service_metrics.get(key)]
    if unavailable:
        frappe.throw(
            "CRM Signals D3 aggregate smoke test failed; unavailable metrics: "
            + ", ".join(unavailable)
        )

    return {
        "status": "passed",
        "ticket_fields": sorted(required_fields),
        "field_permlevels": required_fields,
        "ticket_read_roles": {level: sorted(roles) for level, roles in expected_ticket_roles.items()},
        "sla_read_roles": sorted(expected_sla_roles),
        "aggregate_smoke_test": "passed",
        "sla_doctype": "HD Service Level Agreement",
    }


def _d3_ci_status_names():
    status_names = {}
    for category in ("Open", "Paused", "Resolved"):
        rows = frappe.get_all(
            "HD Ticket Status",
            filters={"category": category, "enabled": 1},
            pluck="name",
            order_by="name asc",
            limit_page_length=1,
        )
        if not rows:
            frappe.throw(
                f"Helpdesk has no enabled HD Ticket Status for category {category}"
            )
        status_names[category] = rows[0]
    return status_names


def _d3_ci_baseline_resolution_stats(period_start):
    from crm_signals.api import _dashboard_aggregate_field

    filters = {
        "resolution_date": [">=", period_start],
        "status_category": "Resolved",
        "resolution_time": [">", 0],
    }
    count_rows = frappe.get_list(
        "HD Ticket",
        fields=[_dashboard_aggregate_field("COUNT", "name", "total")],
        filters=filters,
        limit_page_length=1,
    )
    average_rows = frappe.get_list(
        "HD Ticket",
        fields=[
            _dashboard_aggregate_field(
                "AVG", "resolution_time", "average_resolution_seconds"
            )
        ],
        filters=filters,
        limit_page_length=1,
    )
    count = int((count_rows[0].get("total") if count_rows else 0) or 0)
    average_seconds = float(
        (
            average_rows[0].get("average_resolution_seconds")
            if average_rows
            else 0
        )
        or 0
    )
    return count, average_seconds


def _d3_ci_create_tickets(status_names, sla_name, now, ticket_names):
    fixtures = (
        ("Open", "Resolution Due", None, True),
        ("Open", None, None, False),
        ("Paused", "Paused", None, True),
        ("Resolved", "Fulfilled", 7200, True),
        ("Resolved", "Fulfilled", 1800, True),
        ("Resolved", "Failed", 3600, True),
    )
    previous_initial_sync = getattr(frappe.flags, "initial_sync", False)
    frappe.flags.initial_sync = True
    try:
        for index, (category, agreement_status, resolution_seconds, has_sla) in enumerate(
            fixtures, start=1
        ):
            ticket = frappe.get_doc(
                {
                    "doctype": "HD Ticket",
                    "subject": f"CRM Signals CI D3 aggregate fixture {index}",
                }
            ).insert(ignore_permissions=True)
            ticket_names.append(ticket.name)
            frappe.db.set_value(
                "HD Ticket",
                ticket.name,
                {
                    "status": status_names[category],
                    "status_category": category,
                    "resolution_date": now if category == "Resolved" else None,
                    "resolution_time": resolution_seconds,
                    "sla": sla_name if has_sla else None,
                    "agreement_status": agreement_status,
                },
            )
    finally:
        frappe.flags.initial_sync = previous_initial_sync


def _d3_ci_assert_metrics(actual, baseline, baseline_resolution_count, baseline_average_seconds):
    expected_metrics = {
        "created_last_30_days": int(baseline["created_last_30_days"] or 0) + 6,
        "open_backlog": int(baseline["open_backlog"] or 0) + 2,
        "paused_backlog": int(baseline["paused_backlog"] or 0) + 1,
        "resolved_last_30_days": int(baseline["resolved_last_30_days"] or 0) + 3,
        "sla_eligible": int(baseline["sla_eligible"] or 0) + 3,
        "sla_fulfilled": int(baseline["sla_fulfilled"] or 0) + 2,
        "sla_failed": int(baseline["sla_failed"] or 0) + 1,
        "sla_unconfigured": int(baseline["sla_unconfigured"] or 0) + 1,
    }
    mismatches = [
        f"{key}: expected {expected}, found {actual.get(key)}"
        for key, expected in expected_metrics.items()
        if actual.get(key) != expected
    ]

    expected_average_hours = round(
        (
            baseline_average_seconds * baseline_resolution_count
            + 7200
            + 1800
            + 3600
        )
        / (baseline_resolution_count + 3)
        / 3600,
        2,
    )
    if actual.get("average_resolution_hours") != expected_average_hours:
        mismatches.append(
            "average_resolution_hours: "
            f"expected {expected_average_hours}, found "
            f"{actual.get('average_resolution_hours')}"
        )

    expected_compliance = round(
        (int(baseline["sla_fulfilled"] or 0) + 2)
        * 100
        / (int(baseline["sla_eligible"] or 0) + 3),
        1,
    )
    if actual.get("sla_compliance_percent") != expected_compliance:
        mismatches.append(
            "sla_compliance_percent: "
            f"expected {expected_compliance}, found "
            f"{actual.get('sla_compliance_percent')}"
        )

    required_available = (
        "available",
        "backlog_available",
        "resolved_available",
        "resolution_time_available",
        "sla_available",
    )
    mismatches.extend(
        f"{key} is unavailable"
        for key in required_available
        if not actual.get(key)
    )
    if mismatches:
        frappe.throw(
            "D3 synthetic aggregate fixture failed: " + "; ".join(mismatches)
        )

    return {
        "expected_deltas": expected_metrics,
        "average_resolution_hours": expected_average_hours,
        "sla_compliance_percent": expected_compliance,
    }


def verify_helpdesk_aggregate_fixture():
    """Verify D3 aggregate values against six disposable real HD Ticket documents.

    SLA outcomes are synthetic field values for the aggregate contract only;
    this does not simulate the Helpdesk SLA engine or approve a site calendar.
    """
    from frappe.utils import add_days, now_datetime, nowdate

    from crm_signals.api import get_sales_compass_data

    previous_user = frappe.session.user
    ticket_names = []
    try:
        frappe.set_user("Administrator")
        period_start = add_days(nowdate(), -30)
        baseline = get_sales_compass_data().get("service", {})
        if not baseline.get("available"):
            frappe.throw("D3 baseline metrics are unavailable before the fixture")

        baseline_resolution_count, baseline_average_seconds = (
            _d3_ci_baseline_resolution_stats(period_start)
        )
        sla_name = (
            frappe.db.get_value(
                "HD Service Level Agreement", {"enabled": 1}, "name"
            )
            or "CRM-Signals-CI-Synthetic-SLA"
        )
        _d3_ci_create_tickets(
            _d3_ci_status_names(), sla_name, now_datetime(), ticket_names
        )
        frappe.db.commit()

        actual = get_sales_compass_data().get("service", {})
        summary = _d3_ci_assert_metrics(
            actual,
            baseline,
            baseline_resolution_count,
            baseline_average_seconds,
        )
        return {
            "status": "passed",
            "synthetic_tickets": len(ticket_names),
            "sla_engine_tested": False,
            **summary,
        }
    finally:
        try:
            if ticket_names:
                placeholders = ", ".join(["%s"] * len(ticket_names))
                frappe.db.sql(
                    f"DELETE FROM `tabHD Ticket` WHERE name IN ({placeholders})",
                    tuple(ticket_names),
                )
                frappe.db.commit()
        finally:
            frappe.set_user(previous_user)


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
