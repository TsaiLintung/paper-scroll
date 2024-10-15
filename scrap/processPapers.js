const fs = require('fs');

// Load the JSON file
const papers = require('../data/papers.json');

// Define journal-specific title cleaning patterns
const journalPatterns = {
    "qje": "\\*",
    "aer": "- American",
    "jpe": "\\| J",      // Escape the pipe character for certain journals
    "ecta1": "\\| Th",
    "res": "\\| Th",
    "generic": "\\*"     // Default fallback pattern
};

// Function to clean the title based on journal patterns
function cleanTitle(paper) {
    const cleanPattern = journalPatterns[paper.journal] || journalPatterns['generic'];
    return paper.title.replace(new RegExp(`${cleanPattern}.*`), '').trim();
}

// Function to clean the abstract by removing "Abstract" at the start
function cleanAbstract(abstract) {
    return abstract.replace(/^abstract/i, '').trim();
}

// Function to process papers (sort, clean title, and abstract)
function processPapers(papers) {
    // Separate papers with abstract "Abstract not found" and others
    let foundAbstractPapers = [];
    let noAbstractPapers = [];

    papers.forEach(paper => {
        // Clean the title
        paper.title = cleanTitle(paper);

        // Clean the abstract if it's not "Abstract not found"
        if (paper.abstract !== "Abstract not found") {
            paper.abstract = cleanAbstract(paper.abstract);
            foundAbstractPapers.push(paper);
        } else {
            noAbstractPapers.push(paper);
        }
    });

    // Sort papers with found abstracts by year (descending)
    foundAbstractPapers.sort((a, b) => {
        const yearA = parseInt(a.date.match(/\b\d{4}\b/)[0], 10);
        const yearB = parseInt(b.date.match(/\b\d{4}\b/)[0], 10);
        return yearB - yearA;
    });

    // Concatenate papers with found abstracts first and "Abstract not found" last
    let sortedPapers = foundAbstractPapers.concat(noAbstractPapers);

    // Re-index the papers by their new order
    sortedPapers = sortedPapers.map((paper, index) => {
        paper.index = index + 1;
        return paper;
    });

    return sortedPapers;
}

// Helper function to split an array into chunks
function chunkArray(array, chunkSize) {
    const chunks = [];
    for (let i = 0; i < array.length; i += chunkSize) {
        chunks.push(array.slice(i, i + chunkSize));
    }
    return chunks;
}

// Process the papers
const processedPapers = processPapers(papers);

// Split the processed papers into chunks of 1000 papers each
const paperChunks = chunkArray(processedPapers, 1000);

// Write each chunk to a separate JSON file
paperChunks.forEach((chunk, index) => {
    const filename = `./data/processedPaper_part${index}.json`;
    fs.writeFile(filename, JSON.stringify(chunk, null, 2), (err) => {
        if (err) {
            return console.error(`Error writing JSON file (${filename}):`, err);
        }
        console.log(`Saved ${filename}`);
    });
});
