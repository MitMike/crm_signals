import { expect, test, type Page } from "@playwright/test";

const dashboardMethod = "**/api/method/crm_signals.api.get_sales_compass_data*";
const crmSignalsDashboardMethod =
    "**/api/method/crm_signals.api.get_dashboard_data*";

async function loginAs(page: Page, username: string, password: string) {
    await page.goto("/login");

    const loginResponsePromise = page.waitForResponse(
        (response) => {
            const url = new URL(response.url());
            return (
                ["/login", "/api/method/login"].includes(url.pathname) &&
                response.request().method() === "POST"
            );
        },
        { timeout: 30_000 }
    );

    await page.locator("#login_email").fill(username);
    await page.locator("#login_password").fill(password);
    await page.locator('.form-login button[type="submit"]').click();

    const loginResponse = await loginResponsePromise;
    expect(loginResponse.ok()).toBeTruthy();

    await expect
        .poll(
            async () => {
                const sid = (await page.context().cookies()).find(
                    (cookie) => cookie.name === "sid"
                );
                return Boolean(sid && sid.value && sid.value !== "Guest");
            },
            { timeout: 15_000 }
        )
        .toBe(true);

    // Frappe sets the session cookie before completing its client-side
    // redirect. Do not let the next test action race that navigation.
    await page.waitForURL(
        (url) =>
            ["/app", "/desk"].some(
                (root) =>
                    url.pathname === root || url.pathname.startsWith(`${root}/`)
            ),
        { waitUntil: "domcontentloaded", timeout: 30_000 }
    );
}

async function loginAsAdministrator(page: Page) {
    await loginAs(
        page,
        process.env.FRAPPE_USER || "Administrator",
        process.env.FRAPPE_PASSWORD || "admin"
    );
}

async function frappeMethodGet(
    page: Page,
    method: string,
    params: Record<string, string>
): Promise<{ status: number; body: unknown }> {
    return page.evaluate(
        async ({ method, params }) => {
            const query = new URLSearchParams(params);
            const response = await fetch(
                "/api/method/" + method + "?" + query.toString(),
                { credentials: "same-origin" }
            );
            const body = await response.json().catch(() => ({}));
            return { status: response.status, body };
        },
        { method, params }
    );
}

async function openCrmSignalForm(page: Page, name: string) {
    const responsePromise = page.waitForResponse(
        (response) => {
            const url = new URL(response.url());
            return (
                url.pathname === "/api/method/frappe.desk.form.load.getdoc" &&
                url.searchParams.get("doctype") === "CRM Signal" &&
                url.searchParams.get("name") === name &&
                response.request().method() === "GET"
            );
        },
        { timeout: 30_000 }
    );

    // The Desk shell can return 200 even when the document loader denies this record.
    await page.goto(`/app/crm-signal/${encodeURIComponent(name)}`);
    return responsePromise;
}

