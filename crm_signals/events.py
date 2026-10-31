import frappe

HIGH_VALUE_QUOTE_THRESHOLD = 200000


def _party_links(doctype, party_name):
    """Return one validated Link field for a Quotation party."""
    if not party_name:
        return {"lead": None, "customer": None}
    if doctype == "Customer":
        if not frappe.db.exists("Customer", party_name):
            frappe.throw(f"Customer {party_name} does not exist", frappe.LinkValidationError)
        return {"lead": None, "customer": party_name}
    if doctype == "Lead":
        if not frappe.db.exists("Lead", party_name):
            frappe.throw(f"Lead {party_name} does not exist", frappe.LinkValidationError)
        return {"lead": party_name, "customer": None}
    frappe.throw(f"Unsupported quotation party type: {doctype}", frappe.ValidationError)


def _insert_signal(signal_type, message, priority, lead=None, customer=None):
    signal = frappe.get_doc({
        "doctype": "CRM Signal",
        "signal_type": signal_type,
        "lead": lead,
        "customer": customer,
        "message": message,
        "priority": priority,
        "is_read": 0,
    })
    signal.insert(ignore_permissions=True)  # Trusted document event, not public input.
    frappe.publish_realtime(
        event="crm_signal_received",
        message={
            "name": signal.name,
            "signal_type": signal.signal_type,
            "priority": signal.priority,
            "lead": signal.lead,
            "customer": signal.customer,
        },
        after_commit=True,
    )
    return signal


def on_quotation_submit(doc, method=None):
    """Emit a signal when a submitted quotation crosses the configured threshold."""
    if (doc.grand_total or 0) < HIGH_VALUE_QUOTE_THRESHOLD:
        return
    links = _party_links(getattr(doc, "quotation_to", None), getattr(doc, "party_name", None))
    party = doc.party_name or "the selected party"
    _insert_signal(
        signal_type="High-Value Quote",
        message=f"High-value quotation {doc.name} submitted for {party} (₹{doc.grand_total:,.2f})",
        priority="High",
        **links,
    )


def on_opportunity_update(doc, method=None):
    """Emit a signal on the configured meaningful Opportunity status transition."""
    # ERPNext's Opportunity statuses differ by workflow/customization. Keep this
    # explicit and narrow until the target site's desired stage list is configured.
    target_status = "Replied"
    if not doc.has_value_changed("status") or doc.status != target_status:
        return
    lead = getattr(doc, "party_name", None) if getattr(doc, "opportunity_from", None) == "Lead" else None
    customer = getattr(doc, "party_name", None) if getattr(doc, "opportunity_from", None) == "Customer" else None
    _insert_signal(
        signal_type="Opportunity Activity",
        message=f"Opportunity {doc.name} status updated to {target_status}",
        priority="Medium",
        lead=lead,
        customer=customer,
    )
