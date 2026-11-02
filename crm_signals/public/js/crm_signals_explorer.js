["Lead", "Customer", "Opportunity", "CRM Signal"].forEach((doctype) => {
    frappe.ui.form.on(doctype, {
        refresh(frm) {
            if (frm.is_new()) return;
            if (doctype === "CRM Signal" && !frm.doc.lead && !frm.doc.customer) return;
            if (doctype === "Opportunity" && (!frm.doc.opportunity_from || !frm.doc.party_name)) return;

            frm.add_custom_button(__("Activity Timeline"), () => {
                const contextDoctype =
                    doctype === "CRM Signal" && frm.doc.signal_type === "High-Value Quote"
                        ? "Highlight"
                        : doctype;
                frappe.set_route("crm-signals-explorer", contextDoctype, frm.doc.name);
            });
        }
    });
});