function dashboardPayload(overrides: Record<string, unknown> = {}) {
    return {
        leads: {
            available: true,
            created_last_30_days: 2,
            active_available: true,
            active: 4
        },
        opportunities: {
            available: true,
            total_count: 2,
            status_available: true,
            active_count: 2,
            stages_available: true,
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

async function frappeMethodGetWithToken(
    method: string,
    params: Record<string, string>,
    apiKey: string,
    apiSecret: string
): Promise<{ status: number; body: unknown }> {
    const baseUrl = process.env.BASE_URL;
    if (!baseUrl) throw new Error("BASE_URL is required for API-token E2E");

    const query = new URLSearchParams(params);
    // Node fetch has no browser cookie jar and is excluded from Playwright traces.
    const response = await fetch(
        new URL("/api/method/" + method + "?" + query.toString(), baseUrl),
        {
            headers: {
                Authorization: `token ${apiKey}:${apiSecret}`
            },
            redirect: "manual"
        }
    );
    const responseText = await response.text();
    let body: unknown = responseText;
    try {
        body = JSON.parse(responseText);
    } catch {
        // Preserve non-JSON error bodies for the response-content assertion.
    }
    return { status: response.status, body };
}

async function frappeResourceGetWithToken(
    doctype: string,
    name: string | null,
    params: Record<string, string>,
    apiKey: string,
    apiSecret: string
): Promise<{ status: number; body: unknown }> {
    const baseUrl = process.env.BASE_URL;
    if (!baseUrl) throw new Error("BASE_URL is required for API-token E2E");

    const resourcePath =
        `/api/resource/${encodeURIComponent(doctype)}` +
        (name ? `/${encodeURIComponent(name)}` : "");
    const query = new URLSearchParams(params).toString();
    const url = new URL(resourcePath + (query ? `?${query}` : ""), baseUrl);
    // Node fetch has no browser cookie jar and is excluded from Playwright traces.
    const response = await fetch(url, {
        headers: {
            Accept: "application/json",
            Authorization: `token ${apiKey}:${apiSecret}`
        },
        redirect: "manual"
    });
    const responseText = await response.text();
    let body: unknown = responseText;
    try {
        body = JSON.parse(responseText);
    } catch {
        // Preserve non-JSON error bodies for the response-content assertion.
    }
    return { status: response.status, body };
}

async function getSalesUserSignalPair(page: Page) {
    const linkedMessage = "CRM Signals E2E linked restricted signal";
    const unlinkedMessage = "CRM Signals E2E unlinked owned signal";
    const fixtureResponse = await frappeMethodGet(
        page,
        "frappe.client.get_list",
        {
            doctype: "CRM Signal",
            fields: JSON.stringify(["name", "message"]),
            filters: JSON.stringify([
                ["message", "in", [linkedMessage, unlinkedMessage]]
            ]),
            limit_page_length: "10"
        }
    );
    expect(fixtureResponse.status).toBe(200);
    const fixtureRows =
        (
            fixtureResponse.body as {
                message?: Array<{ name: string; message: string }>;
            }
        ).message || [];
    expect(fixtureRows).toHaveLength(2);

    const linkedSignal = fixtureRows.find(
        (row) => row.message === linkedMessage
    );
    const unlinkedSignal = fixtureRows.find(
        (row) => row.message === unlinkedMessage
    );
    if (!linkedSignal || !unlinkedSignal) {
        throw new Error("Sales User permission fixtures are incomplete");
    }
    return { linkedSignal, unlinkedSignal, linkedMessage, unlinkedMessage };
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
    await expect(page).toHaveURL(
        /\/desk\/(?:accounts\/)?sales-invoice\/ACC-SINV-E2E-0001/
    );
});

test("Empty ERPNext datasets render empty states", async ({ page }) => {
    await loginAsAdministrator(page);
    const empty = dashboardPayload({
        opportunities: {
            available: true,
            total_count: 0,
            status_available: true,
            active_count: 0,
            stages_available: true,
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

test("Status-dependent metrics show unavailable states when status metadata is missing", async ({
    page
}) => {
    await loginAsAdministrator(page);
    const payload = dashboardPayload({
        leads: {
            available: true,
            created_last_30_days: 2,
            active_available: false,
            active: null
        },
        opportunities: {
            available: true,
            total_count: 2,
            status_available: false,
            active_count: null,
            stages_available: false,
            stages: [],
            pipeline_value_available: false,
            pipeline_by_currency: [],
            recent: []
        }
    });
    await mockDashboard(page, payload);

    await page.goto("/app/sahdev-dashboard");

    await expect(page.getByText("Lead status field unavailable")).toBeVisible();
    await expect(
        page.getByText("Opportunity status field unavailable")
    ).toBeVisible();
    await expect(
        page.getByText(
            "Opportunity status field is unavailable; stage distribution cannot be calculated."
        )
    ).toBeVisible();
    await expect(
        page.getByText("Status field unavailable", { exact: true })
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
        page.getByRole("heading", { name: "Sales activity at a glance" })
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

test("CRM Signals dashboard keeps its horizontal inset at desktop and mobile widths", async ({
    page
}) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await loginAsAdministrator(page);
    await page.route(crmSignalsDashboardMethod, (route) =>
        route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                message: {
                    stats: {
                        total: 0,
                        unread: 0,
                        high_priority: 0,
                        last_7_days: 0
                    },
                    by_type: [],
                    recent: []
                }
            })
        })
    );

    await page.goto("/app/crm-signals-dashboard");
    const dashboard = page.locator(".crm-signals-dashboard");
    await expect(
        page.getByRole("heading", { name: "Sales activity at a glance" })
    ).toBeVisible();

    const desktopPadding = await dashboard.evaluate((element) => {
        const styles = window.getComputedStyle(element);
        return [styles.paddingLeft, styles.paddingRight];
    });
    expect(desktopPadding).toEqual(["24px", "24px"]);

    await page.setViewportSize({ width: 390, height: 844 });
    const mobilePadding = await dashboard.evaluate((element) => {
        const styles = window.getComputedStyle(element);
        return [styles.paddingLeft, styles.paddingRight];
    });
    expect(mobilePadding).toEqual(["12px", "12px"]);
});

test("High-Value Quote activity opens its permitted source Quotation", async ({
    page
}) => {
    await loginAsAdministrator(page);
    await page.route(crmSignalsDashboardMethod, (route) =>
        route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                message: {
                    stats: {
                        total: 1,
                        unread: 1,
                        high_priority: 1,
                        last_7_days: 1
                    },
                    by_type: [{ signal_type: "High-Value Quote", total: 1 }],
                    recent: [
                        {
                            name: "SIG-HIGHLIGHT-E2E",
                            creation: "2026-11-02 09:00:00",
                            signal_type: "High-Value Quote",
                            priority: "High",
                            message:
                                "High-value quotation QTN-HIGHLIGHT-E2E submitted",
                            lead: "LEAD-HIGHLIGHT-E2E",
                            customer: null,
                            is_read: 0,
                            source_doctype: "Quotation",
                            source_name: "QTN-HIGHLIGHT-E2E"
                        }
                    ]
                }
            })
        })
    );

    await page.goto("/app/crm-signals-dashboard");
    const signal = page.locator(".crm-signal-row").filter({
        hasText: "High-Value Quote"
    });
    await expect(signal).toContainText("Quotation: QTN-HIGHLIGHT-E2E");
    await signal.click();
    await expect(page).toHaveURL(
        /\/desk\/(?:selling\/)?quotation\/QTN-HIGHLIGHT-E2E/
    );
});
test("Sales User can open the Executive Compass", async ({ page }) => {
    await loginAsAdministrator(page);
    const email = process.env.E2E_SALES_USER || "e2e-sales-user@example.com";
    const password = process.env.E2E_SALES_PASSWORD;
    expect(password).toBeTruthy();
    await page.context().clearCookies();
    await loginAs(page, email, password!);

    const identity = await frappeMethodGet(
        page,
        "frappe.auth.get_logged_user",
        {}
    );
    expect(identity.status).toBe(200);
    expect((identity.body as { message?: string }).message).toBe(email);

    await page.goto("/app/sahdev-dashboard");
    await expect(
        page.getByRole("heading", { name: "Executive Compass" })
    ).toBeVisible();
});

test("Sales User HTTP API respects linked Lead User Permission", async ({
    page
}) => {
    await loginAsAdministrator(page);

    const linkedMessage = "CRM Signals E2E linked restricted signal";
    const unlinkedMessage = "CRM Signals E2E unlinked owned signal";
    const fixtureResponse = await frappeMethodGet(
        page,
        "frappe.client.get_list",
        {
            doctype: "CRM Signal",
            fields: JSON.stringify(["name", "message"]),
            filters: JSON.stringify([
                ["message", "in", [linkedMessage, unlinkedMessage]]
            ]),
            limit_page_length: "10"
        }
    );
    expect(fixtureResponse.status).toBe(200);
    const fixtureRows =
        (
            fixtureResponse.body as {
                message?: Array<{ name: string; message: string }>;
            }
        ).message || [];
    expect(fixtureRows).toHaveLength(2);

    const linkedSignal = fixtureRows.find(
        (row) => row.message === linkedMessage
    );
    const unlinkedSignal = fixtureRows.find(
        (row) => row.message === unlinkedMessage
    );
    expect(linkedSignal).toBeTruthy();
    expect(unlinkedSignal).toBeTruthy();

    const email = process.env.E2E_SALES_USER || "e2e-sales-user@example.com";
    const password = process.env.E2E_SALES_PASSWORD;
    expect(password).toBeTruthy();
    await page.context().clearCookies();
    await loginAs(page, email, password!);

    const identity = await frappeMethodGet(
        page,
        "frappe.auth.get_logged_user",
        {}
    );
    expect(identity.status).toBe(200);
    expect((identity.body as { message?: string }).message).toBe(email);

    const restrictedRead = await frappeMethodGet(page, "frappe.client.get", {
        doctype: "CRM Signal",
        name: linkedSignal!.name
    });
    expect(restrictedRead.status).toBe(403);

    const allowedRead = await frappeMethodGet(page, "frappe.client.get", {
        doctype: "CRM Signal",
        name: unlinkedSignal!.name
    });
    expect(allowedRead.status).toBe(200);
    expect(
        (allowedRead.body as { message?: { name?: string } }).message?.name
    ).toBe(unlinkedSignal!.name);

    const listResponse = await frappeMethodGet(page, "frappe.client.get_list", {
        doctype: "CRM Signal",
        fields: JSON.stringify(["name"]),
        filters: JSON.stringify({
            name: ["in", [linkedSignal!.name, unlinkedSignal!.name]]
        }),
        limit_page_length: "10"
    });
    expect(listResponse.status).toBe(200);
    const visibleNames =
        (
            listResponse.body as { message?: Array<{ name: string }> }
        ).message?.map((row) => row.name) || [];
    expect(visibleNames).toEqual([unlinkedSignal!.name]);
});

test("Sales User API token respects linked Lead User Permission", async ({
    page
}) => {
    await loginAsAdministrator(page);

    const linkedMessage = "CRM Signals E2E linked restricted signal";
    const unlinkedMessage = "CRM Signals E2E unlinked owned signal";
    const fixtureResponse = await frappeMethodGet(
        page,
        "frappe.client.get_list",
        {
            doctype: "CRM Signal",
            fields: JSON.stringify(["name", "message"]),
            filters: JSON.stringify([
                ["message", "in", [linkedMessage, unlinkedMessage]]
            ]),
            limit_page_length: "10"
        }
    );
    expect(fixtureResponse.status).toBe(200);
    const fixtureRows =
        (
            fixtureResponse.body as {
                message?: Array<{ name: string; message: string }>;
            }
        ).message || [];
    expect(fixtureRows).toHaveLength(2);

    const linkedSignal = fixtureRows.find(
        (row) => row.message === linkedMessage
    );
    const unlinkedSignal = fixtureRows.find(
        (row) => row.message === unlinkedMessage
    );
    expect(linkedSignal).toBeTruthy();
    expect(unlinkedSignal).toBeTruthy();

    const apiKey = process.env.E2E_SALES_API_KEY;
    const apiSecret = process.env.E2E_SALES_API_SECRET;
    const email = process.env.E2E_SALES_USER || "e2e-sales-user@example.com";
    expect(apiKey).toBeTruthy();
    expect(apiSecret).toBeTruthy();

    const identity = await frappeMethodGetWithToken(
        "frappe.auth.get_logged_user",
        {},
        apiKey!,
        apiSecret!
    );
    expect(identity.status).toBe(200);
    expect((identity.body as { message?: string }).message).toBe(email);

    const restrictedRead = await frappeMethodGetWithToken(
        "frappe.client.get",
        { doctype: "CRM Signal", name: linkedSignal!.name },
        apiKey!,
        apiSecret!
    );
    expect(restrictedRead.status).toBe(403);
    const restrictedBody = JSON.stringify(restrictedRead.body) ?? "";
    expect(restrictedBody).not.toContain(linkedMessage);

    const allowedRead = await frappeMethodGetWithToken(
        "frappe.client.get",
        { doctype: "CRM Signal", name: unlinkedSignal!.name },
        apiKey!,
        apiSecret!
    );
    expect(allowedRead.status).toBe(200);
    const allowedBody = allowedRead.body as {
        message?: { name?: string; message?: string };
    };
    expect(allowedBody.message?.name).toBe(unlinkedSignal!.name);
    expect(allowedBody.message?.message).toBe(unlinkedMessage);

    const listResponse = await frappeMethodGetWithToken(
        "frappe.client.get_list",
        {
            doctype: "CRM Signal",
            fields: JSON.stringify(["name"]),
            filters: JSON.stringify({
                name: ["in", [linkedSignal!.name, unlinkedSignal!.name]]
            }),
            limit_page_length: "10"
        },
        apiKey!,
        apiSecret!
    );
    expect(listResponse.status).toBe(200);
    const visibleNames =
        (
            listResponse.body as { message?: Array<{ name: string }> }
        ).message?.map((row) => row.name) || [];
    expect(visibleNames).toEqual([unlinkedSignal!.name]);
});

test("Sales User REST resource API token respects linked Lead User Permission", async ({
    page
}) => {
    await loginAsAdministrator(page);

    const linkedMessage = "CRM Signals E2E linked restricted signal";
    const unlinkedMessage = "CRM Signals E2E unlinked owned signal";
    const fixtureResponse = await frappeMethodGet(
        page,
        "frappe.client.get_list",
        {
            doctype: "CRM Signal",
            fields: JSON.stringify(["name", "message"]),
            filters: JSON.stringify([
                ["message", "in", [linkedMessage, unlinkedMessage]]
            ]),
            limit_page_length: "10"
        }
    );
    expect(fixtureResponse.status).toBe(200);
    const fixtureRows =
        (
            fixtureResponse.body as {
                message?: Array<{ name: string; message: string }>;
            }
        ).message || [];
    expect(fixtureRows).toHaveLength(2);

    const linkedSignal = fixtureRows.find(
        (row) => row.message === linkedMessage
    );
    const unlinkedSignal = fixtureRows.find(
        (row) => row.message === unlinkedMessage
    );
    expect(linkedSignal).toBeTruthy();
    expect(unlinkedSignal).toBeTruthy();

    const apiKey = process.env.E2E_SALES_API_KEY;
    const apiSecret = process.env.E2E_SALES_API_SECRET;
    const email = process.env.E2E_SALES_USER || "e2e-sales-user@example.com";
    expect(apiKey).toBeTruthy();
    expect(apiSecret).toBeTruthy();

    const identity = await frappeMethodGetWithToken(
        "frappe.auth.get_logged_user",
        {},
        apiKey!,
        apiSecret!
    );
    expect(identity.status).toBe(200);
    expect((identity.body as { message?: string }).message).toBe(email);

    const restrictedRead = await frappeResourceGetWithToken(
        "CRM Signal",
        linkedSignal!.name,
        {},
        apiKey!,
        apiSecret!
    );
    expect(restrictedRead.status).toBe(403);
    const restrictedBody = JSON.stringify(restrictedRead.body) ?? "";
    expect(restrictedBody).not.toContain(linkedMessage);

    const allowedRead = await frappeResourceGetWithToken(
        "CRM Signal",
        unlinkedSignal!.name,
        {},
        apiKey!,
        apiSecret!
    );
    expect(allowedRead.status).toBe(200);
    const allowedData = (
        allowedRead.body as {
            data?: { name?: string; message?: string };
        }
    ).data;
    expect(allowedData?.name).toBe(unlinkedSignal!.name);
    expect(allowedData?.message).toBe(unlinkedMessage);

    const listResponse = await frappeResourceGetWithToken(
        "CRM Signal",
        null,
        {
            fields: JSON.stringify(["name"]),
            filters: JSON.stringify([
                [
                    "CRM Signal",
                    "name",
                    "in",
                    [linkedSignal!.name, unlinkedSignal!.name]
                ]
            ]),
            limit_page_length: "10"
        },
        apiKey!,
        apiSecret!
    );
    expect(listResponse.status).toBe(200);
    const visibleNames =
        (
            listResponse.body as {
                data?: Array<{ name: string }>;
            }
        ).data?.map((row) => row.name) || [];
    expect(visibleNames).toEqual([unlinkedSignal!.name]);
});

test("Sales User report view and CSV export respect linked Lead User Permission", async ({
    page
}) => {
    await loginAsAdministrator(page);

    const { linkedSignal, unlinkedSignal, linkedMessage, unlinkedMessage } =
        await getSalesUserSignalPair(page);

    const apiKey = process.env.E2E_SALES_API_KEY;
    const apiSecret = process.env.E2E_SALES_API_SECRET;
    const email = process.env.E2E_SALES_USER || "e2e-sales-user@example.com";
    expect(apiKey).toBeTruthy();
    expect(apiSecret).toBeTruthy();

    const identity = await frappeMethodGetWithToken(
        "frappe.auth.get_logged_user",
        {},
        apiKey!,
        apiSecret!
    );
    expect(identity.status).toBe(200);
    expect((identity.body as { message?: string }).message).toBe(email);

    const filters = JSON.stringify([
        ["CRM Signal", "name", "in", [linkedSignal!.name, unlinkedSignal!.name]]
    ]);
    const reportView = await frappeMethodGetWithToken(
        "frappe.desk.reportview.get_list",
        {
            doctype: "CRM Signal",
            fields: JSON.stringify(["name", "message"]),
            filters,
            limit_page_length: "10"
        },
        apiKey!,
        apiSecret!
    );
    expect(reportView.status).toBe(200);
    const reportRows =
        (
            reportView.body as {
                message?: Array<{ name: string; message: string }>;
            }
        ).message || [];
    expect(reportRows.map((row) => row.name)).toEqual([unlinkedSignal!.name]);
    expect(reportRows[0]?.message).toBe(unlinkedMessage);

    const exportResponse = await frappeMethodGetWithToken(
        "frappe.desk.reportview.export_query",
        {
            doctype: "CRM Signal",
            fields: JSON.stringify(["name", "message"]),
            filters,
            file_format_type: "CSV",
            title: "CRM Signals E2E permission export",
            csv_delimiter: ",",
            csv_quoting: "2"
        },
        apiKey!,
        apiSecret!
    );
    expect(exportResponse.status).toBe(200);
    expect(typeof exportResponse.body).toBe("string");
    const csv = exportResponse.body as string;
    expect(csv).toContain(unlinkedSignal!.name);
    expect(csv).toContain(unlinkedMessage);
    expect(csv).not.toContain(linkedSignal!.name);
    expect(csv).not.toContain(linkedMessage);
});


test("Sales User CRM Signals dashboard API respects linked Lead User Permission", async ({
    page
}) => {
    await loginAsAdministrator(page);

    const { linkedSignal, unlinkedSignal, linkedMessage, unlinkedMessage } =
        await getSalesUserSignalPair(page);
    const apiKey = process.env.E2E_SALES_API_KEY;
    const apiSecret = process.env.E2E_SALES_API_SECRET;
    const email = process.env.E2E_SALES_USER || "e2e-sales-user@example.com";
    expect(apiKey).toBeTruthy();
    expect(apiSecret).toBeTruthy();

    const identity = await frappeMethodGetWithToken(
        "frappe.auth.get_logged_user",
        {},
        apiKey!,
        apiSecret!
    );
    expect(identity.status).toBe(200);
    expect((identity.body as { message?: string }).message).toBe(email);

    const dashboard = await frappeMethodGetWithToken(
        "crm_signals.api.get_dashboard_data",
        {},
        apiKey!,
        apiSecret!
    );
    expect(dashboard.status).toBe(200);
    const recent = (
        dashboard.body as {
            message?: {
                recent?: Array<{ name: string; message: string }>;
            };
        }
    ).message?.recent || [];
    expect(recent.some((row) => row.name === unlinkedSignal!.name)).toBe(true);
    expect(recent.some((row) => row.name === linkedSignal!.name)).toBe(false);
    const recentText = JSON.stringify(recent);
    expect(recentText).toContain(unlinkedMessage);
    expect(recentText).not.toContain(linkedMessage);
});

test("Sales User CRM Signal form permission boundary", async ({ page }) => {
    await loginAsAdministrator(page);

    const linkedMessage = "CRM Signals E2E linked restricted signal";
    const unlinkedMessage = "CRM Signals E2E unlinked owned signal";
    const fixtureResponse = await frappeMethodGet(
        page,
        "frappe.client.get_list",
        {
            doctype: "CRM Signal",
            fields: JSON.stringify(["name", "message"]),
            filters: JSON.stringify([
                ["message", "in", [linkedMessage, unlinkedMessage]]
            ]),
            limit_page_length: "10"
        }
    );
    expect(fixtureResponse.status).toBe(200);
    const fixtureRows =
        (
            fixtureResponse.body as {
                message?: Array<{ name: string; message: string }>;
            }
        ).message || [];
    expect(fixtureRows).toHaveLength(2);

    const linkedSignal = fixtureRows.find(
        (row) => row.message === linkedMessage
    );
    const unlinkedSignal = fixtureRows.find(
        (row) => row.message === unlinkedMessage
    );
    expect(linkedSignal).toBeTruthy();
    expect(unlinkedSignal).toBeTruthy();

    const email = process.env.E2E_SALES_USER || "e2e-sales-user@example.com";
    const password = process.env.E2E_SALES_PASSWORD;
    expect(password).toBeTruthy();
    await page.context().clearCookies();
    await loginAs(page, email, password!);

    const identity = await frappeMethodGet(
        page,
        "frappe.auth.get_logged_user",
        {}
    );
    expect(identity.status).toBe(200);
    expect((identity.body as { message?: string }).message).toBe(email);

    const restrictedFormResponse = await openCrmSignalForm(
        page,
        linkedSignal!.name
    );
    expect(restrictedFormResponse.status()).toBe(403);
    const restrictedBody = await restrictedFormResponse.text();
    expect(restrictedBody).not.toContain(linkedMessage);

    const allowedFormResponse = await openCrmSignalForm(
        page,
        unlinkedSignal!.name
    );
    expect(allowedFormResponse.status()).toBe(200);
    const allowedBody = (await allowedFormResponse.json()) as {
        docs?: Array<{ doctype?: string; name?: string; message?: string }>;
    };
    const loadedSignal = allowedBody.docs?.find(
        (doc) =>
            doc.doctype === "CRM Signal" && doc.name === unlinkedSignal!.name
    );
    expect(loadedSignal?.message).toBe(unlinkedMessage);
});

test("Sales User print view respects linked Lead User Permission", async ({
    page
}) => {
    await loginAsAdministrator(page);

    const linkedMessage = "CRM Signals E2E linked restricted signal";
    const unlinkedMessage = "CRM Signals E2E unlinked owned signal";
    const fixtureResponse = await frappeMethodGet(
        page,
        "frappe.client.get_list",
        {
            doctype: "CRM Signal",
            fields: JSON.stringify(["name", "message"]),
            filters: JSON.stringify([
                ["message", "in", [linkedMessage, unlinkedMessage]]
            ]),
            limit_page_length: "10"
        }
    );
    expect(fixtureResponse.status).toBe(200);
    const fixtureRows =
        (
            fixtureResponse.body as {
                message?: Array<{ name: string; message: string }>;
            }
        ).message || [];
    expect(fixtureRows).toHaveLength(2);

    const linkedSignal = fixtureRows.find(
        (row) => row.message === linkedMessage
    );
    const unlinkedSignal = fixtureRows.find(
        (row) => row.message === unlinkedMessage
    );
    expect(linkedSignal).toBeTruthy();
    expect(unlinkedSignal).toBeTruthy();

    const email = process.env.E2E_SALES_USER || "e2e-sales-user@example.com";
    const password = process.env.E2E_SALES_PASSWORD;
    expect(password).toBeTruthy();
    await page.context().clearCookies();
    await loginAs(page, email, password!);

    const restrictedUrl = `/printview?doctype=CRM%20Signal&name=${encodeURIComponent(linkedSignal!.name)}&format=Standard&no_letterhead=1`;
    const restrictedResponse = await page.goto(restrictedUrl);
    expect(restrictedResponse?.status()).toBe(403);
    const restrictedBody = await restrictedResponse!.text();
    expect(restrictedBody).not.toContain(linkedMessage);

    const allowedUrl = `/printview?doctype=CRM%20Signal&name=${encodeURIComponent(unlinkedSignal!.name)}&format=Standard&no_letterhead=1`;
    const allowedResponse = await page.goto(allowedUrl);
    expect(allowedResponse?.status()).toBe(200);
    const allowedBody = await allowedResponse!.text();
    expect(allowedBody).toContain(unlinkedMessage);
});

test("Sales User and non-sales dashboard API permission boundaries", async ({ page }) => {
    await loginAsAdministrator(page);
    const email = process.env.E2E_EMPLOYEE_USER || "e2e-employee@example.com";
    const password = process.env.E2E_EMPLOYEE_PASSWORD;
    expect(password).toBeTruthy();
    await page.context().clearCookies();
    await loginAs(page, email, password!);

    const identity = await frappeMethodGet(
        page,
        "frappe.auth.get_logged_user",
        {}
    );
    expect(identity.status).toBe(200);
    expect((identity.body as { message?: string }).message).toBe(email);

    const compassResponse = await frappeMethodGet(
        page,
        "crm_signals.api.get_sales_compass_data",
        {}
    );
    expect(compassResponse.status).toBe(200);
    const compass = (
        compassResponse.body as {
            message?: {
                leads?: { available?: boolean };
                opportunities?: { available?: boolean };
                billing?: { available?: boolean };
                service?: { available?: boolean };
            };
        }
    ).message;
    expect(compass?.leads?.available).toBe(false);
    expect(compass?.opportunities?.available).toBe(false);
    expect(compass?.billing?.available).toBe(false);
    expect(compass?.service?.available).toBe(false);

    const signalsResponse = await frappeMethodGet(
        page,
        "crm_signals.api.get_dashboard_data",
        {}
    );
    expect(signalsResponse.status).toBe(403);
    const signalsText = JSON.stringify(signalsResponse.body);
    expect(signalsText).not.toContain("CRM Signals E2E linked restricted signal");
    expect(signalsText).not.toContain("CRM Signals E2E unlinked owned signal");

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
        expect(body).toMatch(
            /Authentication is required|AuthenticationError|PermissionError|not whitelisted/
        );
    }

    await page.goto("/app/sahdev-dashboard");
    await expect(page).toHaveURL(/\/login(?:\?|$)/);
});

