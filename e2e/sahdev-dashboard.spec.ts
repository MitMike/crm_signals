import { expect, test, type Page } from "@playwright/test";

const dashboardMethod = "**/api/method/crm_signals.api.get_sales_compass_data*";

async function loginAsAdministrator(page: Page) {
    await page.goto("/login");
    await page.locator("#login_email").fill(
        process.env.FRAPPE_USER || "Administrator"
    );
    await page.locator("#login_password").fill(
        process.env.FRAPPE_PASSWORD || "admin"
    );
    await page.locator('button[type="submit"]').click();

    await expect
        .poll(
            async () => {
                const response = await page.request.get(
                    "/api/method/frappe.auth.get_logged_user"
                );
                if (!response.ok()) return "";
                const payload = await response.json();
                return payload.message || "";
            },
            { timeout: 30_000 }
        )
        .toBe(process.env.FRAPPE_USER || "Administrator");
}

function dashboardPayload(overrides: Record<string, unknown> = {}) {
    return {
        leads: {
            available: true,
            created_last_30_days: 2,
            active: 4
        },
        opportunities: {
            available: true,
            total_count: 2,
            active_count: 2,
            stages: [{ status: "Open", total: 2 }],
            pipeline_value_available: true,
            pipeline_by_currency: [
                { currency: "INR", total_amount: 100000 },
                { currency: "USD", total_amount: 1200 }
            ],
            recent: []
        },
        billing: {
            available: true,
            period_days: 30,
            invoiced_available: true,
            invoiced_by_currency: [
                { currency: "INR", total_amount: 100000, record_count: 2 },
                { currency: "USD", total_amount: 200, record_count: 1 }
            ],
            outstanding_available: true,
            outstanding_by_currency: [
                { currency: "INR", total_amount: 25000, record_count: 1 }
            ],
            customer_receipts_available: true,
            customer_receipts_by_currency: [
                { currency: "INR", total_amount: 75000, record_count: 2 }
            ],
            pos_receipts_available: true,
            pos_receipts_by_currency: [
                { currency: "INR", total_amount: 5000, record_count: 1 }
            ],
            overdue_available: true,
            overdue_count: 1,
            overdue_invoices: [
                {
                    name: "ACC-SINV-E2E-0001",
                    customer: "E2E-CUSTOMER",
                    customer_name: "E2E Customer",
                    due_date: "2026-10-01",
                    party_account_currency: "INR",
                    currency: "INR",
                    outstanding_amount: 25000
                }
            ]
        },
        ...overrides
    };
}

async function mockDashboard(page: Page, message: Record<string, unknown>) {
    await page.route(dashboardMethod, (route) =>
        route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ message })
        })
    );
}

test(
    "Administrator can open the live Executive Compass and read billing data",
    async ({ page }) => {
    const pageErrors: string[] = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));

    await loginAsAdministrator(page);

    const dashboardResponsePromise = page.waitForResponse(
        (response) =>
            response.url().includes(
                "/api/method/crm_signals.api.get_sales_compass_data"
            ),
        { timeout: 30_000 }
    );

    await page.goto("/app/sahdev-dashboard");

    const dashboardResponse = await dashboardResponsePromise;
    expect(dashboardResponse.ok()).toBeTruthy();

    const payload = await dashboardResponse.json();
    expect(payload.message.opportunities.available).toBe(true);
    expect(payload.message.billing.available).toBe(true);
    expect(payload.message.billing.invoiced_available).toBe(true);
    expect(payload.message.billing.outstanding_available).toBe(true);
    expect(payload.message.billing.customer_receipts_available).toBe(true);
    expect(payload.message.billing.pos_receipts_available).toBe(true);
    expect(payload.message.billing.overdue_available).toBe(true);

    await expect(
        page.getByRole("heading", { name: "Executive Compass" })
    ).toBeVisible();
    await expect(
        page.getByRole("heading", { name: "Billing realization" })
    ).toBeVisible();
    await expect(
        page.getByRole("heading", { name: "Overdue customer invoices" })
    ).toBeVisible();
    await expect(
        page.getByText("Invoice and POS amounts use invoice currency.", {
            exact: false
        })
    ).toBeVisible();

    expect(pageErrors).toEqual([]);
});

