import frappe
from frappe import _

ALLOWED_SIGNAL_TYPES = {
    "Website Visit",
    "Email Opened",
    "Link Clicked",
    "WhatsApp Interaction",
    "Inbound Call",
    "High-Value Quote",
    "Opportunity Activity",
}
ALLOWED_PRIORITIES = {"Low", "Medium", "High", "Urgent"}
MAX_MESSAGE_LENGTH = 2000


def _dashboard_aggregate_field(operation, fieldname, alias):
    """Use the aggregate field syntax supported by the installed Frappe major version.

    Frappe v16 moved aggregate fields from raw SQL strings to a structured
    dict representation. Keep the app compatible with both declared versions.
    """
    version = str(getattr(frappe, "__version__", "15"))
    try:
        major_version = int(version.split(".", 1)[0])
    except (TypeError, ValueError):
        major_version = 15

    if major_version >= 16:
        return {operation.upper(): "*" if operation.upper() == "COUNT" else fieldname, "as": alias}
    return f"{operation.lower()}({fieldname}) as {alias}"



def _read_text(value, fieldname, *, required=False, max_length=None):
    if value is None:
        value = ""
    if not isinstance(value, str):
        frappe.throw(_("{0} must be text").format(fieldname), frappe.ValidationError)
    value = value.strip()
    if required and not value:
        frappe.throw(_("{0} is mandatory").format(fieldname), frappe.MandatoryError)
    if max_length is not None and len(value) > max_length:
        frappe.throw(
            _("{0} cannot exceed {1} characters").format(fieldname, max_length),
            frappe.ValidationError,
        )
    return value or None


@frappe.whitelist(methods=["POST"])
def ingest_signal():
    """Create a CRM Signal from an authenticated, idempotent integration request."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication is required"), frappe.AuthenticationError)

    from crm_signals.events import insert_signal_once
    from crm_signals.settings import get_signal_settings

    settings = get_signal_settings()
    if not settings["enabled"] or not settings["enable_external_ingestion"]:
        frappe.throw(_("External CRM Signal ingestion is disabled"), frappe.PermissionError)

    data = frappe.local.form_dict
    signal_type = _read_text(data.get("signal_type"), "signal_type", required=True)
    message = _read_text(
        data.get("message"), "message", required=True, max_length=MAX_MESSAGE_LENGTH
    )
    lead = _read_text(data.get("lead"), "lead")
    customer = _read_text(data.get("customer"), "customer")
    priority = _read_text(data.get("priority") or "Medium", "priority", required=True)
    source_event_id = _read_text(data.get("source_event_id"), "source_event_id", max_length=140)
    source_doctype = _read_text(data.get("source_doctype"), "source_doctype", max_length=140)
    source_name = _read_text(data.get("source_name"), "source_name", max_length=140)

    if signal_type not in ALLOWED_SIGNAL_TYPES:
        frappe.throw(_("Unsupported signal_type"), frappe.ValidationError)
    if priority not in ALLOWED_PRIORITIES:
        frappe.throw(_("Unsupported priority"), frappe.ValidationError)
    if lead and customer:
        frappe.throw(_("Provide either lead or customer, not both"), frappe.ValidationError)
    if lead and not frappe.db.exists("Lead", lead):
        frappe.throw(_("Lead {0} does not exist").format(lead), frappe.LinkValidationError)
    if customer and not frappe.db.exists("Customer", customer):
        frappe.throw(_("Customer {0} does not exist").format(customer), frappe.LinkValidationError)

    if bool(source_doctype) != bool(source_name):
        frappe.throw(
            _("source_doctype and source_name must be supplied together"),
            frappe.ValidationError,
        )
    if (source_doctype or source_name) and not source_event_id:
        frappe.throw(_("source_event_id is required with source metadata"), frappe.ValidationError)
    if source_event_id and not source_doctype:
        source_doctype = "API Integration"
        source_name = frappe.session.user

    signal, created = insert_signal_once(
        signal_type=signal_type,
        message=message,
        priority=priority,
        lead=lead,
        customer=customer,
        source_doctype=source_doctype,
        source_name=source_name,
        source_event_id=source_event_id,
        ignore_permissions=False,
    )
    return {
        "status": "success",
        "signal": signal.name,
        "deduplicated": not created,
    }


@frappe.whitelist()
def get_dashboard_data():
    """Return permission-filtered CRM Signal metrics for the Desk dashboard.

    All reads use frappe.get_list so DocType permissions and the app's
    permission_query_conditions hook are applied to the requesting user.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication is required"), frappe.AuthenticationError)
    if not frappe.has_permission("CRM Signal", ptype="read"):
        frappe.throw(_("You do not have permission to view CRM Signals"), frappe.PermissionError)

    from frappe.utils import add_days, nowdate

    def count_signals(filters=None):
        rows = frappe.get_list(
            "CRM Signal",
            fields=[_dashboard_aggregate_field("COUNT", "name", "total")],
            filters=filters or {},
            limit_page_length=1,
        )
        return int((rows[0].get("total") if rows else 0) or 0)

    stats = {
        "total": count_signals(),
        "unread": count_signals({"is_read": 0}),
        "high_priority": count_signals({"priority": ["in", ["High", "Urgent"]]}),
        "last_7_days": count_signals({"creation": [">=", add_days(nowdate(), -7)]}),
    }

    by_type = frappe.get_list(
        "CRM Signal",
        fields=["signal_type", _dashboard_aggregate_field("COUNT", "name", "total")],
        group_by="signal_type",
        order_by="signal_type asc",
        limit_page_length=20,
    )

    recent = frappe.get_list(
        "CRM Signal",
        fields=[
            "name", "creation", "signal_type", "priority",
            "message", "lead", "customer", "is_read",
        ],
        order_by="creation desc",
        limit_page_length=12,
    )

    return {
        "stats": stats,
        "by_type": [
            {"signal_type": row.signal_type, "total": int(row.total or 0)}
            for row in by_type
        ],
        "recent": recent,
    }



