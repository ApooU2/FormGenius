// @ts-check
const { defineConfig, devices } = require('@playwright/test');

/**
 * Playwright Configuration for FormGenius
 * This file configures Playwright test execution settings
 */
module.exports = defineConfig({
  // Test directory
  testDir: './generated_tests',

  // Test timeout
  timeout: 30000,

  // Expect timeout for assertions
  expect: {
    timeout: 10000,
  },

  // Global test setup
  globalSetup: './setup/global-setup.js',
  globalTeardown: './setup/global-teardown.js',

  // Test output directory
  outputDir: './test-results',

  // Reporter configuration
  reporter: [
    ['list'],
    ['json', { outputFile: './test-results/results.json' }],
    ['html', { outputFolder: './test-results/html-report', open: 'never' }],
    ['junit', { outputFile: './test-results/results.xml' }]
  ],

  // Retry configuration
  retries: 2,

  // Parallel workers
  workers: 4,

  // Global browser settings
  use: {
    // Browser settings
    browserName: 'chromium',
    headless: true,
    viewport: {
      width: 1920,
      height: 1080
    },
    ignoreHTTPSErrors: true,
    acceptDownloads: true,
    locale: 'en-US',
    timezoneId: 'America/New_York',
    
    // Test artifacts
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
  },

  // Projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  // Web server configuration (for local testing)
  webServer: {
    command: 'npm start',
    port: 3000,
    reuseExistingServer: !process.env.CI,
  },
});
