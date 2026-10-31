const crmSignalPresetValues = {
    Balanced: {
        enable_quotation_signals: 1,
        quotation_threshold: 200000,
        enable_opportunity_signals: 1,
        opportunity_trigger_statuses: "Replied",
        enable_daily_digest: 1,
        lead_stale_days: 3,
        digest_time: "08:30:00",
    },
    "Sales Focused": {
        enable_quotation_signals: 1,
        quotation_threshold: 100000,
        enable_opportunity_signals: 1,
        opportunity_trigger_statuses: "Replied",
        enable_daily_digest: 1,
        lead_stale_days: 2,
        digest_time: "08:00:00",
    },
    Executive: {
        enable_quotation_signals: 1,
        quotation_threshold: 500000,
        enable_opportunity_signals: 1,
        opportunity_trigger_statuses: "Replied",
        enable_daily_digest: 1,
        lead_stale_days: 5,
        digest_time: "08:30:00",
    },
};

frappe.ui.form.on("CRM Signals Settings", {
    async notification_preset(frm) {
        const values = crmSignalPresetValues[frm.doc.notification_preset];
        if (!values) return;

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
