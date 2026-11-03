"""Read-only target-site inventory for operators using bench execute.

This module exposes no whitelisted HTTP method. By default, the report reads
configuration and DocType metadata only. An explicitly requested synthetic-record
probe performs bounded, permission-filtered name-only list queries.
"""

import importlib
import re
import subprocess
from pathlib import Path

import frappe

TARGET_ROLES = ("Sales User", "Sales Manager", "System Manager")
TEST_USER_PROFILES = {
    "sales_user": ("Sales User", {"Sales Manager", "System Manager"}),
    "sales_manager": ("Sales Manager", {"System Manager"}),
    "system_manager": ("System Manager", set()),
    "non_sales": (None, set(TARGET_ROLES)),
}
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
TEST_RECORD_DOCTYPES = set(PREFLIGHT_DOCTYPES) - {"HD Service Level Agreement"}
MAX_TEST_RECORDS_PER_PROFILE = 50
MAX_TEST_RECORDS_TOTAL = 100
TEST_RECORD_LABEL_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,39}$")


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


def _source_revision():
    """Return the exact clean-checkout revision without exposing Git errors."""
    try:
        module = importlib.import_module("crm_signals")
        module_file = getattr(module, "__file__", None)
        if not module_file:
            return {"available": False, "reason": "module_path_unavailable"}
        module_path = Path(module_file).resolve()
        app_path = str(module_path.parent)
        repository_path = module_path.parent.parent
        git_options = {
            "check": True,
            "capture_output": True,
            "text": True,
            "timeout": 5,
        }
        root = subprocess.run(
            ["git", "-C", app_path, "rev-parse", "--show-toplevel"],
            **git_options,
        )
        git_root = (root.stdout or "").strip()
        if not git_root or Path(git_root).resolve() != repository_path:
            return {"available": False, "reason": "repository_root_mismatch"}
        status = subprocess.run(
            ["git", "-C", app_path, "status", "--porcelain", "--untracked-files=all"],
            **git_options,
        )
        if (status.stdout or "").strip():
            return {"available": False, "reason": "working_tree_dirty"}
        result = subprocess.run(
            ["git", "-C", app_path, "rev-parse", "--verify", "HEAD"],
            **git_options,
        )
    except FileNotFoundError:
        return {"available": False, "reason": "git_unavailable"}
    except subprocess.TimeoutExpired:
        return {"available": False, "reason": "git_timeout"}
    except subprocess.CalledProcessError:
        return {"available": False, "reason": "git_query_failed"}
    except (ImportError, OSError):
        return {"available": False, "reason": "source_path_unavailable"}

    revision = (result.stdout or "").strip().lower()
    if len(revision) != 40 or any(char not in "0123456789abcdef" for char in revision):
        return {"available": False, "reason": "invalid_revision"}
    return {"available": True, "commit_sha": revision}

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



def _check_test_user_identity(profile, username, seen_users):
    """Validate a supplied synthetic account without retaining its identity."""
    expected_role, disallowed_roles = TEST_USER_PROFILES[profile]
    result = {
        "expected_role": expected_role,
        "account_active": None,
        "system_user": None,
        "role_membership_valid": False,
        "status": None,
        "doctype_read": {},
        "required_field_read": {},
        "error_types": {},
    }
    if not isinstance(username, str) or not username.strip():
        raise ValueError("Each test user profile must map to a non-empty User name")
    username = username.strip()
    if username == "Administrator":
        result["status"] = "administrator_not_allowed"
        return result, None
    if username in seen_users:
        result["status"] = "duplicate_test_user"
        return result, None
    seen_users.add(username)

    try:
        enabled = frappe.db.get_value("User", username, "enabled")
    except Exception as error:
        result["status"] = "user_lookup_failed"
        result["error_types"]["User"] = type(error).__name__
        return result, None
    if enabled is None:
        result["status"] = "user_not_found"
        return result, None
    result["account_active"] = bool(_as_int(enabled))
    if not result["account_active"]:
        result["status"] = "user_disabled"
        return result, None

    try:
        user_type = frappe.db.get_value("User", username, "user_type")
    except Exception as error:
        result["status"] = "user_lookup_failed"
        result["error_types"]["User"] = type(error).__name__
        return result, None
    result["system_user"] = user_type == "System User"
    if not result["system_user"]:
        result["status"] = "user_type_not_system"
        return result, None

    try:
        roles = set(frappe.get_roles(username))
    except Exception as error:
        result["status"] = "role_lookup_failed"
        result["error_types"]["roles"] = type(error).__name__
        return result, None

    expected_role_present = expected_role in roles if expected_role else not bool(
        roles.intersection(TARGET_ROLES)
    )
    result["role_membership_valid"] = expected_role_present and not bool(
        roles.intersection(disallowed_roles)
    )
    if not result["role_membership_valid"]:
        result["status"] = "role_membership_invalid"
        return result, None
    return result, username


