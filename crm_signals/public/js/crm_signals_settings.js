frappe.ui.form.on("CRM Signals Settings", {
    async notification_preset(frm) {
        const selectedPreset = frm.doc.notification_preset;
        if (!selectedPreset || selectedPreset === "Custom") return;

        const response = await frappe.call({
            method: "crm_signals.settings.get_preset_values",
            args: { preset: selectedPreset },
        });
        if (frm.doc.notification_preset !== selectedPreset) return;

        const values = response.message || {};
        if (!Object.keys(values).length) return;

        frm.__applying_crm_signal_preset = true;
        try {
            for (const [field, value] of Object.entries(values)) {
                await frm.set_value(field, value);
            }
        } finally {
            frm.__applying_crm_signal_preset = false;
        }
        frappe.show_alert({
            message: __("Preset applied. Review and customise the values before enabling signals."),
            indicator: "green",
        });
    },
});

const crmSignalCustomFields = [
    "enabled",
    "enable_external_ingestion",
    "enable_quotation_signals",
    "quotation_threshold",
    "enable_opportunity_signals",
    "opportunity_trigger_statuses",
    "enable_daily_digest",
    "digest_time",
    "lead_stale_days",
    "digest_extra_recipients",
];

for (const field of crmSignalCustomFields) {
    frappe.ui.form.on("CRM Signals Settings", {
        [field](frm) {
            if (
                !frm.__applying_crm_signal_preset &&
                frm.doc.notification_preset !== "Custom"
            ) {
                frm.set_value("notification_preset", "Custom");
            }
        },
    });
}
