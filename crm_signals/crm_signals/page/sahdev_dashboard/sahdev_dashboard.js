frappe.pages["sahdev-dashboard"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Sahdev Dashboard"),
        single_column: true
    });

    const dashboard = new SahdevSalesCompass(page);
    wrapper.sahdev_sales_compass = dashboard;
    dashboard.refresh();
};

class SahdevSalesCompass {
    constructor(page) {
        this.page = page;
        this.body = $('<div class="sahdev-sales-compass"></div>').appendTo(page.main);

        page.set_primary_action(__("Refresh"), () => this.refresh(), "refresh");
        page.add_inner_button(__("Signals Console"), () => {
            frappe.set_route("crm-signals-dashboard");
        });
        page.add_inner_button(__("All Opportunities"), () => {
            frappe.set_route("List", "Opportunity");
        });
        page.add_inner_button(__("Sales Invoices"), () => {
            frappe.set_route("List", "Sales Invoice");
        });

        this.body.on("click", ".sahdev-invoice-row", (event) => {
            const name = $(event.currentTarget).attr("data-name");
            if (name) frappe.set_route("Form", "Sales Invoice", name);
        });

        this.body.on("click", ".sahdev-opportunity-row", (event) => {
            const name = $(event.currentTarget).attr("data-name");
            if (name) frappe.set_route("Form", "Opportunity", name);
        });
    }

    escape(value) {
        return frappe.utils.escape_html(String(value === null || value === undefined ? "" : value));
    }

    number(value) {
        return Number(value || 0).toLocaleString();
    }

    amount(value, currency) {
        const code = String(currency || "").trim().toUpperCase();
        if (!code) return this.number(value);
        try {
            return new Intl.NumberFormat(undefined, {
                style: "currency",
                currency: code,
                maximumFractionDigits: 0
            }).format(Number(value || 0));
        } catch (error) {
            return code + " " + this.number(value);
        }
    }

    refresh() {
        this.body.html(
            '<div class="sahdev-loading">' +
            '<span class="spinner-border spinner-border-sm"></span> ' +
            __("Loading the sales compass…") +
            "</div>"
        );

        frappe.call({
            method: "crm_signals.api.get_sales_compass_data",
            freeze: false,
            callback: (response) => {
                if (response.message) {
                    this.render(response.message);
                } else {
                    this.showError();
                }
            },
            error: () => this.showError()
        });
    }

    showError() {
        this.body.html(
            '<div class="sahdev-empty">' +
            __("Unable to load the sales compass. Check your Lead and Opportunity access, then refresh.") +
            "</div>"
        );
    }

    render(data) {
        const leads = data.leads || {};
        const opportunities = data.opportunities || {};
        const billing = data.billing || {};

        const cardHtml = this.renderMetricCards(leads, opportunities);
        const stageHtml = this.renderStageList(opportunities);
        const recentHtml = this.renderRecentOpportunities(opportunities);
        const billingHtml = this.renderBillingSection(billing);
        this.body.html(this.renderDashboardLayout(cardHtml, stageHtml, recentHtml, billingHtml));
    }

    renderPipelineValue(opportunities) {
        const pipeline = opportunities.pipeline_by_currency || [];
        if (!opportunities.available) return __("No access");
        if (!opportunities.status_available) return __("Status field unavailable");
        if (!opportunities.pipeline_value_available) return __("Amount or currency field unavailable");
        if (!pipeline.length) return __("No open pipeline");

        return pipeline.map((item) =>
            '<span class="sahdev-metric-subvalue">' +
            this.escape(item.currency) + " " + this.escape(this.amount(item.total_amount, item.currency)) +
            "</span>"
        ).join("");
    }

    renderMetricCards(leads, opportunities) {
        const cards = [
            {
                label: __("New leads · 30 days"),
                value: leads.available ? this.number(leads.created_last_30_days) : "—",
                hint: leads.available ? __("New Lead records created in the last 30 days") : __("Lead access unavailable")
            },
            {
                label: __("Active leads"),
                value: leads.available && leads.active_available ? this.number(leads.active) : "—",
                hint: !leads.available
                    ? __("Lead access unavailable")
                    : leads.active_available
                        ? __("Excludes converted, lost, closed and do-not-contact statuses")
                        : __("Lead status field unavailable")
            },
            {
                label: __("Active opportunities"),
                value: opportunities.available && opportunities.status_available
                    ? this.number(opportunities.active_count)
                    : "—",
                hint: !opportunities.available
                    ? __("Opportunity access unavailable")
                    : opportunities.status_available
                        ? __("Excludes terminal opportunity statuses")
                        : __("Opportunity status field unavailable")
            },
            {
                label: __("Open pipeline value"),
                value: this.renderPipelineValue(opportunities),
                hint: __("Kept separate by transaction currency; no currency conversion is applied")
            }
        ];

        return cards.map((card, index) =>
            '<section class="sahdev-metric-card">' +
            '<div class="sahdev-metric-label">' + this.escape(card.label) + "</div>" +
            (index === 3
                ? '<div class="sahdev-metric-value sahdev-metric-currency">' + card.value + "</div>"
                : '<div class="sahdev-metric-value">' + this.escape(card.value) + "</div>") +
            '<div class="sahdev-metric-hint">' + this.escape(card.hint) + "</div>" +
            "</section>"
        ).join("");
    }