# ---------------------------------------------------------------------------
# S.A.H.D.E.V. Pillar D — Sales Compass (first executive dashboard slice)
# ---------------------------------------------------------------------------

_TERMINAL_SALES_STATUSES = {
    "cancelled",
    "closed",
    "converted",
    "do not contact",
    "lost",
    "obsolete",
}


def _sales_dashboard_value(row, fieldname, default=None):
    if isinstance(row, dict):
        return row.get(fieldname, default)
    return getattr(row, fieldname, default)


def _sales_dashboard_is_terminal(status):
    normalized = str(status or "").strip().lower()
    return normalized in _TERMINAL_SALES_STATUSES or normalized.startswith("lost ")


def _sales_dashboard_doctype_meta(doctype):
    """Return metadata only when this user can read the requested standard DocType."""
    if not frappe.db.exists("DocType", doctype):
        return None
    if not frappe.has_permission(doctype, ptype="read"):
        return None
    return frappe.get_meta(doctype)


def _sales_dashboard_count(rows):
    return sum(int(_sales_dashboard_value(row, "total", 0) or 0) for row in rows)


def _sales_compass_empty_result():
    return {
        "period_days": 30,
        "leads": {
            "available": False,
            "created_last_30_days": None,
            "active_available": False,
            "active": None,
        },
        "opportunities": {
            "available": False,
            "total_count": None,
            "status_available": False,
            "active_count": None,
            "stages_available": False,
            "stages": [],
            "pipeline_value_available": False,
            "pipeline_by_currency": [],
            "recent": [],
        },
    }


