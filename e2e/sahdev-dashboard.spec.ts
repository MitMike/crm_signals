import { expect, test } from "@playwright/test";

test(
    "Executive Compass loads permission-filtered billing data",
    async ({ page }) => {
        const pageErrors: string[] = [];
        page.on("pageerror", (error) => pageErrors.push(error.message));

        const loginResponse = await page.request.post("/api/method/login", {
            form: {
                usr: process.env.FRAPPE_USER || "Administrator",
                pwd: process.env.FRAPPE_PASSWORD || "admin"
            }
        });
        expect(loginResponse.ok()).toBeTruthy();

        const dashboardResponsePromise = page.waitForResponse((response) =>
            response.url().includes("/api/method/crm_signals.api.get_sales_compass_data")
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
    }
);
