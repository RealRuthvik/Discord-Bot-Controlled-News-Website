let allArticles = []; 

// Optimization: Debounce function to prevent UI lag during typing
function debounce(func, timeout = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
}

document.addEventListener("DOMContentLoaded", async function() {
    // 1. Fetch data using modern async/await
    try {
        const response = await fetch('data/articles.json');
        if (!response.ok) throw new Error('Network response was not ok');
        allArticles = await response.json();
        renderHomepage(allArticles);
    } catch (error) {
        console.error('Error loading news:', error);
    }

    // 2. Smart Live Filter with 300ms Debounce
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce((e) => {
            const query = e.target.value.trim().toLowerCase();
            smartFilter(query);
        }, 300));
    }

    document.addEventListener('submit', function(e) {
        if (e.target && e.target.id === 'search-form') e.preventDefault();
    });
});

function smartFilter(query) {
    if (!query) {
        renderGrid(allArticles);
        return;
    }

    const scoredArticles = allArticles.map(article => {
        let score = 0;
        const title = article.title.toLowerCase();
        const excerpt = article.excerpt.toLowerCase();
        const category = article.category.toLowerCase();
        const author = article.author.toLowerCase();
        const date = article.date.toLowerCase();

        if (title.includes(query)) score += 30;
        if (excerpt.includes(query)) score += 20;
        if (category.includes(query)) score += 15;
        if (author.includes(query)) score += 10;
        if (date.includes(query)) score += 10;

        return { ...article, relevanceScore: score };
    });

    const filtered = scoredArticles
        .filter(article => article.relevanceScore > 0)
        .sort((a, b) => b.relevanceScore - a.relevanceScore);

    // If no results found, show all articles
    renderGrid(filtered.length === 0 ? allArticles : filtered);
}

// PRESERVING YOUR EXACT CSS AND HTML STRUCTURE
function renderGrid(articles) {
    const feedContainer = document.getElementById('feed-container');
    if (!feedContainer) return;

    feedContainer.innerHTML = articles.map(article => `
        <article class="card">
            <div class="card-image-placeholder" style="aspect-ratio: 16/9; overflow: hidden; border-bottom: 3px solid black;">
                <img src="media/image/${article.image}" 
                     alt="${article.title}" 
                     style="width: 100%; height: 100%; object-fit: cover; display: block;">
            </div>
            
            <div style="padding: 15px;">
                <span class="meta-tag" style="font-size: 0.8rem; background-color: #ffc400; padding: 2px 8px; border: 2px solid black; font-weight: bold;">${article.date}</span>
                <span class="meta-tag" style="font-size: 0.8rem; background-color: #64b5f6; padding: 2px 8px; border: 2px solid black; font-weight: bold;">Author: ${article.author}</span>   
                <span class="meta-tag" style="font-size: 0.8rem; background-color: #ff6b6b; padding: 2px 8px; border: 2px solid black; font-weight: bold;">${article.category}</span>
                        
                <h3 style="margin-top: 10px; margin-bottom: 10px; font-size: 1.2rem;">${article.title}</h3>
                <p style="font-size: 0.9rem; color: #555; margin-bottom: 15px;">${article.excerpt}</p>
                <a href="${article.link}">
                    <button class="read-more-btn">READ MORE</button>
                </a>
            </div>
        </article>
    `).join('');
}

// PRESERVING YOUR EXACT CSS AND HTML STRUCTURE
function renderHomepage(articles) {
    const heroContainer = document.getElementById('hero-container');
    if (!heroContainer) return;
    
    const featured = articles.find(article => article.isFeatured === true);
    
    if (featured) {
        heroContainer.style.display = 'block'; 
        heroContainer.innerHTML = `
            <div class="hero-headline" onclick="window.location.href='${featured.link}'" style="cursor: pointer;">
                <h1 style="margin-top: 15px; font-size: 2rem; text-transform: uppercase;">${featured.title}</h1>
            </div>
        `;
    }
    renderGrid(articles);
}