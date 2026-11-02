import { expect, test, type Page } from "@playwright/test";

async function loginAsAdministrator(page: Page) {
    await page.goto("/login");

    const loginResponsePromise = page.waitForResponse(
        (response) =>
            response.url().includes("/api/method/login") &&
            response.request().method() === "POST",
        { timeout: 30_000 }
    );

    await page
        .locator("#login_email")
        .fill(process.env.FRAPPE_USER || "Administrator");
    await page
        .locator("#login_password")
        .fill(process.env.FRAPPE_PASSWORD || "admin");
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
                (root) =>
                    url.pathname === root || url.pathname.startsWith(`${root}/`)
            ),
        { waitUntil: "domcontentloaded", timeout: 30_000 }
    );
}

function timelinePage(pageNumber: number) {
    let item;
    if (pageNumber === 1) {
        item = {
            source_id: "crm_signal",
            source_doctype: "CRM Signal",
            source_event_id: "SIG-EXPLORER-E2E-1",
            event_type: "Website Visit",
            timestamp: "2026-11-02 10:00:00",
            summary: "Website Visit · High"
        };
    } else {
        item = {
            source_id: "opportunity",
            source_doctype: "Opportunity",
            source_event_id: "OPP-EXPLORER-E2E-1",
            event_type: "Opportunity",
            timestamp: "2026-11-02 08:00:00",
            summary: "Opportunity · Open"
        };
    }

    return {
        context: {
            doctype: "Lead",
            name: "LEAD-EXPLORER-E2E",
            party_doctype: "Lead",
            party_name: "LEAD-EXPLORER-E2E"
        },
        sources: [
            {
                source_id: "crm_signal",
                source_doctype: "CRM Signal",
                status: "available"
            },
            {
                source_id: "quotation",
                source_doctype: "Quotation",
                status: "available"
            },
            {
                source_id: "opportunity",
                source_doctype: "Opportunity",
                status: pageNumber === 1 ? "empty" : "available"
            }
        ],
        items: [item],
        next_cursor: pageNumber === 1 ? "cursor-page-2" : null
    };
}

test("Explorer renders safe activity pages and opens the source record", async ({
    page
}) => {
    await loginAsAdministrator(page);
    let requestCount = 0;

    await page.route(
        "**/api/method/crm_signals.explorer.get_explorer_timeline*",
        async (route) => {
            requestCount += 1;
            expect(route.request().method()).toBe("GET");
            const requestUrl = new URL(route.request().url());
            if (requestCount === 1) {
                expect(requestUrl.searchParams.has("cursor")).toBe(false);
            } else {
                expect(requestUrl.searchParams.get("cursor")).toBe(
                    "cursor-page-2"
                );
            }

            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({ message: timelinePage(requestCount) })
            });
        }
    );

    await page.goto("/app/crm-signals-explorer/Lead/LEAD-EXPLORER-E2E");

    await expect(
        page
            .getByRole("navigation", { name: "Breadcrumb" })
            .getByText("Customer Activity Timeline", { exact: true })
    ).toBeVisible();
    await expect(page.getByText("Lead · LEAD-EXPLORER-E2E")).toBeVisible();
    await expect(page.getByText("Website Visit · High")).toBeVisible();
    await expect(
        page.getByText("No matching activity", { exact: true })
    ).toBeVisible();

    await page.getByRole("button", { name: "Load more activity" }).click();
    await expect(page.getByText("Opportunity · Open")).toBeVisible();
    expect(requestCount).toBe(2);

    const sourceButton = page.getByRole("button", {
        name: /Open source record: CRM Signal SIG-EXPLORER-E2E-1/
    });
    await sourceButton.click();

    const sourceUrl = /\/desk\/crm-signals\/crm-signal\/SIG-EXPLORER-E2E-1$/;
    await expect(page).toHaveURL(sourceUrl);
});


