export const Papers = {
    papers: [],  // Holds the list of papers in the current chunk
    currentIndex: 1,  // Tracks the current observed paper index
    chunkSize: 1000,  // Size of each chunk of papers
    loadedChunks: {}, // Keep track of loaded chunks
    latestRenderedIndex: 1,

    async initialize() {
        await this.setIndex(this.loadProgressFromLocalStorage()); // Load saved index after papers are loaded
        console.log(this.currentIndex)
        await this.jumpToPaper(this.currentIndex);    
        await this.handleInfiniteScroll();
    },

    // Method to load a specific chunk of papers
    loadPapersChunk(chunkIndex) {
        // Only load the chunk if it hasn't been loaded yet
        if (this.loadedChunks[chunkIndex]) {
            return Promise.resolve();  // Skip if already loaded
        }

        const filePath = `./data/processedPaper_part${chunkIndex}.json`;

        return fetch(filePath)
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error(`Chunk ${chunkIndex} not found`);
                }
            })
            .then(data => {
                this.papers.push(...data);  // Append the papers to the list
                this.loadedChunks[chunkIndex] = true;  // Mark the chunk as loaded
                console.log(`Loaded chunk ${chunkIndex} with ${data.length} papers.`);
            })
            .catch(error => {
                alert(`Error loading chunk ${chunkIndex}:`, error);
            });
    },

    async loadChunksForIndex(paperIndex) {
        const chunkIndex1 = this.getChunkIndex(paperIndex);
        const chunkIndex2 = this.getChunkIndex(paperIndex + 5);
    
        // Load chunkIndex1 first
        await this.loadPapersChunk(chunkIndex1);
    
        // Load chunkIndex2 only if it's different from chunkIndex1
        if (chunkIndex2 !== chunkIndex1) {
            await this.loadPapersChunk(chunkIndex2);
        }
    },

    // Method to determine which chunk the paper index falls into
    getChunkIndex(paperIndex) {
        return Math.floor((paperIndex) / this.chunkSize);
    },

    // Method to set a new index
    setIndex(newIndex) {
        this.currentIndex = newIndex;
        localStorage.setItem('currentPaperIndex', this.currentIndex);
    },

    // Method to load the saved index from localStorage
    loadProgressFromLocalStorage() {
        const savedIndex = localStorage.getItem('currentPaperIndex');
        let index = savedIndex ? parseInt(savedIndex, 10) : 1;  // Default to 1 if no saved index
    
        console.log(`Loaded index: ${index}`);
        return index;
    },

    // Method to jump to a specific paper index
    async jumpToPaper(paperIndex) {
        if (!paperIndex || isNaN(paperIndex) || paperIndex < 1) {
            alert(`Please enter a valid paper index.`);
            return;
        }

        document.getElementById('paper-list').innerHTML = ''; // Clear everything

        await this.setIndex(paperIndex);
        this.latestRenderedIndex = await paperIndex - 2;
        await this.renderPapers();
        await window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    // Method to render papers starting from the latestRenderedIndex + 1
    async renderPapers(pageSize = 5) {
        const startIndex = this.latestRenderedIndex + 1;  // Start from the next paper after the latest rendered
        const paperList = document.getElementById('paper-list');
        const fragment = document.createDocumentFragment();
    
        // Await loading of chunks before running the loop
        await this.loadChunksForIndex(startIndex);
    
        for (let i = startIndex; i < startIndex + pageSize; i++) {
            // Find the paper with the correct index in the papers array
            const paper = this.papers.find(p => p.index === i + 1); // Assuming paper index starts from 1
            if (paper) {
                fragment.appendChild(this.renderPaper(paper));
                this.latestRenderedIndex = i;  // Update latest rendered index
            } else {
                console.log(`Paper with index ${i + 1} not found.`);
            }
        }
    
        paperList.appendChild(fragment);
        this.observeNewPapers(); // Observe newly rendered papers
    },
    

    // Helper method to render a single paper
    renderPaper(paper) {
        const paperDiv = document.createElement('div');
        paperDiv.className = 'paper';
        paperDiv.id = `paper-${paper.index}`;
        
        const abstractWords = paper.abstract.split(' ');
        const maxAb = 50;
        const shortAbstract = abstractWords.slice(0, maxAb).join(' ');
        const remainingAbstract = abstractWords.slice(maxAb).join(' ');

        paperDiv.innerHTML = `
            <div class="index">${paper.index}</div>
            <div class="paper-header">
                <h2>${paper.title}</h2>
            </div>
            <div class="paper-meta">
                <p>${paper.authors}</p>
                <p>${paper.date.match(/\b\d{4}\b/)} ${paper.journal.toUpperCase()} | 
                    <a href="${paper.pdfUrl}" target="_blank" class="pdf-link">PDF</a> |
                    <a href="${paper.downloadLink}" target="_blank" class="website-link">Website</a>
                </p>
            </div>
            <div class="paper-abstract">
                <p id="abstract-short-${paper.index}" class="abstract-short">
                    ${shortAbstract}...${remainingAbstract.length > 0 ? `<a href="#" id="expand-link-${paper.index}" class="expand-link">More</a>` : ''}
                </p>
                <p id="abstract-full-${paper.index}" class="abstract-full" style="display:none;">${paper.abstract}</p>
            </div>
        `;
        
        if (remainingAbstract.length > 0) {
            const expandLink = paperDiv.querySelector(`#expand-link-${paper.index}`);
            const shortAbstractElement = paperDiv.querySelector(`#abstract-short-${paper.index}`);
            const fullAbstractElement = paperDiv.querySelector(`#abstract-full-${paper.index}`);

            expandLink.addEventListener('click', function(e) {
                e.preventDefault();
                shortAbstractElement.style.display = 'none';
                fullAbstractElement.style.display = 'block';
                expandLink.style.display = 'none';
            });
        }

        return paperDiv;
    },


    // Set up the IntersectionObserver to track when a paper touches the top of the viewport
    observePaperScroll(paper) {
        const observerOptions = {
            root: null, // Use the viewport as the root
            rootMargin: '0px 0px -80% 0px', // Trigger earlier on mobile by changing root margin
            threshold: 0.1 // Use a small threshold to trigger when 10% of the paper is visible
        };
    
        const observer = new IntersectionObserver((entries, observerInstance) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const paperIndex = parseInt(entry.target.id.replace('paper-', ''), 10);
                    this.setIndex(paperIndex);
                    observerInstance.unobserve(entry.target);
                }
            });
        }, observerOptions);

        observer.observe(paper);
    },

    // Re-observe newly added papers after rendering
    observeNewPapers() {
        document.querySelectorAll('.paper').forEach(paper => {
            if (!paper.hasAttribute('data-observed')) {
                this.observePaperScroll(paper);
                paper.setAttribute('data-observed', 'true');
            }
        });
    },

    // Method to handle infinite scrolling
    handleInfiniteScroll() {
        window.onscroll = () => {
            if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
                this.renderPapers(); // Continue rendering papers as the user scrolls down
            }
        };
    }
};
