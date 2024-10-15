const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');

// Load journal-specific parameters from journals.json
const journals = JSON.parse(fs.readFileSync('./scrap/journals.json'));
const minYear = 1999

// Function to log missing titles to scrapPaper.log
function logMissingTitle(url) {
    const logMessage = `Missing or error fetching title for paper: ${url}\n`;
    fs.appendFileSync('scrap/scrapPaper.log', logMessage);
}

// Function to log missing download links
function logMissingDownloadLink(url) {
    const logMessage = `Missing download link for paper: ${url}\n`;
    fs.appendFileSync('scrap/scrapPaper.log', logMessage);
}

// Function to fetch metadata from the download link using a proxy and journal-specific selectors
async function fetchMetadataFromDownloadLink(downloadLink, journal, apiKey, retries = 3) {
    try {
        // Make the request using the proxy
        const response = await axios.get(downloadLink, {
            method: 'GET',
            proxy: {
                host: 'proxy-server.scraperapi.com',
                port: 8001,
                auth: {
                    username: 'scraperapi',
                    password: apiKey
                },
                protocol: 'http'
            }
        });

        const html = response.data;
        const $ = cheerio.load(html);

        // Get the journal-specific selectors from journals.json
        const journalSelectors = journals[journal];

        // Dynamically extract the fields using the selectors
        const title = $(journalSelectors.title).text().trim() || 'Title not found';
        const abstract = $(journalSelectors.abstract).text().trim() || $(journalSelectors.abstract).attr('content') || 'Abstract not found';
        const authors = $(journalSelectors.authors).map((i, el) => $(el).attr('content')).get().join(', ') || $(journalSelectors.authors).text() || 'Authors not found';
        const date = $(journalSelectors.publicationDate).attr('content') || $(journalSelectors.publicationDate).text() || 'Date not found';

        let pdfUrl = $(journalSelectors.pdfUrl).attr('content') || 'PDF URL not found';

        // For "jpe" journal, construct the pdfUrl directly
        if (journal === 'jpe') {
            const doiIdentifier = downloadLink.split('doi/')[1]; // Extract the DOI identifier
            pdfUrl = `https://www.journals.uchicago.edu/doi/epdf/${doiIdentifier}`;
            console.log(`PDF URL for jpe journal updated to: ${pdfUrl}`);
        }

        return { title, pdfUrl, abstract, authors, date, journal };
    } catch (error) {
        if (error.response && error.response.status === 429 && retries > 0) {
            // Handle 429 Too Many Requests (Rate Limit)
            const retryAfter = error.response.headers['retry-after'] || 5; // Retry after 5 seconds if no header is provided
            console.warn(`Rate limit hit. Retrying after ${retryAfter} seconds...`);
            return fetchMetadataFromDownloadLink(downloadLink, journal, apiKey, retries - 1);
        }
        console.error(`Error fetching metadata from ${downloadLink}:`, error.message);
        return {
            title: 'Error fetching title',
            pdfUrl: 'Error fetching PDF URL',
            abstract: 'Error fetching abstract',
            authors: 'Error fetching authors',
            date: 'Error fetching date',
            journal
        };
    }
}

// Function to scrape a single paper's download link and fetch metadata
async function scrapeDownloadLinkAndMetadata(link, journal, apiKey) {
    try {
        const isDoiLink = link.includes("doi");

        if (!isDoiLink) {
            const yearMatch = link.match(/3ay_3a(\d{4})/);
            const year = yearMatch ? parseInt(yearMatch[1], 10) : null;

            if (year && year <= minYear) {
                // console.log(`Skipping paper from ${year}: ${link}`);
                return { skip: true };
            }
        }

        const response = await axios.get(link);
        const html = response.data;
        const $ = cheerio.load(html);

        // Get the journal-specific selectors from journals.json
        const journalSelectors = journals[journal];

        // Dynamically select the download link using the journal's DOWNLOAD_SELECTOR
        const downloadLinkElement = $(journalSelectors.downloadLinkSelector);
        let downloadLink = 'Download link not found';

        if (downloadLinkElement.length > 0) {
            const redirectionUrl = downloadLinkElement.attr('href');
            const urlParams = new URLSearchParams(redirectionUrl.split('?')[1]);
            let fullLink = decodeURIComponent(urlParams.get('u'));

            downloadLink = fullLink.split(';')[0];

            // Special handling for "jpe" and "ecma1"
            if (downloadLink.includes('dx.doi.org') && journal === 'jpe') {
                const doiIdentifier = downloadLink.split('dx.doi.org/')[1];
                downloadLink = `https://www.journals.uchicago.edu/doi/${doiIdentifier}`;
                console.log(`Download link updated to: ${downloadLink}`);
            }

            if (downloadLink.includes('doi.org') && journal === 'ecta1') {
                const doiIdentifier = downloadLink.split('doi.org/')[1];
                downloadLink = `https://www.econometricsociety.org/doi/${doiIdentifier}`;
                console.log(`Download link updated to: ${downloadLink}`);
            }

            const metadata = await fetchMetadataFromDownloadLink(downloadLink, journal, apiKey);

            if (metadata.title === 'Title not found' || metadata.title === 'Error fetching title') {
                logMissingTitle(link);
                return { skip: true };
            }

            return { downloadLink, ...metadata };
        } else {
            logMissingDownloadLink(link);
            return { skip: true };
        }
    } catch (error) {
        console.error(`Error fetching ${link}:`, error.message);
        return { downloadLink: 'Error fetching download link' };
    }
}

module.exports = { scrapeDownloadLinkAndMetadata, fetchMetadataFromDownloadLink };
