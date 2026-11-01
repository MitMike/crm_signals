app_name = "crm_signals"
app_title = "CRM Signals"
app_publisher = "Mithilesh Bansod"
app_description = "Real-time event signals & proactive push digests for ERPNext CRM"
app_license = "mit"

app_include_js = "/assets/crm_signals/js/crm_signals_desk.js"

doctype_js = {
    "CRM Signals Settings": "public/js/crm_signals_settings.js",
}

scheduler_events = {
    "cron": {
        "* * * * *": [
            "crm_signals.tasks.send_daily_signals_digest",
            "crm_signals.signal_outbox.process_pending_signal_outbox",
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

# Restrict row-level access to the linked Lead/Customer or active assignee.
has_permission = {
    "CRM Signal": "crm_signals.permissions.crm_signal_has_permission",
}
permission_query_conditions = {
    "CRM Signal": "crm_signals.permissions.crm_signal_query",
}
