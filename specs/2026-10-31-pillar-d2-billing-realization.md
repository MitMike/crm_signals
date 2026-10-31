# D2 — Billing Realization

**Status:** Implemented in the D2 feature branch; awaiting review and live-site validation.

## Problem and user

A sales manager or business owner needs an at-a-glance view of billing conversion and receivables alongside sales pipeline data, without confusing invoice value with cash received.

## Goals

- Show invoiced value posted in the last 30 days.
- Show customer receipts posted in the last 30 days.
- Show POS receipts separately from Payment Entry receipts.
- Show current positive outstanding receivables and overdue invoices.
- Keep all amounts grouped by their source currency.
- Respect the requesting user's permissions for every source DocType.

## Non-goals

- No cross-currency conversion or combined grand total.
- No claim that Payment Entry receipts are fully allocated to invoices.
- No claim that invoice amount equals recognized revenue or cash collected.
- No collection forecast, DSO, profitability, tax, credit-note analysis or aging buckets in this slice.
- No dashboard data when a source DocType or required field is unavailable.

## Sources and calculations

### Invoiced · last 30 days

Source: **Sales Invoice**.

Filters: submitted documents (docstatus = 1), exclude returns (is_return = 0), and posting date on or after today minus 30 days.

Measure: sum of grand_total, grouped by invoice currency. This is submitted invoice value, not cash collection or recognized revenue.

### Customer receipts · last 30 days

Source: **Payment Entry**.

Filters: submitted entries (docstatus = 1), payment type Receive, party type Customer, and posting date on or after today minus 30 days.

Measure: sum of received_amount, grouped by paid_to_account_currency. It includes allocated and advance/unallocated receipts; it must not be described as the value allocated against invoices.

### POS receipts · last 30 days

Source: **Sales Invoice**.

Filters: submitted, non-return POS invoices with a positive paid_amount and posting date on or after today minus 30 days.

Measure: sum of paid_amount, grouped by invoice currency. Kept separate from Payment Entry receipts to avoid double counting.

### Open receivables · current

Source: **Sales Invoice**.

Filters: submitted, non-return invoices with outstanding_amount greater than zero.

Measure: sum of outstanding_amount, grouped by party_account_currency. ERPNext stores this balance in party-account currency, which can differ from invoice currency.

### Overdue invoices

Source: **Sales Invoice**.

Filters: submitted, non-return invoices with positive outstanding_amount and due_date before today.

Display: total overdue count plus the eight oldest due invoices, with a direct link to each Sales Invoice. Balance is displayed in party-account currency.

## Permissions

- Check read permission independently for Sales Invoice and Payment Entry.
- Use permission-aware frappe.get_list calls for all reads so standard DocType and user-specific query permissions are applied.
- Never use frappe.get_all, raw SQL or ignore_permissions for these metrics.
- When a source is unavailable, render “Not available for your account”; do not show zero as if the query succeeded.

## Acceptance criteria and tests

| ID | Acceptance criterion | Validation |
|---|---|---|
| D2-AC1 | Submitted non-return invoices in the rolling 30-day period are grouped by invoice currency | test_sales_compass_returns_permission_filtered_lead_and_opportunity_metrics |
| D2-AC2 | Open balances use party-account currency, not invoice currency | Same unit test uses different invoice and party currencies |
| D2-AC3 | Customer receipts are limited to submitted Receive Payment Entries for Customer parties and grouped by receiving-account currency | Same unit test |
| D2-AC4 | POS receipts are shown separately from Payment Entry receipts | Same unit test |
| D2-AC5 | Overdue count and oldest invoices use current positive outstanding balances and due dates before today | Same unit test |
| D2-AC6 | Missing source permissions make the corresponding section unavailable | test_billing_marks_sales_invoice_source_unavailable_without_permission and test_billing_marks_payment_entry_receipts_unavailable_without_permission |
| D2-AC7 | Frappe v16 aggregate fields use structured COUNT/SUM syntax | test_billing_uses_structured_aggregate_fields_on_frappe_v16 |
| D2-AC8 | An authenticated user can load the real Desk page and receive its billing payload | e2e/sahdev-dashboard.spec.ts |

## Risks and open validation

- Site-specific role permissions may intentionally hide invoices or payment entries; this must be checked with Sales User and Sales Manager accounts.
- ERPNext customizations may alter DocType field availability. The API checks metadata and marks unsupported sections unavailable.
- Live financial totals must be reconciled against Sales Invoice and Payment Entry reports on the target site before managers rely on them.
