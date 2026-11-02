"""Disposable ERPNext fixtures for real D1/D2 aggregate and permission checks.

This module is called only by Bench CI. It commits the one-time setup wizard
baseline, then keeps every synthetic business record in a transaction that is
rolled back in the finally block. The POS row intentionally models the persisted
aggregate fields; it does not exercise the POS payment workflow.
"""

import frappe
from frappe.utils import add_days, nowdate, random_string


def _ensure_ci_company():
    if frappe.is_setup_complete():
        return

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


def _company_context(tag):
    company = frappe.db.get_value(
        "Company", {"company_name": "CRM Signals CI Company"}, "name"
    )
    if not company:
        company = frappe.db.get_value("Company", {}, "name")
    if not company:
        frappe.throw("D1/D2 fixture requires a completed ERPNext setup wizard")

    doc = frappe.get_doc("Company", company)
    currency = doc.default_currency
    receivable = doc.get("default_receivable_account") or frappe.db.get_value(
        "Account",
        {"company": company, "account_type": "Receivable", "is_group": 0},
        "name",
    )
    income = doc.get("default_income_account") or frappe.db.get_value(
        "Account",
        {"company": company, "root_type": "Income", "is_group": 0},
        "name",
    )
    cost_center = (
        doc.get("cost_center")
        or doc.get("default_cost_center")
        or frappe.db.get_value(
            "Cost Center", {"company": company, "is_group": 0}, "name"
        )
    )
    bank = doc.get("default_bank_account") or frappe.db.get_value(
        "Account",
        {"company": company, "account_type": "Bank", "is_group": 0},
        "name",
    )
    if not bank:
        bank_parent = frappe.db.get_value(
            "Account",
            {"company": company, "account_type": "Bank", "is_group": 1},
            "name",
        )
        if not bank_parent:
            frappe.throw("D1/D2 fixture cannot find a Bank account group")
        bank_doc = frappe.get_doc(
            {
                "doctype": "Account",
                "account_name": f"CRM Signals CI Bank {tag}",
                "company": company,
                "parent_account": bank_parent,
                "account_type": "Bank",
                "account_currency": currency,
            }
        ).insert(ignore_permissions=True)
        bank = bank_doc.name

    missing = [
        label
        for label, value in (
            ("default currency", currency),
            ("receivable account", receivable),
            ("income account", income),
            ("cost center", cost_center),
            ("bank account", bank),
        )
        if not value
    ]
    if missing:
        frappe.throw("D1/D2 fixture is missing: " + ", ".join(missing))

    return {
        "company": company,
        "currency": currency,
        "receivable": receivable,
        "income": income,
        "cost_center": cost_center,
        "bank": bank,
    }


def _create_customer_and_item(context, tag):
    customer_group = frappe.db.get_value(
        "Customer Group", {"is_group": 0}, "name"
    )
    territory = frappe.db.get_value("Territory", {"is_group": 0}, "name")
    item_group = frappe.db.get_value("Item Group", {"is_group": 0}, "name")
    if not customer_group or not territory or not item_group:
        frappe.throw("D1/D2 fixture requires leaf Customer Group, Territory and Item Group records")

    if not frappe.db.exists("UOM", "Nos"):
        frappe.get_doc({"doctype": "UOM", "uom_name": "Nos"}).insert(
            ignore_permissions=True
        )

    customer = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": f"CRM Signals CI Customer {tag}",
            "customer_type": "Individual",
            "customer_group": customer_group,
            "territory": territory,
            "default_currency": context["currency"],
            "accounts": [
                {
                    "company": context["company"],
                    "account": context["receivable"],
                }
            ],
        }
    ).insert(ignore_permissions=True)

    item = frappe.get_doc(
        {
            "doctype": "Item",
            "item_code": f"CRM-SIGNALS-CI-{tag}",
            "item_name": f"CRM Signals CI Item {tag}",
            "item_group": item_group,
            "stock_uom": "Nos",
            "is_stock_item": 0,
        }
    ).insert(ignore_permissions=True)
    return customer.name, item.name