def _sales_compass_lead_metrics(period_start):
    metrics = {
        "available": False,
        "created_last_30_days": None,
        "active_available": False,
        "active": None,
    }
    try:
        lead_meta = _sales_dashboard_doctype_meta("Lead")
        if not lead_meta:
            return metrics

        lead_has_status = lead_meta.has_field("status")
        lead_active = None
        if lead_has_status:
            lead_groups = frappe.get_list(
                "Lead",
                fields=["status", _dashboard_aggregate_field("COUNT", "name", "total")],
                group_by="status",
                order_by="status asc",
                limit_page_length=100,
            )
            lead_active = sum(
                int(_sales_dashboard_value(row, "total", 0) or 0)
                for row in lead_groups
                if not _sales_dashboard_is_terminal(_sales_dashboard_value(row, "status"))
            )

        new_lead_rows = frappe.get_list(
            "Lead",
            fields=[_dashboard_aggregate_field("COUNT", "name", "total")],
            filters={"creation": [">=", period_start]},
            limit_page_length=1,
        )
        return {
            "available": True,
            "created_last_30_days": _sales_dashboard_count(new_lead_rows),
            "active_available": lead_has_status,
            "active": lead_active,
        }
    except frappe.PermissionError:
        return metrics


def _sales_dashboard_opportunity_group_rows(opportunity_meta, has_status, pipeline_available):
    group_fields = [_dashboard_aggregate_field("COUNT", "name", "total")]
    group_by_fields = []
    if has_status:
        group_fields.insert(0, "status")
        group_by_fields.append("status")
    if pipeline_available:
        group_fields.extend([
            "currency",
            _dashboard_aggregate_field("SUM", "opportunity_amount", "total_amount"),
        ])
        group_by_fields.append("currency")

    return frappe.get_list(
        "Opportunity",
        fields=group_fields,
        group_by=", ".join(group_by_fields) if group_by_fields else None,
        order_by="status asc" if has_status else None,
        limit_page_length=200,
    )


def _sales_dashboard_opportunity_stage_metrics(group_rows, has_status, pipeline_available):
    stages = {}
    pipeline = {}
    active_count = 0
    if has_status:
        for row in group_rows:
            status = _sales_dashboard_value(row, "status")
            count = int(_sales_dashboard_value(row, "total", 0) or 0)
            if _sales_dashboard_is_terminal(status):
                continue

            active_count += count
            stage_name = str(status or _("Unspecified"))
            stages[stage_name] = stages.get(stage_name, 0) + count
            if pipeline_available:
                currency = str(
                    _sales_dashboard_value(row, "currency") or _("Unspecified currency")
                )
                pipeline[currency] = pipeline.get(currency, 0.0) + float(
                    _sales_dashboard_value(row, "total_amount", 0) or 0
                )
    return active_count, stages, pipeline


def _sales_dashboard_recent_opportunities(opportunity_meta):
    fields = ["name"]
    optional_fields = (
        "creation",
        "status",
        "opportunity_from",
        "party_name",
        "customer_name",
        "opportunity_amount",
        "currency",
        "expected_closing",
    )
    fields.extend(field for field in optional_fields if opportunity_meta.has_field(field))
    return frappe.get_list(
        "Opportunity",
        fields=fields,
        order_by="creation desc",
        limit_page_length=8,
    )


def _sales_compass_opportunity_metrics():
    metrics = {
        "available": False,
        "total_count": None,
        "status_available": False,
        "active_count": None,
        "stages_available": False,
        "stages": [],
        "pipeline_value_available": False,
        "pipeline_by_currency": [],
        "recent": [],
    }
    try:
        opportunity_meta = _sales_dashboard_doctype_meta("Opportunity")
        if not opportunity_meta:
            return metrics

        has_status = opportunity_meta.has_field("status")
        has_amount = opportunity_meta.has_field("opportunity_amount")
        has_currency = opportunity_meta.has_field("currency")
        pipeline_available = has_status and has_amount and has_currency
        group_rows = _sales_dashboard_opportunity_group_rows(
            opportunity_meta, has_status, pipeline_available
        )
        total_count = _sales_dashboard_count(group_rows)
        active_count, stages, pipeline = _sales_dashboard_opportunity_stage_metrics(
            group_rows, has_status, pipeline_available
        )
        recent = _sales_dashboard_recent_opportunities(opportunity_meta)

        return {
            "available": True,
            "total_count": total_count,
            "status_available": has_status,
            "active_count": active_count if has_status else None,
            "stages_available": has_status,
            "stages": [
                {"status": status, "total": total}
                for status, total in sorted(stages.items(), key=lambda item: item[0].lower())
            ],
            "pipeline_value_available": pipeline_available,
            "pipeline_by_currency": [
                {"currency": currency, "total_amount": amount}
                for currency, amount in sorted(pipeline.items())
            ],
            "recent": recent,
        }
    except frappe.PermissionError:
        return metrics