    renderStageList(opportunities) {
        if (!opportunities.available) {
            return '<div class="sahdev-empty">' + __("Opportunity data is not available to your user.") + "</div>";
        }
        if (!opportunities.stages_available) {
            return '<div class="sahdev-empty">' +
                __("Opportunity status field is unavailable; stage distribution cannot be calculated.") +
                "</div>";
        }

        const stages = opportunities.stages || [];
        if (!stages.length) {
            return '<div class="sahdev-empty">' + __("No active opportunities found.") + "</div>";
        }

        const maxStage = Math.max(1, ...stages.map((item) => Number(item.total || 0)));
        return stages.map((item) => this.renderStageRow(item, maxStage)).join("");
    }

    renderStageRow(item, maxStage) {
        const total = Number(item.total || 0);
        const width = Math.max(3, Math.min(100, Math.round(total / maxStage * 100)));
        return '<div class="sahdev-stage-row">' +
            '<div class="sahdev-stage-heading"><span>' + this.escape(item.status || __("Unspecified")) +
            '</span><strong>' + this.number(total) + "</strong></div>" +
            '<div class="sahdev-stage-track"><span style="width:' + width + '%"></span></div>' +
            "</div>";
    }

    renderRecentOpportunities(opportunities) {
        if (!opportunities.available) {
            return '<div class="sahdev-empty">' + __("Opportunity data is not available to your user.") + "</div>";
        }
        const recent = opportunities.recent || [];
        if (!recent.length) {
            return '<div class="sahdev-empty">' + __("No opportunities found.") + "</div>";
        }
        return recent.map((item) => this.renderRecentOpportunity(item)).join("");
    }

    renderRecentOpportunity(item) {
        const title = item.party_name || item.customer_name || item.name;
        const source = item.opportunity_from && item.party_name
            ? item.opportunity_from + ": " + item.party_name
            : item.name;
        const hasAmount = item.opportunity_amount !== null && item.opportunity_amount !== undefined;
        const amount = hasAmount ? this.amount(item.opportunity_amount, item.currency) : "";
        return '<button type="button" class="sahdev-opportunity-row" data-name="' +
            this.escape(item.name) + '">' +
            '<span class="sahdev-opportunity-main">' +
            '<strong>' + this.escape(title) + "</strong>" +
            '<span class="sahdev-opportunity-meta">' + this.escape(source) + " · " +
            this.escape(item.status || __("Unspecified status")) + "</span>" +
            "</span>" +
            '<span class="sahdev-opportunity-side">' +
            (amount ? '<strong>' + this.escape(amount) + "</strong>" : "") +
            '<span>' + this.escape(item.expected_closing || item.creation || "") + "</span>" +
            "</span>" +
            "</button>";
    }

    renderBillingMetric(label, available, rows, countLabel, unavailableMessage) {
        let content = "";
        if (!available) {
            content = this.escape(unavailableMessage || __("Not available for your account"));
        } else if (!rows || !rows.length) {
            content = __("No transactions in this period");
        } else {
            content = rows.map((item) =>
                '<span class="sahdev-billing-currency-line">' +
                '<strong>' + this.escape(this.amount(item.total_amount, item.currency)) + "</strong>" +
                '<small>' + this.escape(item.currency) + " · " +
                this.number(item.record_count) + " " + this.escape(countLabel) + "</small>" +
                "</span>"
            ).join("");
        }
        return '<section class="sahdev-metric-card">' +
            '<div class="sahdev-metric-label">' + this.escape(label) + "</div>" +
            '<div class="sahdev-metric-value sahdev-metric-currency">' + content + "</div>" +
            "</section>";
    }

    renderBillingCards(billing) {
        return [
            this.renderBillingMetric(
                __("Invoiced · 30 days"),
                billing.invoiced_available,
                billing.invoiced_by_currency,
                __("invoices"),
                billing.sales_invoice_unavailable_reason
            ),
            this.renderBillingMetric(
                __("Customer receipts · 30 days"),
                billing.customer_receipts_available,
                billing.customer_receipts_by_currency,
                __("Payment Entries")
            ),
            this.renderBillingMetric(
                __("POS receipts · 30 days"),
                billing.pos_receipts_available,
                billing.pos_receipts_by_currency,
                __("POS invoices"),
                billing.sales_invoice_unavailable_reason
            ),
            this.renderBillingMetric(
                __("Open receivables · current"),
                billing.outstanding_available,
                billing.outstanding_by_currency,
                __("open invoices"),
                billing.sales_invoice_unavailable_reason
            )
        ].join("");
    }

