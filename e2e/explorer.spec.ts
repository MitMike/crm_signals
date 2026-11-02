import { expect, test, type Page } from "@playwright/test";

async function loginAsAdministrator(page: Page) {
    await page.goto("/login");

    const loginResponsePromise = page.waitForResponse(
        (response) =>
            response.url().includes("/api/method/login") &&
            response.request().method() === "POST",
        { timeout: 30_000 }
    );

    await page.locator("#login_email").fill(
        process.env.FRAPPE_USER || "Administrator"
    );
    await page.locator("#login_password").fill(
        process.env.FRAPPE_PASSWORD || "admin"
    );
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

    await page.waitForURL(
        (url) =>
            ["/app", "/desk"].some(
                (root) => url.pathname === root || url.pathname.startsWith(`${root}/`)
            ),
        { waitUntil: "domcontentloaded", timeout: 30_000 }
    );
}

function timelinePayload(nextCursor: string | null, includeOpportunity: boolean) {
    return {
        context: {
            doctype: "Lead",
            name: "LEAD-EXPLORER-E2E",
            party_doctype: "Lead",
            party_name: "LEAD-EXPLORER-E2E",
        },
        sources: [
            { source_id: "crm_signal", source_doctype: "CRM Signal", status: "available" },
            { source_id: "quotation", source_doctype: "Quotation", status: "available" },
            {
                source_id: "opportunity",
                source_doctype: "Opportunity",
                status: includeOpportunity ? "available" : "empty",
            },
        ],
        items: includeOpportunity
            ? [
                  {
                      source_id: "opportunity",
                      source_doctype: "Opportunity",
                      source_event_id: "OPP-EXPLORER-E2E-1",
                      event_type: "Opportunity",
                      timestamp: "2026-11-02 08:00:00",
                      summary: "Opportunity · Open",
                  },
              ]
            : [
                  {
                      source_id: "crm_signal",
                      source_doctype: "CRM Signal",
                      source_event_id: "SIG-EXPLORER-E2E-1",
                      event_type: "Website Visit",
                      timestamp: "2026-11-02 10:00:00",
                      summary: "Website Visit · High",
                  },
                  {
                      source_id: "quotation",
                      source_doctype: "Quotation",
                      source_event_id: "QTN-EXPLORER-E2E-1",
                      event_type: "Quotation",
                      timestamp: "2026-11-02 09:00:00",
                      summary: "Quotation · Open",
                  },
              ],
        next_cursor: nextCursor,
    };
}

test("Explorer renders safe activity pages and opens the source record", async ({ page }) => {
    await loginAsAdministrator(page);
    let requestCount = 0;

    await page.route(
        "**/api/method/crm_signals.explorer.get_explorer_timeline*",
        async (route) => {
            requestCount += 1;
            if (requestCount === 2) {
                expect(
                    new URL(route.request().url()).searchParams.get("cursor")
                ).toBe("cursor-page-2");
            }

            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    message: timelinePayload(
                        requestCount === 1 ? "cursor-page-2" : null,
                        requestCount > 1
                    ),
                }),
            });
        }
    );

    await page.goto("/app/crm-signals-explorer/Lead/LEAD-EXPLORER-E2E");

    await expect(
        page.getByRole("heading", { name: "Customer Activity Timeline" })
    ).toBeVisible();
    await expect(page.getByText("Lead · LEAD-EXPLORER-E2E")).toBeVisible();
    await expect(page.getByText("Website Visit · High")).toBeVisible();
    await expect(page.getByText("Quotation · Open")).toBeVisible();
    await expect(page.getByText("No matching activity", { exact: true })).toBeVisible();

    await page.getByRole("button", { name: "Load more activity" }).click();
    await expect(page.getByText("Opportunity · Open")).toBeVisible();
    expect(requestCount).toBe(2);

    await page
        .getByRole("button", {
            name: /Open source record: CRM Signal SIG-EXPLORER-E2E-1/,
        })
        .click();
    await expect(page).toHaveURL(/\/app\/crm-signal\/SIG-EXPLORER-E2E-1$/);
});

test("Lead form opens the Explorer timeline", async ({ page }) => {
    await loginAsAdministrator(page);
    const leadLabel = `Explorer E2E ${Date.now()}`;
    let leadName: string | null = null;

    try {
        const lead = await page.evaluate(async (leadName) => {
            return await new Promise<{ name: string }>((resolve, reject) => {
                frappe.call({
                    method: "frappe.client.insert",
                    args: {
                        doc: {
                            doctype: "Lead",
                            lead_name: leadName,
                            first_name: "Explorer",
                            last_name: "E2E",
                        },
                    },
                    callback: (response) => resolve(response.message),
                    error: (error) => reject(new Error(error?.message || "Lead insert failed")),
                });
            });
        }, leadLabel);
        leadName = lead.name;

        await page.route(
            "**/api/method/crm_signals.explorer.get_explorer_timeline*",
            async (route) => {
                await route.fulfill({
                    status: 200,
                    contentType: "application/json",
                    body: JSON.stringify({
                        message: {
                            context: {
                                doctype: "Lead",
                                name: lead.name,
                                party_doctype: "Lead",
                                party_name: lead.name,
                            },
                            sources: [
                                {
                                    source_id: "crm_signal",
                                    source_doctype: "CRM Signal",
                                    status: "empty",
                                },
                                {
                                    source_id: "quotation",
                                    source_doctype: "Quotation",
                                    status: "empty",
                                },
                                {
                                    source_id: "opportunity",
                                    source_doctype: "Opportunity",
                                    status: "empty",
                                },
                            ],
                            items: [],
                            next_cursor: null,
                        },
                    }),
                });
            }
        );

        await page.goto(`/app/lead/${lead.name}`);
        await page.getByRole("button", { name: "Activity Timeline" }).click();

        await expect(
            page.getByRole("heading", { name: "Customer Activity Timeline" })
        ).toBeVisible();
        await expect(page.getByText(`Lead · ${lead.name}`)).toBeVisible();
    } finally {
        if (leadName) {
            await page.evaluate(async (name) => {
                await new Promise<void>((resolve) => {
                    frappe.call({
                        method: "frappe.client.delete",
                        args: { doctype: "Lead", name },
                        callback: () => resolve(),
                        error: () => resolve(),
                    });
                });
            }, leadName).catch(() => undefined);
        }
    }
});
