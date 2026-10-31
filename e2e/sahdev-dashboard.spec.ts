import { expect, test, type Page } from "@playwright/test";

const dashboardMethod = "**/api/method/crm_signals.api.get_sales_compass_data*";

async function loginAs(page: Page, username: string, password: string) {
    await page.goto("/login");
    await page.locator("#login_email").fill(username);
    await page.locator("#login_password").fill(password);
    await page.locator('.form-login button[type="submit"]').click();

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
        .toBe(username);
}

async function loginAsAdministrator(page: Page) {
    await loginAs(
        page,
        process.env.FRAPPE_USER || "Administrator",
        process.env.FRAPPE_PASSWORD || "admin"
    );
}

async function createRoleUser(
    page: Page,
    email: string,
    firstName: string,
    role: string,
    password: string
) {
    const response = await page.request.post("/api/resource/User", {
        data: {
            email,
            first_name: firstName,
            enabled: 1,
            user_type: "System User",
            new_password: password,
            send_welcome_email: 0,
            roles: [{ role }]
        }
    });
    expect(response.ok()).toBeTruthy();
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

test("Live Executive Compass loads billing data", async ({ page }) => {
    const pageErrors: string[] = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));

    await loginAsAdministrator(page);

    const dashboardResponsePromise = page.waitForResponse(
        (response) =>
            response
                .url()
                .includes("/api/method/crm_signals.api.get_sales_compass_data"),
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

test("Billing cards preserve currencies and drill down", async ({ page }) => {
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
    await expect(page).toHaveURL(/\/app\/sales-invoice\/ACC-SINV-E2E-0001/);
});

test("Empty ERPNext datasets render empty states", async ({ page }) => {
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
    await expect(page.getByText("No transactions in this period")).toHaveCount(
        4
    );
    await expect(
        page.getByText("No active opportunities found.")
    ).toBeVisible();
});

test("API permission failures render a helpful message", async ({ page }) => {
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

test("CRM Signals dashboard loads its live API", async ({ page }) => {
    await loginAsAdministrator(page);

    const responsePromise = page.waitForResponse(
        (response) =>
            response
                .url()
                .includes("/api/method/crm_signals.api.get_dashboard_data"),
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

test("Sales User can open the Executive Compass", async ({ page }) => {
    await loginAsAdministrator(page);
    const email = "e2e-sales-user@example.com";
    const password = "E2E-Sales-User-Password-2026";
    await createRoleUser(page, email, "E2E Sales User", "Sales User", password);

    await page.context().clearCookies();
    await loginAs(page, email, password);

    const rolesResponse = await page.request.get(
        "/api/method/frappe.core.doctype.user.user.get_current_user_roles"
    );
    expect(rolesResponse.ok()).toBeTruthy();
    expect((await rolesResponse.json()).message).toContain("Sales User");

    await page.goto("/app/sahdev-dashboard");
    await expect(
        page.getByRole("heading", { name: "Executive Compass" })
    ).toBeVisible();
});

test("Users without a Sales role cannot open the Compass", async ({ page }) => {
    await loginAsAdministrator(page);
    const email = "e2e-employee@example.com";
    const password = "E2E-Employee-Password-2026";
    await createRoleUser(page, email, "E2E Employee", "Employee", password);

    await page.context().clearCookies();
    await loginAs(page, email, password);

    const rolesResponse = await page.request.get(
        "/api/method/frappe.core.doctype.user.user.get_current_user_roles"
    );
    expect(rolesResponse.ok()).toBeTruthy();
    const roles = (await rolesResponse.json()).message;
    expect(roles).toContain("Employee");
    expect(roles).not.toContain("Sales User");
    expect(roles).not.toContain("Sales Manager");
    expect(roles).not.toContain("System Manager");

    await page.goto("/app/sahdev-dashboard");
    await expect(
        page.getByRole("heading", { name: "Executive Compass" })
    ).toHaveCount(0);
});

test("Guest access is rejected", async ({ page, request }) => {
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
