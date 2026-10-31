import { defineConfig } from "@playwright/test";

export default defineConfig({
    testDir: "./e2e",
    testMatch: "**/*.spec.ts",
    fullyParallel: false,
    forbidOnly: Boolean(process.env.CI),
    retries: process.env.CI ? 1 : 0,
    workers: 1,
    reporter: process.env.CI
        ? [
              ["github"],
              ["html", { outputFolder: "playwright-report", open: "never" }]
          ]
        : "list",
    timeout: 60_000,
    expect: {
        timeout: 10_000
    },
    use: {
        baseURL: process.env.BASE_URL || "http://test.local:8000",
        trace: "on-first-retry",
        video: "retain-on-failure",
        screenshot: "only-on-failure",
        actionTimeout: 15_000,
        navigationTimeout: 30_000
    }
});
