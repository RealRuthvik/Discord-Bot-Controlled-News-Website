document.addEventListener("DOMContentLoaded", async function() {
    const path = window.location.pathname;
    const isHomePage = path === '/' || path.endsWith('index.html');
    const isQuizzesHome = path.endsWith('quizzes.html');

    let headerPath = '/components/header-articles.html';
    if (isHomePage) {
        headerPath = '/components/header.html';
    } else if (isQuizzesHome) {
        headerPath = '/components/header-quizzes.html';
    }

    await Promise.all([
        loadComponent('header-placeholder', headerPath),
        loadComponent('footer-placeholder', '/components/footer.html')
    ]);

    document.addEventListener('click', function(e) {
        const btn = e.target.closest('#mobile-menu-btn');
        if (btn) {
            const nav = document.getElementById('main-nav');
            if (nav) {
                nav.classList.toggle('active');
            }
        }
    });
});

async function loadComponent(elementId, filePath) {
    try {
        const response = await fetch(filePath);
        if (!response.ok) throw new Error("Component not found: " + filePath);
        const data = await response.text();
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = data;
        }
    } catch (error) {
        console.error('Error loading component:', error);
    }
}