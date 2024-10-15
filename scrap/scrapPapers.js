const fs = require('fs');
const { scrapeDownloadLinkAndMetadata } = require('./scrapeUtils'); // Import from scrapeUtils.js

// Load the API key from key.json
const apiKey = JSON.parse(fs.readFileSync('key.json')).key;

// Load links from the links.json file
const links = require('./links.json');

// Load previously scraped papers
let scrapedPapers = [];
try {
    scrapedPapers = JSON.parse(fs.readFileSync('data/papers.json'));
} catch (error) {
    console.log('No existing papers.json file found, starting fresh.');
}

// Extract the URLs of already scraped papers into a Set
const scrapedURLs = new Set(scrapedPapers.map(paper => paper.link));

// Set a batch size for scraping
const MAX_WORKERS = 20; // Maximum number of concurrent workers
const SAVE_INTERVAL = 50; // Save after every 50 papers

// Atomic index handler to ensure that only one worker can increment the index at a time
let index = 0;

// Function to get the next index for processing
function getNextIndex() {
    return index++;
}

// Function to scrape papers in parallel with a worker limit
async function scrapeBatchOfPapersInParallel(maxWorkers) {
    let paperData = [...scrapedPapers]; // Load already scraped papers
    let writtenCount = 0;
    let totalSaved = 0;
    const totalLinks = links.length;

    // Worker function to scrape individual papers
    async function worker() {
        while (true) {
            const currentIndex = getNextIndex();

            if (currentIndex >= totalLinks) return; // No more papers to process

            const { link, journal } = links[currentIndex];

            // Skip already scraped papers based on URL
            if (scrapedURLs.has(link)) {
                // console.log(`Skipping already scraped paper: ${link}`);
                continue;
            }

            // Scrape the download link and metadata
            try {
                const paperDetails = await scrapeDownloadLinkAndMetadata(link, journal, apiKey);

                // Skip papers marked to be skipped
                if (paperDetails.skip) continue;

                // Push result to paperData
                paperData.push({
                    index: currentIndex + 1,
                    link,
                    ...paperDetails
                });

                // Add the paper's link to the scrapedURLs set
                scrapedURLs.add(link); 
                writtenCount++;
                totalSaved++;
                console.log(`Scraped paper ${currentIndex + 1} from journal: ${journal}`);

                // Write to file after every 50 papers scraped
                if (totalSaved % SAVE_INTERVAL === 0) {
                    fs.writeFileSync('data/papers.json', JSON.stringify(paperData, null, 2));
                    console.log(`Saved ${totalSaved} papers to papers.json`);
                }
            } catch (error) {
                console.error(`Error scraping paper at ${link}:`, error);
            }
        }
    }

    // Create worker promises
    const workers = Array.from({ length: maxWorkers }, () => worker());

    // Wait for all workers to finish
    await Promise.all(workers);

    // Save remaining papers if less than SAVE_INTERVAL in the final batch
    if (totalSaved % SAVE_INTERVAL !== 0) {
        fs.writeFileSync('data/papers.json', JSON.stringify(paperData, null, 2));
        console.log(`Final save: ${totalSaved} papers saved to papers.json`);
    }
}

// Function to control how many links to process
async function scrapePapers() {
    await scrapeBatchOfPapersInParallel(MAX_WORKERS);
}

// Start the scraping process
scrapePapers();
