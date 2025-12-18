document.addEventListener("DOMContentLoaded", function () {
    // 1. Fetch the data
    fetch('/data/articles.json')
        .then(response => response.json())
        .then(articles => {
            loadArticleData(articles);
        })
        .catch(error => console.error('Error loading article data:', error));
});

function loadArticleData(articles) {
    // 2. Figure out which page we are on
    const currentPath = window.location.pathname;

    // 3. Find the article in JSON that matches this URL
    const currentArticle = articles.find(article => currentPath.includes(article.link));

    if (currentArticle) {
        // 4. Update the HTML elements
        document.getElementById('meta-date').innerText = `DATE: ${currentArticle.date}`;
        document.getElementById('meta-author').innerText = `AUTHOR: ${currentArticle.author || 'Staff'}`;
        
        const moodElement = document.getElementById('meta-mood');
        if (moodElement) moodElement.innerText = `Catagory: ${currentArticle.mood || currentArticle.category}`;
    }
}

// --- ARTICLE SEARCH (BUTTON TRIGGER ONLY) ---

document.addEventListener('submit', function (e) {
    if (e.target && e.target.id === 'search-form') {
        e.preventDefault();

        const searchInput = document.getElementById('search-input');
        if (!searchInput) return;

        const query = searchInput.value.trim().toLowerCase();
        if (query.length < 2) return;

        const articleBody = document.querySelector('.article-body');
        if (!articleBody) return;

        const searchableElements = articleBody.querySelectorAll('h2, p, blockquote, .meme-entry');

        let found = false;
        for (const element of searchableElements) {
            // Exact word regex to avoid partial matches like "stuff" for "tuff"
            const regex = new RegExp(`\\b${query}\\b`, 'i');

            if (regex.test(element.textContent)) {
                element.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });

                element.style.transition = "background-color 0.4s ease";
                element.style.backgroundColor = "var(--accent-blue)";

                setTimeout(() => {
                    element.style.backgroundColor = "";
                }, 1500);

                found = true;
                break; 
            }
        }

        // --- NEW LOGIC: UPDATE PLACEHOLDER IF NOT FOUND ---
        if (!found) {
            // 1. Save the original placeholder so we can restore it later
            const originalPlaceholder = searchInput.placeholder;

            // 2. Clear current text and show the error message in placeholder
            searchInput.value = ""; 
            searchInput.placeholder = "No matches found.";
            
            // 3. Visual feedback (red outline)
            searchInput.style.outline = "3px solid var(--accent-red)";

            // 4. Revert back to normal after 2 seconds
            setTimeout(() => {
                searchInput.placeholder = originalPlaceholder;
                searchInput.style.outline = "";
            }, 2000);
        }
    }
});