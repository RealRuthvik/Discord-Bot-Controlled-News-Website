document.addEventListener("DOMContentLoaded", async function() {
    // 1. Determine which header to load based on the current page
    const isHomePage = window.location.pathname === '/' || window.location.pathname.endsWith('index.html');
    const headerPath = isHomePage ? '/components/header.html' : '/components/header-articles.html';

    // 2. Load components concurrently for better performance
    await Promise.all([
        loadComponent('header-placeholder', headerPath),
        loadComponent('footer-placeholder', '/components/footer.html')
    ]);

    // 3. Mobile Menu Logic (unchanged to preserve functionality)
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

/**
 * Optimized async component loader
 */
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