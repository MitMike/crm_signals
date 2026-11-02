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
                (root) =>
                    url.pathname === root ||
                    url.pathname.startsWith(`${root}/`)
            ),
        { waitUntil: "domcontentloaded", timeout: 30_000 }
    );
}

function timelinePage(pageNumber: number) {
    const signalItem = {
        source_id: "crm_signal",
        source_doctype: "CRM Signal",
        source_event_id: "SIG-EXPLORER-E2E-1",
        event_type: "Website Visit",
        timestamp: "2026-11-02 10:00:00",
        summary: "Website Visit · High"
    };
    const opportunityItem = {
        source_id: "opportunity",
        source_doctype: "Opportunity",
        source_event_id: "OPP-EXPLORER-E2E-1",
        event_type: "Opportunity",
        timestamp: "2026-11-02 08:00:00",
        summary: "Opportunity · Open"
    };

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
        items: pageNumber === 1 ? [signalItem] : [opportunityItem],
        next_cursor: pageNumber === 1 ? "cursor-page-2" : null
    };
}

test("Explorer opens paged activity sources", async ({ page }) => {
    await loginAsAdministrator(page);
    let requestCount = 0;

    await page.route(
        "**/api/method/crm_signals.explorer.get_explorer_timeline*",
        async (route) => {
            requestCount += 1;
            expect(route.request().method()).toBe("GET");
            const requestUrl = new URL(route.request().url());
            if (requestCount === 2) {
                expect(requestUrl.searchParams.get("cursor")).toBe(
                    "cursor-page-2"
                );
            }

            const responseBody = {
                message: timelinePage(requestCount)
            };
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify(responseBody)
            });
        }
    );

    await page.goto("/app/crm-signals-explorer/Lead/LEAD-EXPLORER-E2E");

    const heading = page.getByRole("heading", {
        name: "Customer Activity Timeline"
    });
    await expect(heading).toBeVisible();
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

    const sourceUrl = new RegExp("/app/crm-signal/SIG-EXPLORER-E2E-1$");
    await expect(page).toHaveURL(sourceUrl);
});