def _test_user_doctype_permissions(username, doctype_reports):
    """Return DocType and required-field read checks for one validated account."""
    doctype_read = {}
    required_field_read = {}
    error_types = {}
    for doctype, summary in doctype_reports.items():
        required_fields = [field["fieldname"] for field in summary["required_fields"]]
        if not summary["available"]:
            doctype_read[doctype] = None
            required_field_read[doctype] = {field: None for field in required_fields}
            continue

        try:
            can_read = bool(
                frappe.has_permission(doctype, ptype="read", user=username, throw=False)
            )
        except Exception as error:
            doctype_read[doctype] = None
            required_field_read[doctype] = {field: None for field in required_fields}
            error_types[doctype] = type(error).__name__
            continue

        doctype_read[doctype] = can_read
        if not can_read:
            required_field_read[doctype] = {field: False for field in required_fields}
            continue

        try:
            permitted_fields = set(
                frappe.get_meta(doctype).get_permitted_fieldnames(user=username)
            )
        except Exception as error:
            required_field_read[doctype] = {field: None for field in required_fields}
            error_types[doctype] = type(error).__name__
            continue

        required_field_read[doctype] = {
            field: field in permitted_fields for field in required_fields
        }
    return doctype_read, required_field_read, error_types


def _empty_record_visibility(reason):
    return {
        "available": False,
        "reason": reason,
        "doctypes": {},
        "error_types": {},
    }


def _validate_test_records(test_records, test_users):
    """Validate bounded alias-to-synthetic-record input without retaining output identities."""
    if test_records is None or test_records == {}:
        return {}
    if not isinstance(test_records, dict):
        raise ValueError("test_records must map profile aliases to DocType record labels")
    if not isinstance(test_users, dict) or not test_users:
        raise ValueError("test_records require test_users")
    if set(test_records) - set(TEST_USER_PROFILES):
        raise ValueError("Unsupported test record profile")
    if set(test_records) - set(test_users):
        raise ValueError("test_records require a supplied test user profile")

    normalized = {}
    total_records = 0
    for profile, doctypes in sorted(test_records.items()):
        if not isinstance(doctypes, dict) or not doctypes:
            raise ValueError("Each test record profile must contain DocType mappings")
        profile_records = 0
        normalized[profile] = {}
        for doctype, records in sorted(doctypes.items()):
            if doctype not in TEST_RECORD_DOCTYPES:
                raise ValueError("Unsupported test record DocType")
            if not isinstance(records, dict) or not records:
                raise ValueError("Each test record DocType must contain labeled records")
            normalized_records = {}
            seen_names = set()
            for label, name in sorted(records.items()):
                if not isinstance(label, str) or not TEST_RECORD_LABEL_PATTERN.fullmatch(label):
                    raise ValueError("Invalid test record label")
                if not isinstance(name, str) or not name.strip() or len(name.strip()) > 140:
                    raise ValueError(
                        "Test record names must be non-empty strings of at most 140 characters"
                    )
                name = name.strip()
                if name in seen_names:
                    raise ValueError("Duplicate test record name for DocType")
                seen_names.add(name)
                normalized_records[label] = name
                profile_records += 1
                total_records += 1
                if profile_records > MAX_TEST_RECORDS_PER_PROFILE:
                    raise ValueError("Too many test records for profile")
                if total_records > MAX_TEST_RECORDS_TOTAL:
                    raise ValueError("Too many test records")
            normalized[profile][doctype] = normalized_records
    return normalized


def _record_visibility_for_doctype(doctype, records, summary, doctype_read):
    """Check one bounded DocType group and return labels only."""
    labels = list(records)
    unavailable = {label: None for label in labels}
    if not summary.get("available"):
        return {"status": "doctype_unavailable", "records": unavailable}, None
    if doctype_read.get(doctype) is False:
        return {
            "status": "doctype_read_denied",
            "records": {label: False for label in labels},
        }, None
    if doctype_read.get(doctype) is not True:
        return {
            "status": "doctype_permission_unavailable",
            "records": unavailable,
        }, None

    names = list(records.values())
    try:
        rows = frappe.get_list(
            doctype,
            filters={"name": ["in", names]},
            fields=["name"],
            limit_page_length=len(names),
        )
        visible_names = set()
        for row in rows:
            name = _value(row, "name")
            if name:
                visible_names.add(str(name))
        return {
            "status": "checked",
            "records": {
                label: name in visible_names for label, name in records.items()
            },
        }, None
    except Exception as error:
        return {
            "status": "error",
            "records": unavailable,
        }, type(error).__name__


