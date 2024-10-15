const https = require('https');
const cheerio = require('cheerio');
const fs = require('fs');

// Load journal-specific parameters from journals.json
const journals = JSON.parse(fs.readFileSync('journals.json'));

// Function to fetch HTML content of a URL
const fetchHtml = (url, callback) => {
  https.get(url, (res) => {
    let data = '';

    // Collect data chunks
    res.on('data', (chunk) => {
      data += chunk;
    });

    // Once data is fully received
    res.on('end', () => {
      callback(null, data);
    });
  }).on('error', (err) => {
    callback(err, null);
  });
};

// Array to hold the final links
const finalLinks = [];

// Function to process a single journal
const processJournal = (journal, journalName) => {
  return new Promise((resolve, reject) => {
    const mainUrl = journal.baseUrl;

    // Fetch the main URL
    fetchHtml(`${mainUrl}/`, (err, data) => {
      if (err) {
        console.error(`Error fetching the main URL for ${journalName}:`, err);
        return reject(err);
      }

      const $ = cheerio.load(data);

      // Select the parent container that holds all the links
      const container = $('body > table > tbody > tr:nth-child(3) > td:nth-child(3) > table > tbody > tr:nth-child(1) > td:nth-child(2) > div');

      const linksInContainer = container.find('a');
      if (!linksInContainer.length) {
        console.log(`No links found in the main URL for ${journalName}`);
        return resolve();  // Resolve if no links found
      }

      let promises = [];

      // Find all anchor tags in the container and get their href attributes
      linksInContainer.each((index, element) => {
        const href = $(element).attr('href');
        
        if (href && href.startsWith('default')) {
          const fullUrl = `${mainUrl}/${href}`; // Use `mainUrl` to construct the full URL

          // Push a new promise for fetching each individual page
          promises.push(
            new Promise((resolveLink, rejectLink) => {
              fetchHtml(fullUrl, (err, pageData) => {
                if (err) {
                  console.error(`Error fetching the URL ${fullUrl}:`, err);
                  return rejectLink(err);
                }

                const $page = cheerio.load(pageData);

                // Find the links in the page
                const links = $page('body > table > tbody > tr:nth-child(3) > td:nth-child(3) > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > dl > dt > a');
                
                if (links.length) {
                  links.each((i, el) => {
                    const extractedLink = $(el).attr('href');
                    // Add the final URL to the array, with the journal field
                    finalLinks.push({ 
                      index: finalLinks.length + 1, 
                      link: `${mainUrl}/${extractedLink}`, 
                      journal: journalName 
                    });
                  });
                  console.log(`Found ${links.length} links in URL ${fullUrl}:`);
                } else {
                  console.log(`No matching links found for URL: ${fullUrl}`);
                }
                resolveLink();  // Resolve the inner promise when done processing the links
              });
            })
          );
        } else {
          console.log(`Skipping non-default href: ${href}`);
        }
      });

      // Wait for all link-fetching promises to resolve
      Promise.all(promises)
        .then(() => {
          console.log(`Finished processing journal: ${journalName}`);
          resolve();  // Resolve the main promise when all links are processed
        })
        .catch(reject);  // Reject if any of the inner promises fail
    });
  });
};

// Loop through each journal in the journals.json
const journalNames = Object.keys(journals);
const processNextJournal = async (index) => {
  if (index < journalNames.length) {
    const journalName = journalNames[index];
    const journal = journals[journalName];

    console.log(`Processing journal: ${journalName}`);

    // Await the processing of the current journal
    try {
      await processJournal(journal, journalName);  // Make sure this is asynchronous and returns a promise
      // After the current journal is processed, move to the next one
      await processNextJournal(index + 1);
    } catch (error) {
      console.error(`Error processing journal ${journalName}:`, error);
    }
  } else {
    // Once all journals are processed, write the final links to links.json
    console.log('All journals processed. Writing to links.json...');

    fs.writeFile('./scrap/links.json', JSON.stringify(finalLinks, null, 2), (err) => {
      if (err) {
        return console.error('Error writing JSON file:', err);
      }
      console.log('Final links saved to links.json');
    });
  }
};

// Kick off the processing of journals
processNextJournal(0);