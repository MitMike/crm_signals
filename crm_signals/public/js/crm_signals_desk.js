frappe.provide("crm_signals");

$(document).on("app_ready", function() {
    frappe.realtime.on("crm_signal_received", function(data) {
        if (!data || !data.signal_type || !data.message) return;
        let indicator = data.priority === "Urgent" ? "red" : (data.priority === "High" ? "orange" : "blue");
        frappe.show_alert({
            message: `<b>[${frappe.utils.escape_html(data.signal_type)}]</b> ${frappe.utils.escape_html(data.message)}`,
            indicator: indicator
        }, 12);

        if (typeof cur_list !== "undefined" && cur_list && cur_list.doctype === "CRM Signal") {
            cur_list.refresh();
        }
    });
});
