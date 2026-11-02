frappe.provide("crm_signals");
const crmSignals = window.crm_signals;

crmSignals.seen_delivery_ids = crmSignals.seen_delivery_ids || new Set();

crmSignals.handle_realtime_signal = function(data) {
    if (!data || !data.signal_type || !data.message) return;
    if (data.delivery_id) {
        if (crmSignals.seen_delivery_ids.has(data.delivery_id)) return;
        crmSignals.seen_delivery_ids.add(data.delivery_id);
        if (crmSignals.seen_delivery_ids.size > 500) {
            const oldest = crmSignals.seen_delivery_ids.values().next().value;
            crmSignals.seen_delivery_ids.delete(oldest);
        }
    }

    let indicator = data.priority === "Urgent" ? "red" : (data.priority === "High" ? "orange" : "blue");
    frappe.show_alert({
        message: `<b>[${frappe.utils.escape_html(data.signal_type)}]</b> ${frappe.utils.escape_html(data.message)}`,
        indicator: indicator
    }, 12);

    if (typeof cur_list !== "undefined" && cur_list && cur_list.doctype === "CRM Signal") {
        cur_list.refresh();
    }
};

$(document).on("app_ready", function() {
    frappe.realtime.on("crm_signal_received", crmSignals.handle_realtime_signal);
});
