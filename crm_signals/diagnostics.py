"""Read-only target-site diagnostics for operators using bench execute.

This module intentionally exposes no whitelisted HTTP method. The static report
reads configuration and DocType metadata only. The optional user-access report
checks only explicitly supplied sample document names and never returns business
field values.
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



def _normalize_user_permission_inputs(users, sample_documents):
    """Validate and bound explicit operator-supplied permission checks."""
    if not isinstance(users, (list, tuple)) or not users:
        raise ValueError("users must be a non-empty list of Frappe user IDs")
    if len(users) > 20:
        raise ValueError("at most 20 users may be checked in one report")

    normalized_users = []
    for user in users:
        if not isinstance(user, str) or not user.strip() or len(user.strip()) > 140:
            raise ValueError("each user must be a non-empty Frappe user ID of at most 140 characters")
        normalized = user.strip()
        if normalized not in normalized_users:
            normalized_users.append(normalized)

    if sample_documents is None:
        sample_documents = {}
    if not isinstance(sample_documents, dict):
        raise ValueError("sample_documents must map supported DocTypes to document-name lists")

    normalized_documents = {}
    total_documents = 0
    for doctype, names in sample_documents.items():
        if doctype not in PREFLIGHT_DOCTYPES:
            raise ValueError(f"unsupported sample-document DocType: {doctype}")
        if not isinstance(names, (list, tuple)):
            raise ValueError(f"sample document names for {doctype} must be a list")
        if len(names) > 10:
            raise ValueError(f"at most 10 sample documents may be checked for {doctype}")

        normalized_names = []
        for name in names:
            if not isinstance(name, str) or not name.strip() or len(name.strip()) > 140:
                raise ValueError(f"sample document names for {doctype} must be non-empty strings")
            normalized = name.strip()
            if normalized not in normalized_names:
                normalized_names.append(normalized)

        normalized_documents[doctype] = normalized_names
        total_documents += len(normalized_names)

    if total_documents > 40 or len(normalized_users) * total_documents > 200:
        raise ValueError("sample-document checks are limited to 40 names and 200 user/document pairs")

    return normalized_users, normalized_documents


def _user_doctype_permission_summary(user, doctype, required_fields, sample_names):
    """Summarize DocType, field-permlevel and explicit document read checks."""
    if not frappe.db.exists("DocType", doctype):
        return {
            "available": False,
            "doctype_read": None,
            "doctype_read_error": None,
            "required_fields": [
                {
                    "fieldname": name,
                    "present": False,
                    "permlevel": None,
                    "field_permlevel_read": False,
                }
                for name in required_fields
            ],
            "sample_document_checks": [],
        }

    meta = frappe.get_meta(doctype)
    try:
        doctype_read = bool(frappe.has_permission(doctype, ptype="read", user=user))
        doctype_read_error = None
    except Exception as error:
        doctype_read = None
        doctype_read_error = type(error).__name__

    fields_by_name = {
        _value(field, "fieldname"): field
        for field in getattr(meta, "fields", [])
        if _value(field, "fieldname")
    }
    try:
        permitted_fields = set(
            meta.get_permitted_fieldnames(user=user, permission_type="read")
        )
        field_permission_error = None
    except Exception as error:
        permitted_fields = set()
        field_permission_error = type(error).__name__

    required = []
    for fieldname in required_fields:
        field = fields_by_name.get(fieldname)
        required.append(
            {
                "fieldname": fieldname,
                "present": field is not None,
                "permlevel": _as_int(_value(field, "permlevel")) if field else None,
                "field_permlevel_read": bool(field and fieldname in permitted_fields),
            }
        )

    sample_checks = []
    for name in sample_names:
        try:
            readable = bool(
                frappe.has_permission(
                    doctype,
                    ptype="read",
                    doc=name,
                    user=user,
                )
            )
        except Exception as error:
            sample_checks.append(
                {"name": name, "read": None, "error_type": type(error).__name__}
            )
        else:
            sample_checks.append({"name": name, "read": readable, "error_type": None})

    return {
        "available": True,
        "doctype_read": doctype_read,
        "doctype_read_error": doctype_read_error,
        "required_fields": required,
        "field_permission_error": field_permission_error,
        "sample_document_checks": sample_checks,
        "permission_boundary": (
            "DocType read uses frappe.has_permission; field access reports role-based "
            "permlevel grants; each supplied sample document is checked separately."
        ),
    }


def get_user_access_preflight_report(users, sample_documents=None):
    """Return bounded, read-only access diagnostics for named test users.

    Run from the Bench server. Optional sample_documents is a mapping such as
    {"Lead": ["LEAD-00001"], "Quotation": ["QTN-00001"]}. Only permission
    outcomes and document names are returned; business field values are not.
    This function is intentionally not whitelisted for HTTP access.
    """
    normalized_users, normalized_documents = _normalize_user_permission_inputs(
        users, sample_documents
    )
    user_reports = []

    for user in normalized_users:
        user_info = frappe.db.get_value(
            "User", user, ["enabled", "user_type"], as_dict=True
        )
        if not user_info:
            user_reports.append(
                {
                    "user": user,
                    "account_exists": False,
                    "enabled": None,
                    "user_type": None,
                    "roles": [],
                    "doctypes": {},
                }
            )
            continue

        roles_error = None
        try:
            roles = sorted(set(frappe.get_roles(user)))
        except Exception as error:
            roles = []
            roles_error = type(error).__name__

        doctype_reports = {
            doctype: _user_doctype_permission_summary(
                user,
                doctype,
                required_fields,
                normalized_documents.get(doctype, []),
            )
            for doctype, required_fields in PREFLIGHT_DOCTYPES.items()
        }
        user_reports.append(
            {
                "user": user,
                "account_exists": True,
                "enabled": bool(_as_int(_value(user_info, "enabled"))),
                "user_type": _value(user_info, "user_type"),
                "roles": roles,
                "roles_error": roles_error,
                "doctypes": doctype_reports,
            }
        )

    return {
        "report_version": 1,
        "generated_at": str(frappe.utils.now_datetime()),
        "read_only": True,
        "http_whitelisted": False,
        "users": user_reports,
        "acceptance_warning": (
            "This report checks DocType-level read, role-based field permlevels and "
            "only the explicitly supplied sample documents. It does not execute list, "
            "report, export, API, digest or realtime paths and is not pilot acceptance."
        ),
    }
