app_name = "crm_signals"
app_title = "CRM Signals"
app_publisher = "Mithilesh Bansod"
app_description = "Real-time event signals & proactive push digests for ERPNext CRM"
app_license = "mit"

app_include_js = "/assets/crm_signals/js/crm_signals_desk.js"

scheduler_events = {
    "cron": {
        "30 8 * * *": [
            "crm_signals.tasks.send_daily_signals_digest"
        ]
    }
}

doc_events = {
    "Quotation": {
        "on_submit": "crm_signals.events.on_quotation_submit"
    },
    "Opportunity": {
        "on_update": "crm_signals.events.on_opportunity_update"
    }
}