@frappe.whitelist()
def get_sales_compass_data():
    """Return permission-filtered Pillar D metrics from ERPNext CRM data.

    Monetary metrics remain grouped by transaction currency. Billing and
    service SLA use separate source-backed metric contracts.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication is required"), frappe.AuthenticationError)

    from frappe.utils import add_days, nowdate

    period_start = add_days(nowdate(), -30)
    result = _sales_compass_empty_result()
    result["leads"] = _sales_compass_lead_metrics(period_start)
    result["opportunities"] = _sales_compass_opportunity_metrics()
    result["billing"] = _get_sales_billing_data(period_start, nowdate())
    result["service"] = _get_helpdesk_service_metrics(period_start)
    return result




# ---------------------------------------------------------------------------
# S.A.H.D.E.V. Pillar D3 — Frappe Helpdesk service resolution and SLA
# ---------------------------------------------------------------------------

def _helpdesk_empty_metrics():
    return {
        "source": "Frappe Helpdesk", "available": False, "period_days": 30,
        "created_last_30_days": None, "backlog_available": False,
        "open_backlog": None, "paused_backlog": None,
        "resolved_available": False, "resolved_last_30_days": None,
        "resolution_time_available": False, "average_resolution_hours": None,
        "sla_available": False, "sla_eligible": None, "sla_fulfilled": None,
        "sla_failed": None, "sla_compliance_percent": None, "sla_unconfigured": None,
    }


def _helpdesk_count(filters):
    rows = frappe.get_list(
        "HD Ticket",
        fields=[_dashboard_aggregate_field("COUNT", "name", "total")],
        filters=filters, limit_page_length=1,
    )
    return int(_sales_dashboard_value(rows[0], "total", 0) if rows else 0)


def _get_helpdesk_service_metrics(period_start):
    """Aggregate standard Frappe Helpdesk ticket lifecycle and native SLA outcomes."""
    metrics = _helpdesk_empty_metrics()
    try:
        ticket_meta = _sales_dashboard_doctype_meta("HD Ticket")
        if not ticket_meta or not all(ticket_meta.has_field(f) for f in ("creation", "status_category")):
            return metrics
        metrics["available"] = True
        metrics["created_last_30_days"] = _helpdesk_count({"creation": [">=", period_start]})
        category_rows = frappe.get_list(
            "HD Ticket",
            fields=["status_category", _dashboard_aggregate_field("COUNT", "name", "total")],
            group_by="status_category", order_by="status_category asc", limit_page_length=10,
        )
        categories = {
            str(_sales_dashboard_value(row, "status_category", "") or ""):
            int(_sales_dashboard_value(row, "total", 0) or 0) for row in category_rows
        }
        metrics.update({
            "backlog_available": True,
            "open_backlog": categories.get("Open", 0),
            "paused_backlog": categories.get("Paused", 0),
        })
        if ticket_meta.has_field("resolution_date"):
            metrics["resolved_available"] = True
            resolved_filters = {"resolution_date": [">=", period_start], "status_category": "Resolved"}
            metrics["resolved_last_30_days"] = _helpdesk_count(resolved_filters)
            if ticket_meta.has_field("resolution_time"):
                average_rows = frappe.get_list(
                    "HD Ticket",
                    fields=[_dashboard_aggregate_field("AVG", "resolution_time", "average_resolution_seconds")],
                    filters={**resolved_filters, "resolution_time": [">", 0]}, limit_page_length=1,
                )
                raw_average = _sales_dashboard_value(
                    average_rows[0], "average_resolution_seconds", None
                ) if average_rows else None
                metrics["resolution_time_available"] = True
                metrics["average_resolution_hours"] = (
                    round(float(raw_average) / 3600, 2) if raw_average is not None else None
                )
        if ticket_meta.has_field("sla") and ticket_meta.has_field("agreement_status"):
            if not frappe.has_permission("HD Service Level Agreement", ptype="read"):
                return metrics
            if not _sales_dashboard_doctype_meta("HD Service Level Agreement"):
                return metrics
            sla_rows = frappe.get_list(
                "HD Ticket",
                fields=["agreement_status", _dashboard_aggregate_field("COUNT", "name", "total")],
                filters={"sla": ["is", "set"]},
                group_by="agreement_status", order_by="agreement_status asc", limit_page_length=20,
            )
            outcomes = {
                str(_sales_dashboard_value(row, "agreement_status", "") or ""):
                int(_sales_dashboard_value(row, "total", 0) or 0) for row in sla_rows
            }
            fulfilled, failed = outcomes.get("Fulfilled", 0), outcomes.get("Failed", 0)
            eligible = fulfilled + failed
            metrics.update({
                "sla_available": True, "sla_eligible": eligible,
                "sla_fulfilled": fulfilled, "sla_failed": failed,
                "sla_compliance_percent": round(fulfilled * 100 / eligible, 1) if eligible else None,
                "sla_unconfigured": _helpdesk_count({"sla": ["is", "not set"]}),
            })
        return metrics
    except frappe.PermissionError:
        return _helpdesk_empty_metrics()

# ---------------------------------------------------------------------------
# S.A.H.D.E.V. Pillar D2 — Billing realization
# ---------------------------------------------------------------------------

def _sales_billing_group_rows(doctype, filters, currency_field, amount_field):
    """Aggregate one amount only within its source currency."""
    rows = frappe.get_list(
        doctype,
        fields=[
            currency_field,
            _dashboard_aggregate_field("SUM", amount_field, "total_amount"),
            _dashboard_aggregate_field("COUNT", "name", "record_count"),
        ],
        filters=filters,
        group_by=currency_field,
        order_by=f"{currency_field} asc",
        limit_page_length=100,
    )
    return [
        {
            "currency": str(_sales_dashboard_value(row, currency_field) or _("Unspecified currency")),
            "total_amount": float(_sales_dashboard_value(row, "total_amount", 0) or 0),
            "record_count": int(_sales_dashboard_value(row, "record_count", 0) or 0),
        }
        for row in rows
    ]


def _sales_billing_empty_result():
    return {
        "available": False,
        "period_days": 30,
        "sales_invoice_unavailable_reason": None,
        "invoiced_available": False,
        "invoiced_by_currency": [],
        "outstanding_available": False,
        "outstanding_by_currency": [],
        "customer_receipts_available": False,
        "customer_receipts_by_currency": [],
        "pos_receipts_available": False,
        "pos_receipts_by_currency": [],
        "overdue_available": False,
        "overdue_count": None,
        "overdue_invoices": [],
    }


def _sales_billing_group_metrics(result, invoice_meta, base_filters, period_start):
    has_currency = invoice_meta.has_field("currency")
    has_posting_date = invoice_meta.has_field("posting_date")
    has_grand_total = invoice_meta.has_field("grand_total")
    has_outstanding = invoice_meta.has_field("outstanding_amount")
    has_party_currency = invoice_meta.has_field("party_account_currency")
    has_is_return = invoice_meta.has_field("is_return")

    if has_is_return and has_currency and has_grand_total and has_posting_date:
        invoiced_filters = dict(base_filters)
        invoiced_filters["posting_date"] = [">=", period_start]
        result["invoiced_by_currency"] = _sales_billing_group_rows(
            "Sales Invoice", invoiced_filters, "currency", "grand_total"
        )
        result["invoiced_available"] = True

    if has_is_return and has_party_currency and has_outstanding:
        outstanding_filters = dict(base_filters)
        outstanding_filters["outstanding_amount"] = [">", 0]
        result["outstanding_by_currency"] = _sales_billing_group_rows(
            "Sales Invoice", outstanding_filters, "party_account_currency", "outstanding_amount"
        )
        result["outstanding_available"] = True

    if (
        has_is_return
        and has_currency
        and invoice_meta.has_field("is_pos")
        and invoice_meta.has_field("paid_amount")
        and has_posting_date
    ):
        pos_filters = dict(base_filters)
        pos_filters.update({
            "is_pos": 1,
            "paid_amount": [">", 0],
            "posting_date": [">=", period_start],
        })
        result["pos_receipts_by_currency"] = _sales_billing_group_rows(
            "Sales Invoice", pos_filters, "currency", "paid_amount"
        )
        result["pos_receipts_available"] = True


def _sales_billing_overdue_metrics(result, invoice_meta, base_filters, today):
    if not (
        invoice_meta.has_field("is_return")
        and invoice_meta.has_field("outstanding_amount")
        and invoice_meta.has_field("party_account_currency")
        and invoice_meta.has_field("due_date")
    ):
        return

    overdue_filters = dict(base_filters)
    overdue_filters.update({
        "outstanding_amount": [">", 0],
        "due_date": ["<", today],
    })
    overdue_count_rows = frappe.get_list(
        "Sales Invoice",
        fields=[_dashboard_aggregate_field("COUNT", "name", "total")],
        filters=overdue_filters,
        limit_page_length=1,
    )
    result["overdue_count"] = int(
        _sales_dashboard_value(overdue_count_rows[0], "total", 0)
        if overdue_count_rows else 0
    )

    overdue_fields = [
        "name", "customer", "due_date", "party_account_currency", "outstanding_amount"
    ]
    if invoice_meta.has_field("currency"):
        overdue_fields.append("currency")
    if invoice_meta.has_field("customer_name"):
        overdue_fields.insert(2, "customer_name")
    if invoice_meta.has_field("posting_date"):
        overdue_fields.insert(2, "posting_date")
    result["overdue_invoices"] = frappe.get_list(
        "Sales Invoice",
        fields=overdue_fields,
        filters=overdue_filters,
        order_by="due_date asc",
        limit_page_length=8,
    )
    result["overdue_available"] = True


def _sales_invoice_metrics(result, invoice_meta, period_start, today):
    has_is_return = invoice_meta.has_field("is_return")
    base_filters = {"docstatus": 1}
    if has_is_return:
        base_filters["is_return"] = 0
    else:
        result["sales_invoice_unavailable_reason"] = _(
            "Sales Invoice is_return metadata is unavailable; return-sensitive measures cannot exclude returns"
        )

    # Every Sales Invoice measure claims to exclude returns. Do not aggregate
    # if the metadata cannot establish return identity.
    _sales_billing_group_metrics(result, invoice_meta, base_filters, period_start)
    _sales_billing_overdue_metrics(result, invoice_meta, base_filters, today)


def _sales_customer_receipt_metrics(result, period_start):
    try:
        payment_meta = _sales_dashboard_doctype_meta("Payment Entry")
        required_fields = (
            "payment_type",
            "party_type",
            "posting_date",
            "received_amount",
            "paid_to_account_currency",
        )
        if payment_meta and all(payment_meta.has_field(field) for field in required_fields):
            result["customer_receipts_by_currency"] = _sales_billing_group_rows(
                "Payment Entry",
                {
                    "docstatus": 1,
                    "payment_type": "Receive",
                    "party_type": "Customer",
                    "posting_date": [">=", period_start],
                },
                "paid_to_account_currency",
                "received_amount",
            )
            result["customer_receipts_available"] = True
    except frappe.PermissionError:
        pass
    return result


def _get_sales_billing_data(period_start, today):
    """Return permission-filtered billing metrics with explicit source semantics.

    Payment Entry receipts are grouped in receiving-account currency and include
    allocated and advance receipts. POS receipts remain a separate measure.
    """
    result = _sales_billing_empty_result()
    try:
        invoice_meta = _sales_dashboard_doctype_meta("Sales Invoice")
        if not invoice_meta:
            result["sales_invoice_unavailable_reason"] = _(
                "Sales Invoice source is unavailable for this user"
            )
            return result

        result["available"] = True
        _sales_invoice_metrics(result, invoice_meta, period_start, today)
    except frappe.PermissionError:
        return result

    return _sales_customer_receipt_metrics(result, period_start)