test(
    "Explorer routes every supported context through the GET timeline API",
    async ({ page }) => {
        await loginAsAdministrator(page);
        const contexts = [
            { doctype: "Lead", name: "LEAD-EXPLORER-MATRIX" },
            { doctype: "Customer", name: "CUSTOMER-EXPLORER-MATRIX" },
            { doctype: "Opportunity", name: "OPP-EXPLORER-MATRIX" },
            { doctype: "CRM Signal", name: "SIG-EXPLORER-MATRIX" },
            { doctype: "Highlight", name: "SIG-HIGHLIGHT-MATRIX" }
        ];
        const requests: {
            doctype: string | null;
            name: string | null;
            pageLength: string | null;
        }[] = [];

        await page.route(
            "**/api/method/crm_signals.explorer.get_explorer_timeline*",
            async (route) => {
                expect(route.request().method()).toBe("GET");
                const requestUrl = new URL(route.request().url());
                const doctype = requestUrl.searchParams.get("context_doctype");
                const name = requestUrl.searchParams.get("context_name");
                const pageLength = requestUrl.searchParams.get("page_length");
                requests.push({ doctype, name, pageLength });

                await route.fulfill({
                    status: 200,
                    contentType: "application/json",
                    body: JSON.stringify({
                        message: {
                            context: {
                                doctype,
                                name,
                                party_doctype:
                                    doctype === "Customer" ? "Customer" : "Lead",
                                party_name: name
                            },
                            sources: [],
                            items: [],
                            next_cursor: null
                        }
                    })
                });
            }
        );

        for (const context of contexts) {
            await page.goto(
                `/app/crm-signals-explorer/${encodeURIComponent(context.doctype)}/${encodeURIComponent(context.name)}`
            );
            await expect(
                page.getByText(
                    `${context.doctype} · ${context.name}`,
                    { exact: true }
                )
            ).toBeVisible();
        }

        expect(requests).toEqual(
            contexts.map((context) => ({
                doctype: context.doctype,
                name: context.name,
                pageLength: "20"
            }))
        );
    }
);

test(
    "Explorer ignores a late response after the user changes timeline context",
    async ({ page }) => {
        await loginAsAdministrator(page);
        let releaseStaleResponse: (() => Promise<void>) | undefined;
        let signalStaleRequestStarted: (() => void) | undefined;
        const staleRequestStarted = new Promise<void>((resolve) => {
            signalStaleRequestStarted = resolve;
        });

        const responseFor = (
            doctype: string,
            name: string,
            summary: string
        ) => ({
            message: {
                context: {
                    doctype,
                    name,
                    party_doctype: doctype === "Customer" ? "Customer" : "Lead",
                    party_name: name
                },
                sources: [],
                items: [
                    {
                        source_id: "crm_signal",
                        source_doctype: "CRM Signal",
                        source_event_id: `SIG-${name}`,
                        event_type: "CRM Signal",
                        timestamp: "2026-11-02 10:00:00",
                        summary
                    }
                ],
                next_cursor: null
            }
        });

        await page.route(
            "**/api/method/crm_signals.explorer.get_explorer_timeline*",
            async (route) => {
                expect(route.request().method()).toBe("GET");
                const requestUrl = new URL(route.request().url());
                const doctype =
                    requestUrl.searchParams.get("context_doctype") || "";
                const name = requestUrl.searchParams.get("context_name") || "";

                if (name === "LEAD-EXPLORER-STALE") {
                    await new Promise<void>((resolve) => {
                        releaseStaleResponse = async () => {
                            await route.fulfill({
                                status: 200,
                                contentType: "application/json",
                                body: JSON.stringify(
                                    responseFor(
                                        doctype,
                                        name,
                                        "Stale response marker"
                                    )
                                )
                            });
                            resolve();
                        };
                        signalStaleRequestStarted?.();
                    });
                    return;
                }

                await route.fulfill({
                    status: 200,
                    contentType: "application/json",
                    body: JSON.stringify(
                        responseFor(
                            doctype,
                            name,
                            "Current response marker"
                        )
                    )
                });
            }
        );

        await page.goto(
            "/app/crm-signals-explorer/Lead/LEAD-EXPLORER-STALE"
        );
        await staleRequestStarted;
        await page.evaluate(() => {
            (window as any).frappe.set_route(
                "crm-signals-explorer",
                "Customer",
                "CUSTOMER-EXPLORER-CURRENT"
            );
        });

        await expect(
            page.getByText("Customer · CUSTOMER-EXPLORER-CURRENT")
        ).toBeVisible();
        await expect(
            page.getByText("Current response marker")
        ).toBeVisible();
        if (!releaseStaleResponse) {
            throw new Error("The stale timeline request was not captured");
        }
        await releaseStaleResponse();
        await expect(
            page.getByText("Stale response marker")
        ).toHaveCount(0);
        await expect(
            page.getByText("Current response marker")
        ).toBeVisible();
    }
);
