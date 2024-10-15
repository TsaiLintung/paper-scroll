import { Papers } from './papers.js';  // Import Papers object

// Initialize the page and load progress
function init() {

    Papers.initialize();

    document.getElementById('jump-input').addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            const paperIndex = parseInt(document.getElementById('jump-input').value, 10);
            Papers.jumpToPaper(paperIndex);
        }
    });
}

init();  // Start the page