test("CRM Signals Settings presets can be applied and customised", async ({
    page
}) => {
    await loginAsAdministrator(page);
    await page.goto("/app/crm-signals-settings");

    const preset = page.locator(
        '.frappe-control[data-fieldname="notification_preset"] select'
    );
    const staleDays = page.locator(
        '.frappe-control[data-fieldname="lead_stale_days"] input'
    );
    const quotationThreshold = page.locator(
        '.frappe-control[data-fieldname="quotation_threshold"] input'
    );

    await expect(preset).toBeVisible();
    await preset.selectOption({ label: "Sales Focused" });

    await expect(staleDays).toHaveValue("2");
    await expect
        .poll(async () =>
            Number((await quotationThreshold.inputValue()).replace(/,/g, ""))
        )
        .toBe(100000);

    await staleDays.fill("4");
    // Frappe's Int control commits its model value on change/blur.
    await staleDays.blur();
    await expect(preset).toHaveValue("Custom");
});

test("Realtime notifications suppress duplicate delivery IDs", async ({
    page
}) => {
    await loginAsAdministrator(page);
    await page.goto("/app/crm-signals-dashboard");

    const alertCount = await page.evaluate(() => {
        const frappe = (window as any).frappe;
        const crmSignals = (window as any).crm_signals;
        if (!crmSignals?.handle_realtime_signal) {
            throw new Error("CRM Signals realtime handler is not available");
        }
        const originalShowAlert = frappe.show_alert;
        const alerts: unknown[] = [];
        frappe.show_alert = (...args: unknown[]) => alerts.push(args);
        const payload = {
            delivery_id: "e2e-stable-delivery-id",
            signal_type: "Website Visit",
            priority: "High",
            message: "Duplicate suppression test"
        };
        try {
            crmSignals.handle_realtime_signal(payload);
            crmSignals.handle_realtime_signal(payload);
        } finally {
            frappe.show_alert = originalShowAlert;
        }
        return alerts.length;
    });

    expect(alertCount).toBe(1);
});