def _test_user_record_visibility(username, record_specs, doctype_reports, doctype_read):
    """Check exact synthetic record names with permission-filtered name-only list queries."""
    if not record_specs:
        return _empty_record_visibility("test_records_not_supplied")

    session = getattr(frappe, "session", None)
    previous_user = getattr(session, "user", None)
    if not isinstance(previous_user, str) or not previous_user:
        return _empty_record_visibility("session_user_unavailable")

    try:
        frappe.set_user(username)
    except Exception as error:
        return {
            "available": True,
            "reason": None,
            "doctypes": {
                doctype: {
                    "status": "session_switch_failed",
                    "records": {label: None for label in records},
                }
                for doctype, records in record_specs.items()
            },
            "error_types": {"session": type(error).__name__},
        }

    results = {}
    errors = {}
    try:
        for doctype, records in sorted(record_specs.items()):
            result, error_type = _record_visibility_for_doctype(
                doctype,
                records,
                doctype_reports.get(doctype, {}),
                doctype_read,
            )
            results[doctype] = result
            if error_type:
                errors[doctype] = error_type
    finally:
        try:
            frappe.set_user(previous_user)
        except Exception as error:
            errors["session_restore"] = type(error).__name__

    return {
        "available": True,
        "reason": None,
        "doctypes": results,
        "error_types": errors,
    }


def _effective_user_permissions(test_users, doctype_reports, test_records=None):
    """Check explicit synthetic users and, optionally, exact synthetic record visibility."""
    scope = (
        "DocType and required-field read checks; optional bounded list-visibility checks use "
        "Frappe permission-filtered name-only queries for exact supplied synthetic records. "
        "Missing and inaccessible records both report false. This does not prove direct form, "
        "API, report, export, print or dashboard access."
    )
    if test_users is None:
        if test_records not in (None, {}):
            raise ValueError("test_records require test_users")
        return {
            "available": False,
            "reason": "test_users_not_supplied",
            "profiles": {},
            "scope": scope,
        }
    if not isinstance(test_users, dict):
        raise ValueError("test_users must map approved profile aliases to User names")
    if not test_users:
        if test_records not in (None, {}):
            raise ValueError("test_records require test_users")
        return {
            "available": False,
            "reason": "test_users_not_supplied",
            "profiles": {},
            "scope": scope,
        }
    if set(test_users) - set(TEST_USER_PROFILES):
        raise ValueError("Unsupported test user profile")
    normalized_records = _validate_test_records(test_records, test_users)

    profiles = {}
    seen_users = set()
    for profile, username in sorted(test_users.items()):
        result, validated_user = _check_test_user_identity(
            profile, username, seen_users
        )
        if validated_user:
            doctype_read, field_read, errors = _test_user_doctype_permissions(
                validated_user, doctype_reports
            )
            record_specs = normalized_records.get(profile, {})
            record_visibility = _test_user_record_visibility(
                validated_user, record_specs, doctype_reports, doctype_read
            )
            result["doctype_read"] = doctype_read
            result["required_field_read"] = field_read
            result["record_visibility"] = record_visibility
            result["error_types"] = errors
            has_record_error = bool(record_visibility["error_types"]) or (
                bool(record_specs) and not record_visibility["available"]
            )
            result["status"] = "partial" if errors or has_record_error else "checked"
        else:
            result["record_visibility"] = _empty_record_visibility(
                "test_user_not_validated"
            )
        profiles[profile] = result

    return {
        "available": True,
        "reason": None,
        "profiles": profiles,
        "scope": scope,
    }




def get_site_preflight_report(test_users=None, test_records=None):
    """Return a bounded, read-only site inventory for bench execute.

    Run as an operator from the Bench server with:
    bench --site <site> execute crm_signals.diagnostics.get_site_preflight_report
    This function is intentionally not whitelisted for HTTP access. Optional
    test_users maps profile aliases to synthetic accounts; test_records maps
    those profiles to exact synthetic records for name-only list visibility checks.
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
            "crm_signals_source": _source_revision(),
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
        "effective_user_permissions": _effective_user_permissions(
            test_users, doctype_reports, test_records
        ),
        "acceptance_warning": (
            "Static metadata is not proof of effective user permissions, financial "
            "reconciliation, SLA calendar behavior, or pilot acceptance."
        ),
    }
