frappe.pages["crm-signals-explorer"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Customer Activity Timeline"),
        single_column: true
    });

    wrapper.crm_signals_explorer = new CRMSignalsExplorer(page);
    wrapper.crm_signals_explorer.loadRoute();
};

frappe.pages["crm-signals-explorer"].on_page_show = function (wrapper) {
    if (wrapper.crm_signals_explorer) {
        wrapper.crm_signals_explorer.loadRoute();
    }
};

class CRMSignalsExplorer {
    constructor(page) {
        this.page = page;
        this.body = $('<div class="crm-signals-explorer"></div>').appendTo(page.main);
        this.context = null;
        this.cursor = null;
        this.items = [];
        this.sources = [];
        this.requestSequence = 0;

        page.set_primary_action(__("Refresh"), () => this.refresh(), "refresh");
        this.body.on("click", ".crm-explorer-load-more", () => this.loadMore());
        this.body.on("click", ".crm-explorer-source", (event) => {
            const button = $(event.currentTarget);
            const doctype = button.attr("data-doctype");
            const name = button.attr("data-name");
            if (doctype && name) {
                frappe.set_route("Form", doctype, name);
            }
        });
    }

    escape(value) {
        return frappe.utils.escape_html(String(value === null || value === undefined ? "" : value));
    }

    formatTimestamp(value) {
        if (!value) return "";
        try {
            return frappe.datetime.str_to_user(value);
        } catch {
            return String(value);
        }
    }

    loadRoute() {
        const route = frappe.get_route();
        if (route[0] === "crm-signals-explorer") {
            this.load(route[1], route[2]);
        }
    }

    load(contextDoctype, contextName, force = false) {
        if (!contextDoctype || !contextName) {
            this.context = null;
            this.requestSequence += 1;
            this.showError(__("Open this page from a Lead, Customer, Opportunity or CRM Signal."));
            return;
        }

        const nextContext = {
            doctype: String(contextDoctype),
            name: String(contextName)
        };
        if (
            !force &&
            this.context &&
            this.context.doctype === nextContext.doctype &&
            this.context.name === nextContext.name
        ) {
            return;
        }

        this.context = nextContext;
        this.cursor = null;
        this.items = [];
        this.sources = [];
        this.fetchPage(null, false);
    }

    refresh() {
        if (this.context) {
            this.load(this.context.doctype, this.context.name, true);
        }
    }

    loadMore() {
        if (this.context && this.cursor) {
            this.fetchPage(this.cursor, true);
        }
    }

    fetchPage(cursor, append) {
        const requestSequence = ++this.requestSequence;
        const requestedContext = { ...this.context };
        const isCurrentRequest = () =>
            requestSequence === this.requestSequence &&
            this.context &&
            this.context.doctype === requestedContext.doctype &&
            this.context.name === requestedContext.name;

        if (!append) {
            this.body.html(
                '<div class="crm-explorer-state">' +
                '<span class="spinner-border spinner-border-sm"></span> ' +
                __("Loading activity timeline…") +
                "</div>"
            );
        } else {
            this.body.find(".crm-explorer-load-more").prop("disabled", true);
        }

        const args = {
            context_doctype: this.context.doctype,
            context_name: this.context.name,
            page_length: 20
        };
        if (cursor) {
            args.cursor = cursor;
        }

        frappe.call({
            method: "crm_signals.explorer.get_explorer_timeline",
            type: "GET",
            args: args,
            callback: (response) => {
                if (!isCurrentRequest()) return;
                if (!response.message) {
                    this.showError(__("Unable to load the activity timeline. Check your access and refresh."));
                    return;
                }

                const result = response.message;
                this.sources = result.sources || [];
                const nextItems = result.items || [];
                if (append) {
                    const byIdentity = new Map(
                        this.items.map((item) => [
                            item.source_id + ":" + item.source_event_id,
                            item
                        ])
                    );
                    nextItems.forEach((item) => {
                        byIdentity.set(item.source_id + ":" + item.source_event_id, item);
                    });
                    this.items = Array.from(byIdentity.values());
                } else {
                    this.items = nextItems;
                }
                this.cursor = result.next_cursor || null;
                this.render(result.context || this.context);
            },
            error: () => {
                if (!isCurrentRequest()) return;
                this.showError(__("Unable to load the activity timeline. Check your access and refresh."));
            }
        });
    }

    render(context) {
        const sourceLabels = {
            crm_signal: __("CRM Signals"),
            quotation: __("Quotations"),
            opportunity: __("Opportunities")
        };
        const statusLabels = {
            available: __("Available"),
            empty: __("No matching activity"),
            unavailable: __("Unavailable"),
            not_connected: __("Not connected")
        };
        const sourceHtml = this.sources.map((source) => {
            const label = sourceLabels[source.source_id] || source.source_doctype || source.source_id;
            const status = statusLabels[source.status] || __("Unavailable");
            return (
                '<div class="crm-explorer-source-state">' +
                '<span>' + this.escape(label) + "</span>" +
                '<strong class="crm-explorer-status-' + this.escape(source.status) + '">' +
                this.escape(status) + "</strong>" +
                "</div>"
            );
        }).join("");

        const itemHtml = this.items.map((item) => {
            const doctype = String(item.source_doctype || "");
            const name = String(item.source_event_id || "");
            const label = __("Open source record") + ": " + doctype + " " + name;
            return (
                '<article class="crm-explorer-item">' +
                '<div class="crm-explorer-item-copy">' +
                '<div class="crm-explorer-item-summary">' + this.escape(item.summary || item.event_type) + "</div>" +
                '<time class="crm-explorer-item-time">' + this.escape(this.formatTimestamp(item.timestamp)) + "</time>" +
                "</div>" +
                '<button type="button" class="btn btn-default btn-xs crm-explorer-source" ' +
                'data-doctype="' + this.escape(doctype) + '" data-name="' + this.escape(name) + '" ' +
                'aria-label="' + this.escape(label) + '">' +
                __("Open source") +
                "</button>" +
                "</article>"
            );
        }).join("");

        const emptyHtml = this.items.length
            ? ""
            : '<div class="crm-explorer-state">' + __("No matching activity is available.") + "</div>";
        const loadMoreHtml = this.cursor
            ? '<div class="crm-explorer-load-more-wrap"><button type="button" class="btn btn-default crm-explorer-load-more">' +
                __("Load more activity") +
                "</button></div>"
            : "";

        this.body.html(
            '<div class="crm-explorer-context">' +
            '<div class="crm-explorer-context-title">' +
            this.escape(context.doctype + " · " + context.name) +
            "</div>" +
            '<div class="crm-explorer-sources">' + sourceHtml + "</div>" +
            '<div class="crm-explorer-timeline">' + itemHtml + "</div>" +
            emptyHtml +
            loadMoreHtml +
            "</div>"
        );
    }

    showError(message) {
        this.body.html('<div class="crm-explorer-state crm-explorer-error">' + this.escape(message) + "</div>");
    }
}