    renderOverdueList(billing) {
        if (!billing.overdue_available) {
            return '<div class="sahdev-empty">' + this.escape(
                billing.sales_invoice_unavailable_reason || __("Overdue invoice details are not available.")
            ) + "</div>";
        }
        const overdue = billing.overdue_invoices || [];
        if (!overdue.length) {
            return '<div class="sahdev-empty">' + __("No overdue open invoices.") + "</div>";
        }
        return overdue.map((item) => this.renderOverdueInvoice(item)).join("");
    }

    renderOverdueInvoice(item) {
        const customer = item.customer_name || item.customer || item.name;
        const amountCurrency = item.party_account_currency || item.currency;
        const amount = this.amount(item.outstanding_amount, amountCurrency);
        return '<button type="button" class="sahdev-invoice-row" data-name="' +
            this.escape(item.name) + '">' +
            '<span class="sahdev-invoice-main">' +
            '<strong>' + this.escape(customer) + "</strong>" +
            '<span class="sahdev-opportunity-meta">' + this.escape(item.name) +
            " · " + __("Due") + " " + this.escape(item.due_date || "") + "</span>" +
            "</span>" +
            '<span class="sahdev-invoice-side">' +
            '<strong>' + this.escape(amount) + "</strong>" +
            '<span>' + this.escape(amountCurrency || "") + "</span>" +
            "</span>" +
            "</button>";
    }

    renderBillingSection(billing) {
        const billingCards = this.renderBillingCards(billing);
        const overdueHtml = this.renderOverdueList(billing);
        const overdueSummary = billing.overdue_available
            ? this.number(billing.overdue_count) + " " + __("overdue invoices")
            : __("Overdue count unavailable");
        const billingNote = __("Invoice and POS amounts use invoice currency. Open receivables use the party-account currency. Payment Entry customer receipts use receiving-account currency and include allocated as well as advance/unallocated receipts. POS receipts are shown separately. All transaction groups remain separate by currency.");

        return '<section class="sahdev-billing-section">' +
            '<div class="sahdev-section-intro">' +
            '<div><div class="sahdev-eyebrow">' + __("S.A.H.D.E.V. · PILLAR D2") + "</div>" +
            '<h3>' + __("Billing realization") + "</h3>" +
            '<p>' + __("Invoice value, customer receipts and open receivables from submitted ERPNext records.") +
            "</p></div>" +
            "</div>" +
            '<div class="sahdev-billing-metrics">' + billingCards + "</div>" +
            '<section class="sahdev-panel sahdev-overdue-panel">' +
            '<div class="sahdev-panel-heading">' +
            '<h4>' + __("Overdue customer invoices") + "</h4>" +
            '<span class="sahdev-overdue-count">' + this.escape(overdueSummary) + "</span>" +
            "</div>" +
            '<div class="sahdev-invoice-list">' + overdueHtml + "</div>" +
            "</section>" +
            '<div class="sahdev-billing-note">' + this.escape(billingNote) + "</div>" +
            "</section>";
    }

    renderDashboardLayout(cardHtml, stageHtml, recentHtml, billingHtml) {
        return '<div class="sahdev-intro">' +
            '<div><div class="sahdev-eyebrow">' + __("S.A.H.D.E.V. · PILLAR D") + "</div>" +
            '<h3>' + __("Executive Compass") + "</h3>" +
            '<p>' + __("A focused view of sales movement from the Lead and Opportunity records you can access.") +
            "</p></div>" +
            "</div>" +
            '<div class="sahdev-metrics">' + cardHtml + "</div>" +
            '<div class="sahdev-follow-on-note">' +
            '<strong>' + __("Scope of this slice") + "</strong> " +
            __("This dashboard now combines CRM sales with the first billing realization slice. Service-ticket SLA metrics remain a separate follow-on slice.") +
            "</div>" +
            '<div class="sahdev-panels">' +
            '<section class="sahdev-panel">' +
            '<div class="sahdev-panel-heading"><h4>' + __("Active pipeline by stage") + "</h4></div>" +
            '<div class="sahdev-panel-content">' + stageHtml + "</div>" +
            "</section>" +
            '<section class="sahdev-panel">' +
            '<div class="sahdev-panel-heading"><h4>' + __("Recent opportunities") + "</h4></div>" +
            '<div class="sahdev-opportunity-list">' + recentHtml + "</div>" +
            "</section>" +
            "</div>" +
            billingHtml +
            '<div class="sahdev-footer">' +
            __("Pipeline totals are grouped by transaction currency. Terminal statuses are excluded from active counts and pipeline value.") +
            "</div>";
    }

}
