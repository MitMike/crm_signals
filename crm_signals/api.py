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
    """Create a CRM Signal from an authenticated server-to-server integration.

    Authenticate with Frappe API key/secret as a dedicated integration user.
    The caller must have permission to create CRM Signal documents.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication is required"), frappe.AuthenticationError)

    data = frappe.local.form_dict
    signal_type = _read_text(data.get("signal_type"), "signal_type", required=True)
    message = _read_text(
        data.get("message"), "message", required=True, max_length=MAX_MESSAGE_LENGTH
    )
    lead = _read_text(data.get("lead"), "lead")
    customer = _read_text(data.get("customer"), "customer")
    priority = _read_text(data.get("priority") or "Medium", "priority", required=True)

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

    # Recipient selection is never caller-controlled; the resolver uses related
    # document ownership and active ToDo assignments only.
    doc = frappe.get_doc({
        "doctype": "CRM Signal",
        "signal_type": signal_type,
        "lead": lead,
        "customer": customer,
        "message": message,
        "priority": priority,
        "is_read": 0,
    })
    doc.insert()  # Enforces normal Frappe permissions; framework owns transaction.

    from crm_signals.notifications import notify_signal

    notify_signal(doc)
    return {"status": "success", "signal": doc.name}



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


@frappe.whitelist()
def get_sales_compass_data():
    """Return the first Pillar D sales slice from permission-filtered ERPNext CRM data.

    Metrics intentionally stay in transaction currency; the endpoint never adds
    amounts from different currencies together. Billing and service SLA data are
    not included until their own source-backed slices are implemented.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication is required"), frappe.AuthenticationError)

    from frappe.utils import add_days, nowdate

    period_start = add_days(nowdate(), -30)
    result = {
        "period_days": 30,
        "leads": {
            "available": False,
            "created_last_30_days": None,
            "active": None,
        },
        "opportunities": {
            "available": False,
            "total_count": None,
            "active_count": None,
            "stages": [],
            "pipeline_value_available": False,
            "pipeline_by_currency": [],
            "recent": [],
        },
    }

    # Lead data is independently permission-checked. A user without Lead read
    # access sees an unavailable metric, not a count calculated with elevated
    # permissions.
    try:
        lead_meta = _sales_dashboard_doctype_meta("Lead")
        if lead_meta:
            lead_group_fields = [_dashboard_aggregate_field("COUNT", "name", "total")]
            lead_group_by = None
            if lead_meta.has_field("status"):
                lead_group_fields.insert(0, "status")
                lead_group_by = "status"

            lead_groups = frappe.get_list(
                "Lead",
                fields=lead_group_fields,
                group_by=lead_group_by,
                order_by="status asc" if lead_group_by else None,
                limit_page_length=100,
            )
            lead_active = (
                sum(
                    int(_sales_dashboard_value(row, "total", 0) or 0)
                    for row in lead_groups
                    if not _sales_dashboard_is_terminal(_sales_dashboard_value(row, "status"))
                )
                if lead_group_by
                else _sales_dashboard_count(lead_groups)
            )
            new_lead_rows = frappe.get_list(
                "Lead",
                fields=[_dashboard_aggregate_field("COUNT", "name", "total")],
                filters={"creation": [">=", period_start]},
                limit_page_length=1,
            )
            result["leads"] = {
                "available": True,
                "created_last_30_days": _sales_dashboard_count(new_lead_rows),
                "active": lead_active,
            }
    except frappe.PermissionError:
        pass

    # Opportunity aggregates are grouped by status and currency. Frappe's
    # permission-aware get_list applies the current user's DocType and row rules.
    try:
        opportunity_meta = _sales_dashboard_doctype_meta("Opportunity")
        if opportunity_meta:
            has_status = opportunity_meta.has_field("status")
            has_amount = opportunity_meta.has_field("opportunity_amount")
            has_currency = opportunity_meta.has_field("currency")

            group_fields = [_dashboard_aggregate_field("COUNT", "name", "total")]
            group_by_fields = []
            if has_status:
                group_fields.insert(0, "status")
                group_by_fields.append("status")
            if has_currency:
                group_fields.append("currency")
                group_by_fields.append("currency")
            if has_amount:
                group_fields.append(_dashboard_aggregate_field("SUM", "opportunity_amount", "total_amount"))

            group_rows = frappe.get_list(
                "Opportunity",
                fields=group_fields,
                group_by=", ".join(group_by_fields) if group_by_fields else None,
                order_by="status asc" if has_status else None,
                limit_page_length=200,
            )

            total_count = _sales_dashboard_count(group_rows)
            stages = {}
            pipeline = {}
            active_count = 0
            for row in group_rows:
                status = _sales_dashboard_value(row, "status")
                count = int(_sales_dashboard_value(row, "total", 0) or 0)
                if has_status and _sales_dashboard_is_terminal(status):
                    continue

                active_count += count
                stage_name = str(status or _("Unspecified"))
                stages[stage_name] = stages.get(stage_name, 0) + count

                if has_amount:
                    currency = str(
                        _sales_dashboard_value(row, "currency") or _("Unspecified currency")
                    )
                    pipeline[currency] = pipeline.get(currency, 0.0) + float(
                        _sales_dashboard_value(row, "total_amount", 0) or 0
                    )

            recent_fields = ["name"]
            for optional_field in (
                "creation",
                "status",
                "opportunity_from",
                "party_name",
                "customer_name",
                "opportunity_amount",
                "currency",
                "expected_closing",
            ):
                if opportunity_meta.has_field(optional_field):
                    recent_fields.append(optional_field)

            recent = frappe.get_list(
                "Opportunity",
                fields=recent_fields,
                order_by="creation desc",
                limit_page_length=8,
            )
            result["opportunities"] = {
                "available": True,
                "total_count": total_count,
                "active_count": active_count,
                "stages": [
                    {"status": status, "total": total}
                    for status, total in sorted(stages.items(), key=lambda item: item[0].lower())
                ],
                "pipeline_value_available": has_amount,
                "pipeline_by_currency": [
                    {"currency": currency, "total_amount": amount}
                    for currency, amount in sorted(pipeline.items())
                ],
                "recent": recent,
            }
    except frappe.PermissionError:
        pass

    result["billing"] = _get_sales_billing_data(period_start, nowdate())
    return result



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


