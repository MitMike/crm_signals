frappe.pages["crm-signals-dashboard"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("CRM Signals Dashboard"),
        single_column: true
    });

    const dashboard = new CRMSignalsDashboard(page);
    wrapper.crm_signals_dashboard = dashboard;
    dashboard.refresh();
};

class CRMSignalsDashboard {
    constructor(page) {
        this.page = page;
        this.body = $('<div class="crm-signals-dashboard"></div>').appendTo(page.main);
        this.bind_events();

        page.set_primary_action(__("Refresh"), () => this.refresh(), "refresh");
        page.add_inner_button(__("All Signals"), () => {
            frappe.set_route("List", "CRM Signal");
        });
        page.add_inner_button(__("New Signal"), () => {
            frappe.new_doc("CRM Signal");
        });
    }

    bind_events() {
        this.body.on("click", ".crm-signal-row", (event) => {
            const row = $(event.currentTarget);
            const name = row.attr("data-name");
            const lead = row.attr("data-lead");
            const customer = row.attr("data-customer");

            if (lead) {
                frappe.set_route("Form", "Lead", lead);
            } else if (customer) {
                frappe.set_route("Form", "Customer", customer);
            } else if (name) {
                frappe.set_route("Form", "CRM Signal", name);
            }
        });
    }

    refresh() {
        this.body.html(
            '<div class="crm-dashboard-loading"><span class=" spinner-border spinner-border-sm"></span> ' +
            __("Loading CRM signals…") +
            "</div>"
        );

        frappe.call({
            method: "crm_signals.api.get_dashboard_data",
            freeze: false,
            callback: (response) => {
                if (response.message) {
                    this.render(response.message);
                }
            },
            error: () => {
                this.body.html(
                    '<div class="crm-dashboard-empty">' +
                    __("Unable to load the CRM Signals dashboard. Check your access and try again.") +
                    "</div>"
                );
            }
        });
    }

    escape(value) {
        return frappe.utils.escape_html(String(value === null || value === undefined ? "" : value));
    }

    number(value) {
        return Number(value || 0).toLocaleString();
    }

    render(data) {
        const stats = data.stats || {};
        const cards = [
            { label: __("Total signals"), value: stats.total, hint: __("Signals visible to you"), tone: "blue" },
            { label: __("Unread"), value: stats.unread, hint: __("Awaiting acknowledgement"), tone: "orange" },
            { label: __("High priority"), value: stats.high_priority, hint: __("High and urgent signals"), tone: "red" },
            { label: __("Last 7 days"), value: stats.last_7_days, hint: __("New signals this week"), tone: "green" }
        ];

        const cardHtml = cards.map((card) => {
            return '<div class="crm-dashboard-card">' +
                '<div class="crm-dashboard-card-label">' + this.escape(card.label) + "</div>" +
                '<div class="crm-dashboard-card-value ' + card.tone + '">' + this.number(card.value) + "</div>" +
                '<div class="crm-dashboard-card-hint">' + this.escape(card.hint) + "</div>" +
                "</div>";
        }).join("");

        const types = data.by_type || [];
        const maximum = Math.max(1, ...types.map((item) => Number(item.total || 0)));
        const typeHtml = types.length ? types.map((item) => {
            const count = Number(item.total || 0);
            const width = Math.max(3, Math.min(100, Math.round((count / maximum) * 100)));
            return '<div class="crm-dashboard-type-row">' +
                '<div class="crm-dashboard-type-heading"><span>' + this.escape(item.signal_type) +
                '</span><strong>' + this.number(count) + "</strong></div>" +
                '<div class="crm-dashboard-bar"><span style="width:' + width + '%"></span></div>' +
                "</div>";
        }).join("") : '<div class="crm-dashboard-empty">' + __("No signals yet.") + "</div>";

        const recent = data.recent || [];
        const recentHtml = recent.length ? recent.map((item) => {
            let party = __("Unlinked signal");
            if (item.lead) party = __("Lead: ") + item.lead;
            if (item.customer) party = __("Customer: ") + item.customer;

            const priority = String(item.priority || "Medium").toLowerCase().replace(/[^a-z]/g, "");
            const readLabel = item.is_read ? __("Read") : __("Unread");
            return '<button type="button" class="crm-signal-row" data-name="' + this.escape(item.name) +
                '" data-lead="' + this.escape(item.lead || "") +
                '" data-customer="' + this.escape(item.customer || "") + '">' +
                '<span class="crm-signal-row-main">' +
                '<span class="crm-signal-row-title">' + this.escape(item.signal_type) + "</span>" +
                '<span class="crm-signal-row-message">' + this.escape(item.message) + "</span>" +
                '<span class="crm-signal-row-meta">' + this.escape(party) + " · " +
                this.escape(item.creation || "") + "</span>" +
                "</span>" +
                '<span class="crm-signal-row-side">' +
                '<span class="crm-signal-priority ' + this.escape(priority) + '">' +
                this.escape(item.priority || "Medium") + "</span>" +
                '<span class="crm-signal-read-state">' + this.escape(readLabel) + "</span>" +
                "</span></button>";
        }).join("") : '<div class="crm-dashboard-empty">' +
            __("No CRM signals have been recorded yet. Signals will appear here as activity is captured.") +
            "</div>";

        this.body.html(
            '<div class="crm-dashboard-intro">' +
                '<div><h3>' + __("Sales activity at a glance") + "</h3>" +
                '<p>' + __("A permission-filtered view of CRM activity and signals assigned to you.") + "</p></div>" +
            "</div>" +
            '<div class="crm-dashboard-cards">' + cardHtml + "</div>" +
            '<div class="crm-dashboard-columns">' +
                '<section class="crm-dashboard-panel">' +
                    '<div class="crm-dashboard-panel-heading"><h4>' + __("Signals by type") + "</h4></div>" +
                    '<div class="crm-dashboard-panel-content">' + typeHtml + "</div>" +
                "</section>" +
                '<section class="crm-dashboard-panel">' +
                    '<div class="crm-dashboard-panel-heading"><h4>' + __("Recent activity") + "</h4>" +
                    '<button class="btn btn-xs btn-default crm-dashboard-view-all">' + __("View all") + "</button></div>" +
                    '<div class="crm-dashboard-recent">' + recentHtml + "</div>" +
                "</section>" +
            "</div>" +
            '<div class="crm-dashboard-footer">' +
                __("Showing the latest 12 signals. Counts follow your CRM Signal permissions.") +
            "</div>"
        );

        this.body.find(".crm-dashboard-view-all").on("click", () => {
            frappe.set_route("List", "CRM Signal");
        });
    }
}