def _price_list(currency, tag):
    name = frappe.db.get_value(
        "Price List",
        {"currency": currency, "selling": 1, "enabled": 1},
        "name",
    )
    if name:
        return name
    doc = frappe.get_doc(
        {
            "doctype": "Price List",
            "price_list_name": f"CRM Signals CI {currency} {tag}",
            "selling": 1,
            "buying": 0,
            "enabled": 1,
            "currency": currency,
        }
    ).insert(ignore_permissions=True)
    return doc.name


def _create_invoice(context, customer, item, tag, rate, due_date, currency=None):
    currency = currency or context["currency"]
    price_list = _price_list(currency, tag)
    invoice = frappe.get_doc(
        {
            "doctype": "Sales Invoice",
            "company": context["company"],
            "customer": customer,
            "posting_date": add_days(nowdate(), -10),
            "due_date": due_date,
            "set_posting_time": 1,
            "debit_to": context["receivable"],
            "currency": currency,
            "conversion_rate": 83 if currency == "USD" and context["currency"] != "USD" else 1,
            "selling_price_list": price_list,
            "price_list_currency": currency,
            "plc_conversion_rate": 1,
            "cost_center": context["cost_center"],
            "items": [
                {
                    "item_code": item,
                    "qty": 1,
                    "rate": rate,
                    "price_list_rate": rate,
                    "income_account": context["income"],
                    "cost_center": context["cost_center"],
                }
            ],
        }
    )
    invoice.insert(ignore_permissions=True)
    invoice.submit()
    return invoice


def _create_opportunity(customer, status, currency, amount):
    opportunity = frappe.get_doc(
        {
            "doctype": "Opportunity",
            "opportunity_from": "Customer",
            "party_name": customer,
            "status": status,
            "transaction_date": nowdate(),
        }
    ).insert(ignore_permissions=True)
    frappe.db.set_value(
        "Opportunity",
        opportunity.name,
        {"currency": currency, "opportunity_amount": amount},
    )
    return opportunity.name


def _currency_totals(rows):
    totals = {}
    for row in rows or []:
        currency = row.get("currency") or "Unspecified currency"
        totals[currency] = totals.get(currency, 0.0) + float(
            row.get("total_amount") or 0
        )
    return totals


def _assert_currency_delta(label, before, after, currency, expected):
    actual = _currency_totals(after).get(currency, 0.0) - _currency_totals(
        before
    ).get(currency, 0.0)
    if abs(actual - expected) > 0.05:
        frappe.throw(
            f"{label} {currency} delta: expected {expected}, found {actual}"
        )


def _assert_d1(baseline, actual, currency):
    leads_before = baseline["leads"]
    leads_after = actual["leads"]
    if leads_after["created_last_30_days"] != leads_before["created_last_30_days"] + 1:
        frappe.throw("D1 fixture did not add exactly one recent Lead")
    if leads_after["active"] != leads_before["active"] + 1:
        frappe.throw("D1 fixture did not add exactly one active Lead")

    opp_before = baseline["opportunities"]
    opp_after = actual["opportunities"]
    if opp_after["total_count"] != opp_before["total_count"] + 3:
        frappe.throw("D1 fixture did not add exactly three Opportunities")
    if opp_after["active_count"] != opp_before["active_count"] + 2:
        frappe.throw("D1 fixture counted a terminal Opportunity as active")

    before_stages = {row["status"]: row["total"] for row in opp_before["stages"]}
    after_stages = {row["status"]: row["total"] for row in opp_after["stages"]}
    if after_stages.get("Open", 0) - before_stages.get("Open", 0) != 2:
        frappe.throw("D1 fixture did not add exactly two active Open stages")
    _assert_currency_delta(
        "D1 active pipeline", opp_before["pipeline_by_currency"],
        opp_after["pipeline_by_currency"], currency, 1250
    )
    _assert_currency_delta(
        "D1 active pipeline", opp_before["pipeline_by_currency"],
        opp_after["pipeline_by_currency"], "USD", 2500
    )


