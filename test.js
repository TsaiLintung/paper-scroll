const puppeteer = require('puppeteer');

// Define a dynamic URL for testing
const BASE_URL = process.env.TEST_URL || 'http://localhost:3000'; // Default to localhost if not provided

describe('Paper Scroll Application Tests', () => {
    let browser;
    let page;

    before(async () => {
        browser = await puppeteer.launch({ headless: true });
        page = await browser.newPage();
        await page.goto(BASE_URL); // Use the dynamic URL
    });

    after(async () => {
        await browser.close();
    });

    // Test 1: Jump to Paper Feature
    it('should jump to the correct paper index', async () => {
        // Enter a paper index in the jump input
        await page.type('#jump-input', '50');
        await page.keyboard.press('Enter');

        // Wait for the page to update and jump to the correct paper
        await page.waitForSelector('#paper-49'); // Paper index is 0-based

        // Check if the correct paper is displayed
        const paperIndex = await page.evaluate(() => {
            return document.querySelector('.index').innerText;
        });

        console.log(`Jumped to paper index: ${paperIndex}`);
        expect(paperIndex).toBe('50');
    });

    // Test 2: Infinite Scroll Feature
    it('should load more papers when scrolled to the bottom', async () => {
        // Scroll to the bottom of the page
        await page.evaluate(() => {
            window.scrollTo(0, document.body.scrollHeight);
        });

        // Wait for more papers to load
        await page.waitForSelector('#paper-5'); // Assuming initial 5 papers are rendered

        // Check if papers beyond the initial set are rendered
        const paperExists = await page.evaluate(() => {
            return !!document.querySelector('#paper-10'); // Check if paper 10 is rendered
        });

        console.log('Infinite scroll loading more papers:', paperExists);
        expect(paperExists).toBe(true);
    });

    // Test 3: Progress Saving Feature
    it('should save the current paper index to localStorage', async () => {
        // Jump to a specific paper index
        await page.type('#jump-input', '50');
        await page.keyboard.press('Enter');

        // Wait for the jump to complete
        await page.waitForSelector('#paper-49');

        // Check localStorage for the saved paper index
        const savedIndex = await page.evaluate(() => {
            return localStorage.getItem('currentPaperIndex');
        });

        console.log(`Saved paper index in localStorage: ${savedIndex}`);
        expect(parseInt(savedIndex, 10)).toBe(50);
    });

    // Test 4: Loading saved progress on refresh
    it('should load the saved progress on refresh', async () => {
        // Reload the page
        await page.reload();

        // Wait for the saved paper to be rendered
        await page.waitForSelector('#paper-49');

        // Check if the correct paper is displayed after refresh
        const paperIndex = await page.evaluate(() => {
            return document.querySelector('.index').innerText;
        });

        console.log(`Loaded paper index after refresh: ${paperIndex}`);
        expect(paperIndex).toBe('50');
    });
});
