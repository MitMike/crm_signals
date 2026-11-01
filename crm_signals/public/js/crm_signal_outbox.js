frappe.ui.form.on("CRM Signal Outbox", {
    refresh(frm) {
        if (frm.doc.status !== "Failed" || !frappe.user.has_role("System Manager")) {
            return;
        }
        frm.add_custom_button(__("Replay Failed Event"), () => {
            frappe.confirm(
                __("This requeues the event and may send a CRM Signal notification. Attempt history is retained. Continue?"),
                () => {
                    frappe.call({
                        method: "crm_signals.crm_signals.doctype.crm_signal_outbox.crm_signal_outbox.replay_failed_signal_outbox",
                        args: { name: frm.doc.name },
                        freeze: true,
                        freeze_message: __("Queueing audited replay..."),
                    }).then(() => frm.reload_doc());
                }
            );
        });
    },
});