def _invoice_snapshot(name):
    return frappe.db.get_value(
        "Sales Invoice",
        name,
        [
            "currency",
            "grand_total",
            "party_account_currency",
            "outstanding_amount",
            "paid_amount",
        ],
        as_dict=True,
    )


def _assert_d2(baseline, actual, invoices, payment_entry, company_currency):
    before = baseline["billing"]
    after = actual["billing"]
    if not all(
        after.get(key)
        for key in (
            "available",
            "invoiced_available",
            "outstanding_available",
            "customer_receipts_available",
            "pos_receipts_available",
            "overdue_available",
        )
    ):
        frappe.throw("D2 fixture returned an unavailable aggregate section")

    snapshots = [_invoice_snapshot(name) for name in invoices]
    usd_invoice = snapshots[2]
    if (
        usd_invoice.currency != "USD"
        or usd_invoice.party_account_currency != company_currency
    ):
        frappe.throw("D2 fixture did not preserve the Company's party-account currency for a USD invoice")
    expected_invoiced = {}
    expected_outstanding = {}
    for row in snapshots:
        expected_invoiced[row.currency] = (
            expected_invoiced.get(row.currency, 0) + float(row.grand_total or 0)
        )
        expected_outstanding[row.party_account_currency] = (
            expected_outstanding.get(row.party_account_currency, 0)
            + float(row.outstanding_amount or 0)
        )

    for currency, amount in expected_invoiced.items():
        _assert_currency_delta(
            "D2 invoiced", before["invoiced_by_currency"],
            after["invoiced_by_currency"], currency, amount
        )
    for currency, amount in expected_outstanding.items():
        _assert_currency_delta(
            "D2 outstanding", before["outstanding_by_currency"],
            after["outstanding_by_currency"], currency, amount
        )

    payment = frappe.get_doc("Payment Entry", payment_entry)
    _assert_currency_delta(
        "D2 customer receipts",
        before["customer_receipts_by_currency"],
        after["customer_receipts_by_currency"],
        payment.paid_to_account_currency,
        float(payment.received_amount or 0),
    )
    pos = snapshots[-1]
    if (
        float(pos.paid_amount or 0) < float(pos.grand_total or 0) - 0.05
        or float(pos.outstanding_amount or 0) > 0.05
    ):
        frappe.throw("D2 POS-shaped invoice is not fully paid in the aggregate fixture")
    _assert_currency_delta(
        "D2 POS receipts",
        before["pos_receipts_by_currency"],
        after["pos_receipts_by_currency"],
        pos.currency,
        float(pos.paid_amount or 0),
    )
    if after["overdue_count"] != before["overdue_count"] + 1:
        frappe.throw("D2 fixture did not add exactly one overdue invoice")
    overdue_names = {row.get("name") for row in after["overdue_invoices"]}
    if invoices[0] not in overdue_names:
        frappe.throw("D2 fixture did not return the synthetic overdue invoice")


def _create_payment_reader(tag):
    role = f"CRM Signals CI Payment Reader {tag}"
    user = f"crm-signals-ci-{tag.lower()}@example.com"
    frappe.get_doc(
        {"doctype": "Role", "role_name": role, "desk_access": 0}
    ).insert(ignore_permissions=True)
    frappe.get_doc(
        {
            "doctype": "Custom DocPerm",
            "parent": "Payment Entry",
            "role": role,
            "read": 1,
            "select": 1,
        }
    ).insert(ignore_permissions=True)
    frappe.get_doc(
        {
            "doctype": "User",
            "email": user,
            "first_name": f"CRM Signals CI Payment Reader {tag}",
            "enabled": 1,
            "user_type": "System User",
            "send_welcome_email": 0,
            "roles": [{"role": role}],
        }
    ).insert(ignore_permissions=True)
    frappe.clear_cache()
    return user