test(
    "billing cards keep currencies separate and overdue invoices drill down",
    async ({ page }) => {
    await loginAsAdministrator(page);
    await mockDashboard(page, dashboardPayload());

    await page.goto("/app/sahdev-dashboard");

    const billing = page.locator(".sahdev-billing-section");
    await expect(
        billing.getByRole("heading", { name: "Billing realization" })
    ).toBeVisible();
    await expect(billing).toContainText("INR");
    await expect(billing).toContainText("USD");
    await expect(billing).toContainText(
        "Invoice and POS amounts use invoice currency"
    );

    const overdueInvoice = page.locator(".sahdev-invoice-row");
    await expect(overdueInvoice).toBeVisible();
    await expect(overdueInvoice).toContainText("E2E Customer");
    await expect(overdueInvoice).toContainText("ACC-SINV-E2E-0001");

    await overdueInvoice.click();
    await expect(page).toHaveURL(
        /\/app\/sales-invoice\/ACC-SINV-E2E-0001/
    );
});

test(
    "empty ERPNext datasets show explicit empty states",
    async ({ page }) => {
    await loginAsAdministrator(page);
    const empty = dashboardPayload({
        opportunities: {
            available: true,
            total_count: 0,
            active_count: 0,
            stages: [],
            pipeline_value_available: true,
            pipeline_by_currency: [],
            recent: []
        },
        billing: {
            available: true,
            period_days: 30,
            invoiced_available: true,
            invoiced_by_currency: [],
            outstanding_available: true,
            outstanding_by_currency: [],
            customer_receipts_available: true,
            customer_receipts_by_currency: [],
            pos_receipts_available: true,
            pos_receipts_by_currency: [],
            overdue_available: true,
            overdue_count: 0,
            overdue_invoices: []
        }
    });
    await mockDashboard(page, empty);

    await page.goto("/app/sahdev-dashboard");

    await expect(page.getByText("No overdue open invoices.")).toBeVisible();
    await expect(
        page.getByText("No transactions in this period")
    ).toHaveCount(4);
    await expect(page.getByText("No active opportunities found.")).toBeVisible();
});

test(
    "dashboard renders a useful message when its API is forbidden",
    async ({ page }) => {
    await loginAsAdministrator(page);
    await page.route(dashboardMethod, (route) =>
        route.fulfill({
            status: 403,
            contentType: "application/json",
            body: JSON.stringify({
                exception: "frappe.exceptions.PermissionError: Not permitted"
            })
        })
    );

    await page.goto("/app/sahdev-dashboard");

    await expect(
        page.getByText(
            "Unable to load the sales compass. Check your Lead and Opportunity access, then refresh."
        )
    ).toBeVisible();
});


test(
    "CRM Signals Desk dashboard loads its live permission-filtered API",
    async ({ page }) => {
    await loginAsAdministrator(page);

    const responsePromise = page.waitForResponse(
        (response) =>
            response.url().includes(
                "/api/method/crm_signals.api.get_dashboard_data"
            ),
        { timeout: 30_000 }
    );
    await page.goto("/app/crm-signals-dashboard");

    const response = await responsePromise;
    expect(response.ok()).toBeTruthy();
    const payload = await response.json();
    expect(payload.message.stats).toEqual(
        expect.objectContaining({
            total: expect.any(Number),
            unread: expect.any(Number),
            high_priority: expect.any(Number),
            last_7_days: expect.any(Number)
        })
    );

    await expect(
        page.getByRole("heading", { name: "CRM Signals Dashboard" })
    ).toBeVisible();
    await expect(
        page.getByRole("heading", { name: "Sales activity at a glance" })
    ).toBeVisible();
    await expect(
        page.getByRole("heading", { name: "Signals by type" })
    ).toBeVisible();
    await expect(
        page.getByRole("heading", { name: "Recent activity" })
    ).toBeVisible();
});

test(
    "Guest users are redirected from Desk and cannot call either dashboard API",
    async ({ page, request }) => {
    const salesCompass = await request.get(
        "/api/method/crm_signals.api.get_sales_compass_data"
    );
    const signals = await request.get(
        "/api/method/crm_signals.api.get_dashboard_data"
    );

    for (const response of [salesCompass, signals]) {
        expect(response.status()).toBeGreaterThanOrEqual(400);
        const body = await response.text();
        expect(body).toMatch(/Authentication is required|AuthenticationError/);
    }

    await page.goto("/app/sahdev-dashboard");
    await expect(page).toHaveURL(/\/login(?:\?|$)/);
});
