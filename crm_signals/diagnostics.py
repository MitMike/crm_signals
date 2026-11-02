"""Read-only target-site inventory for operators using bench execute.

This module intentionally exposes no whitelisted HTTP method. The report reads
configuration and DocType metadata only; it never reads business-document rows.
"""

import importlib

import frappe

TARGET_ROLES = ("Sales User", "Sales Manager", "System Manager")
PREFLIGHT_DOCTYPES = {
    "CRM Signal": ("signal_type", "priority", "lead", "customer", "source_doctype", "source_name", "source_event_id"),
    "Lead": ("status",),
    "Customer": ("customer_name",),
    "Opportunity": ("status",),
    "Quotation": ("quotation_to", "party_name", "status", "grand_total", "currency"),
    "Sales Invoice": ("is_return", "docstatus", "currency", "grand_total", "outstanding_amount", "is_pos", "paid_amount", "posting_date", "due_date", "customer"),
    "Payment Entry": ("docstatus", "payment_type", "party_type", "party", "paid_amount", "received_amount", "posting_date", "paid_from_account_currency", "paid_to_account_currency"),
    "HD Ticket": (
        "status_category",
        "resolution_date",
        "resolution_time",
        "sla",
        "agreement_status",
    ),
    "HD Service Level Agreement": (),
}
WORKFLOW_DOCTYPES = {"Lead", "Opportunity"}


def _value(row, key, default=None):
    if isinstance(row, dict):
        return row.get(key, default)
    return getattr(row, key, default)


def _as_int(value, default=0):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return default


def _company_thresholds(companies, settings):
    """Describe effective thresholds without applying currency conversion."""
    overrides = {row["company"]: row for row in settings.get("company_thresholds", [])}
    result = []
    legacy_currency = settings.get("threshold_currency")
    legacy_amount = settings.get("quotation_threshold")
    for company in companies:
        name = company.get("name")
        currency = company.get("default_currency")
        override = overrides.get(name)
        if override:
            amount = override.get("quotation_threshold")
            configured_currency = override.get("currency")
            effective = bool(currency and configured_currency == currency and amount is not None)
            source = "company_override" if effective else "company_override_currency_mismatch"
        else:
            amount = legacy_amount
            configured_currency = legacy_currency
            source = "legacy_exact_currency" if currency and legacy_currency == currency else "suppressed_currency_mismatch"
            effective = source == "legacy_exact_currency"
        result.append(
            {
                "company": name,
                "base_currency": currency,
                "threshold_source": source,
                "threshold_amount": amount if effective else None,
                "threshold_currency": configured_currency,
                "effective": effective,
            }
        )
    return result


def _settings_summary(settings, companies):
    """Return operational settings only; deliberately omit recipient addresses."""
    return {
        "enabled": bool(settings.get("enabled")),
        "external_ingestion_enabled": bool(settings.get("enable_external_ingestion")),
        "quotation_signals_enabled": bool(settings.get("enable_quotation_signals")),
        "opportunity_signals_enabled": bool(settings.get("enable_opportunity_signals")),
        "daily_digest_enabled": bool(settings.get("enable_daily_digest")),
        "opportunity_trigger_statuses": list(settings.get("opportunity_trigger_statuses") or []),
        "lead_stale_days": _as_int(settings.get("lead_stale_days")),
        "digest_time": str(settings.get("digest_time") or ""),
        "company_thresholds": _company_thresholds(companies, settings),
    }


def _app_version(app):
    try:
        module = importlib.import_module(app)
    except Exception as error:
        return {"app": app, "version": None, "import_error": type(error).__name__}
    version = getattr(module, "__version__", None)
    return {"app": app, "version": str(version) if version else None}


def _field_summary(field):
    fieldname = _value(field, "fieldname")
    if not fieldname:
        return None
    fieldtype = _value(field, "fieldtype")
    summary = {
        "fieldname": fieldname,
        "label": _value(field, "label"),
        "fieldtype": fieldtype,
        "permlevel": _as_int(_value(field, "permlevel")),
    }
    if fieldtype == "Select":
        summary["options"] = [
            option for option in str(_value(field, "options") or "").splitlines() if option
        ]
    return summary