def _assert_independent_payment_permission(user, expected_currency, expected_amount):
    from crm_signals.api import get_sales_compass_data

    frappe.set_user(user)
    if frappe.has_permission("Sales Invoice", ptype="read"):
        frappe.throw("D2 fixture user unexpectedly has Sales Invoice read access")
    if not frappe.has_permission("Payment Entry", ptype="read"):
        frappe.throw("D2 fixture user does not have Payment Entry read access")

    billing = get_sales_compass_data()["billing"]
    if billing["available"] or billing["invoiced_available"]:
        frappe.throw("D2 invoice metrics were not hidden from the split-permission user")
    if not billing["customer_receipts_available"]:
        frappe.throw("D2 Payment Entry receipts were hidden from the split-permission user")
    receipts = _currency_totals(billing["customer_receipts_by_currency"])
    if receipts.get(expected_currency, 0.0) < expected_amount - 0.05:
        frappe.throw("D2 split-permission user could not see the synthetic Payment Entry receipt")


def verify_sales_compass_aggregate_fixture():
    """Assert D1/D2 aggregate deltas and split-source permissions on a disposable site."""
    from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

    from crm_signals.api import get_sales_compass_data

    previous_user = frappe.session.user
    tag = random_string(8).upper()
    try:
        frappe.set_user("Administrator")
        _ensure_ci_company()
        frappe.db.commit()
        context = _company_context(tag)
        customer, item = _create_customer_and_item(context, tag)
        baseline = get_sales_compass_data()

        frappe.get_doc(
            {
                "doctype": "Lead",
                "lead_name": f"CRM Signals CI Lead {tag}",
                "company_name": f"CRM Signals CI Lead {tag}",
                "status": "Open",
            }
        ).insert(ignore_permissions=True)
        _create_opportunity(customer, "Open", context["currency"], 1250)
        _create_opportunity(customer, "Open", "USD", 2500)
        _create_opportunity(customer, "Lost", context["currency"], 5000)

        overdue = _create_invoice(
            context, customer, item, tag, 1000, add_days(nowdate(), -5)
        )
        paid = _create_invoice(
            context, customer, item, tag, 300, add_days(nowdate(), 10)
        )
        usd = _create_invoice(
            context, customer, item, tag, 100, add_days(nowdate(), 10), "USD"
        )
        pos = _create_invoice(
            context, customer, item, tag, 500, add_days(nowdate(), 10)
        )
        frappe.db.set_value(
            "Sales Invoice",
            pos.name,
            {
                "is_pos": 1,
                "paid_amount": pos.grand_total,
                "outstanding_amount": 0,
            },
        )

        payment = get_payment_entry(
            "Sales Invoice", paid.name, bank_account=context["bank"]
        )
        payment.reference_no = f"CRM Signals CI {tag}"
        payment.reference_date = nowdate()
        payment.submit()

        actual = get_sales_compass_data()
        invoice_names = [overdue.name, paid.name, usd.name, pos.name]
        _assert_d1(baseline, actual, context["currency"])
        _assert_d2(
            baseline, actual, invoice_names, payment.name, context["currency"]
        )

        reader = _create_payment_reader(tag)
        _assert_independent_payment_permission(
            reader,
            payment.paid_to_account_currency,
            float(payment.received_amount or 0),
        )
        frappe.set_user("Administrator")
        return {
            "status": "passed",
            "framework_version": frappe.__version__,
            "synthetic_lead_count": 1,
            "synthetic_opportunity_count": 3,
            "synthetic_invoice_count": 4,
            "synthetic_payment_entry_count": 1,
            "split_permission": "Payment Entry readable; Sales Invoice denied",
            "pos_workflow_tested": False,
            "financial_reconciliation": False,
            "records_committed": False,
        }
    finally:
        frappe.set_user("Administrator")
        frappe.db.rollback()
        frappe.clear_cache()
        frappe.set_user(previous_user)