def _get_sales_billing_data(period_start, today):
    """Return permission-filtered billing metrics with explicit source semantics.

    - Invoiced: submitted, non-return Sales Invoice grand totals posted in period.
    - Outstanding: current positive outstanding on submitted, non-return invoices.
    - Customer receipts: submitted Receive Payment Entries, shown in receiving
      account currency. This includes allocated and unallocated/advance receipts.
    - POS receipts: paid_amount on submitted POS Sales Invoices, shown in invoice
      currency. Kept separate from Payment Entry receipts to avoid mixed currencies
      and double counting.
    """
    result = {
        "available": False,
        "period_days": 30,
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

    try:
        invoice_meta = _sales_dashboard_doctype_meta("Sales Invoice")
        if not invoice_meta:
            return result

        result["available"] = True
        has_currency = invoice_meta.has_field("currency")
        has_posting_date = invoice_meta.has_field("posting_date")
        has_grand_total = invoice_meta.has_field("grand_total")
        has_outstanding = invoice_meta.has_field("outstanding_amount")
        has_party_currency = invoice_meta.has_field("party_account_currency")
        has_is_return = invoice_meta.has_field("is_return")
        base_filters = {"docstatus": 1}
        if has_is_return:
            base_filters["is_return"] = 0

        if has_currency and has_grand_total and has_posting_date:
            invoiced_filters = dict(base_filters)
            invoiced_filters["posting_date"] = [">=", period_start]
            result["invoiced_by_currency"] = _sales_billing_group_rows(
                "Sales Invoice",
                invoiced_filters,
                "currency",
                "grand_total",
            )
            result["invoiced_available"] = True

        if has_party_currency and has_outstanding:
            outstanding_filters = dict(base_filters)
            outstanding_filters["outstanding_amount"] = [">", 0]
            result["outstanding_by_currency"] = _sales_billing_group_rows(
                "Sales Invoice",
                outstanding_filters,
                "party_account_currency",
                "outstanding_amount",
            )
            result["outstanding_available"] = True

        if has_currency and invoice_meta.has_field("is_pos") and invoice_meta.has_field("paid_amount") and has_posting_date:
            pos_filters = dict(base_filters)
            pos_filters.update({
                "is_pos": 1,
                "paid_amount": [">", 0],
                "posting_date": [">=", period_start],
            })
            result["pos_receipts_by_currency"] = _sales_billing_group_rows(
                "Sales Invoice",
                pos_filters,
                "currency",
                "paid_amount",
            )
            result["pos_receipts_available"] = True

        if has_outstanding and has_party_currency and invoice_meta.has_field("due_date"):
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
    except frappe.PermissionError:
        return result

    # Standard customer receipts. Payment Entry rows are first filtered through
    # the parent's permission-aware get_list before any aggregate is returned.
    try:
        payment_meta = _sales_dashboard_doctype_meta("Payment Entry")
        if (
            payment_meta
            and payment_meta.has_field("payment_type")
            and payment_meta.has_field("party_type")
            and payment_meta.has_field("posting_date")
            and payment_meta.has_field("received_amount")
            and payment_meta.has_field("paid_to_account_currency")
        ):
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
