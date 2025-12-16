document.addEventListener("DOMContentLoaded", function() {
    fetch('/data/articles.json')
        .then(response => response.json())
        .then(data => {
            renderHomepage(data);
        })
        .catch(error => console.error('Error loading news:', error));
});

function renderHomepage(articles) {
    const heroContainer = document.getElementById('hero-container');
    const feedContainer = document.getElementById('feed-container');

    // 1. Find the FIRST article marked as Featured
    const featured = articles.find(article => article.isFeatured === true);
    
    // 2. Variable to hold the list of articles for the grid
    let gridArticles;

    // --- LOGIC START ---
    
    if (featured) {
        // SCENARIO: We found a featured article
        
        // A. Show the hero container
        heroContainer.style.display = 'block'; 

        // B. Inject the HTML for the Green Box
        heroContainer.innerHTML = `
            <div class="hero-headline" onclick="window.location.href='${featured.link}'">
                ${featured.title}
            </div>
        `;

        // C. Filter the grid so the featured one doesn't appear twice
        gridArticles = articles.filter(article => article.id !== featured.id);

    } else {
        // SCENARIO: No featured article found
        
        // A. Hide the hero container completely (poof! gone)
        heroContainer.style.display = 'none';

        // B. The grid should show ALL articles
        gridArticles = articles;
    }

    // --- LOGIC END ---

    // 3. Render the Feed Grid (using the list we decided on above)
    feedContainer.innerHTML = gridArticles.map(article => `
        <article class="card">
            <div class="card-image-placeholder">
               [${article.category}]
            </div>
            <h3>${article.title}</h3>
            <p>${article.excerpt}</p>
            <a href="${article.link}">
                <button class="read-more-btn">READ MORE</button>
            </a>
        </article>
    `).join('');
}