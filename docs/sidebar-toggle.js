// Custom sidebar toggle behavior for mdbook
// When clicking a section title that you're already viewing, toggle collapse instead of reloading
(() => {
    document.addEventListener('DOMContentLoaded', () => {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;

        sidebar.addEventListener('click', (e) => {
            // Find the clicked anchor element
            const link = e.target.closest('a[href]');
            if (!link) return;

            // Skip if this is a toggle button (those already work correctly)
            if (link.classList.contains('toggle')) return;

            // Check if this link's parent has a sibling toggle button (meaning it's a collapsible section)
            const toggleButton = link.parentElement?.querySelector('a.toggle');
            if (!toggleButton) return;

            // Get the current page URL without hash/query
            const currentPage = document.location.href.toString().split('#')[0].split('?')[0];

            // Get the link's target URL
            const linkHref = new URL(link.href, document.location.href).href.split('#')[0].split('?')[0];

            // If we're already on this page, toggle the section instead of navigating
            if (currentPage === linkHref) {
                e.preventDefault();
                e.stopPropagation();
                // Toggle the expanded class on the parent li
                const parentLi = link.parentElement;
                if (parentLi && parentLi.classList.contains('chapter-item')) {
                    parentLi.classList.toggle('expanded');
                }
            }
        });
    });
})();