def _doctype_summary(doctype, required_fields=()):
    if not frappe.db.exists("DocType", doctype):
        return {
            "available": False,
            "fields": [],
            "required_fields": [{"fieldname": name, "present": False} for name in required_fields],
            "role_read_permissions": [],
        }
    meta = frappe.get_meta(doctype)
    fields = [_field_summary(field) for field in meta.fields]
    fields_by_name = {field["fieldname"]: field for field in fields if field}
    permissions = []
    for permission in getattr(meta, "permissions", []) or []:
        role = _value(permission, "role")
        if role in TARGET_ROLES:
            permissions.append(
                {
                    "role": role,
                    "read": bool(_as_int(_value(permission, "read"))),
                    "permlevel": _as_int(_value(permission, "permlevel")),
                }
            )
    return {
        "available": True,
        "module": getattr(meta, "module", None),
        "fields": [field for field in fields if field],
        "required_fields": [
            {
                "fieldname": name,
                "present": name in fields_by_name,
                "permlevel": fields_by_name[name]["permlevel"] if name in fields_by_name else None,
            }
            for name in required_fields
        ],
        "role_read_permissions": permissions,
        "permission_boundary": "static DocPerm only; not effective user access",
    }


def _workflow_summary():
    try:
        workflows = frappe.get_all(
            "Workflow",
            filters={"is_active": 1},
            fields=["name", "document_type", "workflow_state_field"],
            order_by="name asc",
            limit_page_length=500,
        )
    except Exception as error:
        return {"available": False, "error_type": type(error).__name__, "items": []}

    items = []
    for workflow in workflows:
        doctype = _value(workflow, "document_type")
        if doctype not in WORKFLOW_DOCTYPES:
            continue
        try:
            states = frappe.get_all(
                "Workflow Document State",
                filters={"parent": _value(workflow, "name")},
                fields=["state", "doc_status"],
                order_by="idx asc",
                limit_page_length=100,
            )
        except Exception as error:
            states = []
            state_error = type(error).__name__
        else:
            state_error = None
        items.append(
            {
                "name": _value(workflow, "name"),
                "document_type": doctype,
                "state_field": _value(workflow, "workflow_state_field"),
                "states": [
                    {
                        "state": _value(state, "state"),
                        "doc_status": _as_int(_value(state, "doc_status")),
                    }
                    for state in states
                ],
                "state_read_error": state_error,
            }
        )
    return {"available": True, "items": items}


def get_site_preflight_report():
    """Return a bounded, read-only site inventory for bench execute.

    Run as an operator from the Bench server with:
    bench --site <site> execute crm_signals.diagnostics.get_site_preflight_report
    This function is intentionally not whitelisted for HTTP access.
    """
    companies = frappe.get_all(
        "Company",
        fields=["name", "default_currency"],
        order_by="name asc",
        limit_page_length=500,
    )
    try:
        from crm_signals.settings import get_signal_settings

        settings = get_signal_settings()
        settings_available = True
        settings_error = None
    except Exception as error:
        settings = {}
        settings_available = False
        settings_error = type(error).__name__

    installed_apps = sorted(frappe.get_installed_apps())
    doctype_reports = {
        doctype: _doctype_summary(doctype, required_fields)
        for doctype, required_fields in PREFLIGHT_DOCTYPES.items()
    }
    return {
        "report_version": 1,
        "generated_at": str(frappe.utils.now_datetime()),
        "read_only": True,
        "http_whitelisted": False,
        "framework": {
            "frappe_version": str(getattr(frappe, "__version__", "") or ""),
            "installed_apps": [_app_version(app) for app in installed_apps],
        },
        "site": {
            "timezone": frappe.db.get_single_value("System Settings", "time_zone"),
        },
        "companies": companies,
        "crm_signals_settings": {
            "available": settings_available,
            "error_type": settings_error,
            **(_settings_summary(settings, companies) if settings_available else {}),
        },
        "active_lead_opportunity_workflows": _workflow_summary(),
        "doctypes": doctype_reports,
        "acceptance_warning": (
            "Static metadata is not proof of effective user permissions, financial "
            "reconciliation, SLA calendar behavior, or pilot acceptance."
        ),
    }
