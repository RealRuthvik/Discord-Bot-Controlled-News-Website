document.addEventListener("DOMContentLoaded", function () {

    fetch('/data/articles.json')
        .then(response => response.json())
        .then(articles => {
            loadArticleData(articles);
        })
        .catch(error => console.error('Error loading article data:', error));
});

function loadArticleData(articles) {

    const currentPath = window.location.pathname;

    const currentArticle = articles.find(article => currentPath.includes(article.link));

    if (currentArticle) {

        document.getElementById('meta-date').innerText = `DATE: ${currentArticle.date}`;
        document.getElementById('meta-author').innerText = `AUTHOR: ${currentArticle.author || 'Staff'}`;

        const moodElement = document.getElementById('meta-mood');
        if (moodElement) moodElement.innerText = `Catagory: ${currentArticle.mood || currentArticle.category}`;
    }
}

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

        if (!found) {

            const originalPlaceholder = searchInput.placeholder;

            searchInput.value = ""; 
            searchInput.placeholder = "No matches found.";

            searchInput.style.outline = "3px solid var(--accent-red)";

            setTimeout(() => {
                searchInput.placeholder = originalPlaceholder;
                searchInput.style.outline = "";
            }, 2000);
        }
    }
});