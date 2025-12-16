document.addEventListener("DOMContentLoaded", function() {
    loadComponent('header-placeholder', '/components/header.html');
    loadComponent('footer-placeholder', '/components/footer.html');

    // --- Mobile Menu Logic Only ---
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

function loadComponent(elementId, filePath) {
    fetch(filePath)
        .then(response => {
            if (!response.ok) throw new Error("Component not found");
            return response.text();
        })
        .then(data => {
            document.getElementById(elementId).innerHTML = data;
        })
        .catch(error => console.error('Error loading component:', error));
}

