/**
 * Authors page functionality
 * 
 * TODO: BROKEN - This page causes the browser to hang indefinitely.
 * The issue appears to be in the fetch request or API endpoint.
 * The page is currently hidden from the navigation menu.
 * 
 * Known issues:
 * - Page hangs when loading authors
 * - No error messages appear in console
 * - Fetch request may not be completing
 * - API endpoint may not be responding
 * 
 * See docs/KNOWN_ISSUES.md for more details and debugging steps.
 */

// Toast notification function (fallback if not defined elsewhere)
function showToast(type, title, message) {
    try {
        // Check if the toast container exists, if not create it
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }

        // Create a unique ID for this toast
        const toastId = 'toast-' + Date.now();
        
        // Determine the background color based on type
        const bgClass = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-info';
        
        // Create the toast element
        const toastElement = document.createElement('div');
        toastElement.id = toastId;
        toastElement.className = `toast ${bgClass} text-white`;
        toastElement.setAttribute('role', 'alert');
        toastElement.setAttribute('aria-live', 'assertive');
        toastElement.setAttribute('aria-atomic', 'true');
        toastElement.innerHTML = `
            <div class="toast-header ${bgClass} text-white">
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        toastContainer.appendChild(toastElement);
        
        // Show the toast if bootstrap is available
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const toast = new bootstrap.Toast(toastElement);
            toast.show();
            
            // Remove the toast element after it's hidden
            toastElement.addEventListener('hidden.bs.toast', function() {
                toastElement.remove();
            });
        } else {
            // Fallback: just log to console if bootstrap is not available
            console.log(`${title}: ${message}`);
            // Auto-remove after 3 seconds
            setTimeout(() => toastElement.remove(), 3000);
        }
    } catch (error) {
        console.error('Error showing toast:', error);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    try {
        console.log('DOMContentLoaded fired');
        
        // Variables
        let currentPage = 1;
        let itemsPerPage = 20;
        let totalAuthors = 0;
        let currentSort = 'name';
        let currentOrder = 'asc';
        
        // Elements - use try/catch to avoid blocking if elements don't exist
        let authorsContainer, loadingAuthors, noAuthors, authorsPagination, refreshAuthorsBtn, authorCardTemplate, sortOptions;
        
        try {
            authorsContainer = document.getElementById('authorsContainer');
            loadingAuthors = document.getElementById('loadingAuthors');
            noAuthors = document.getElementById('noAuthors');
            authorsPagination = document.getElementById('authorsPagination');
            refreshAuthorsBtn = document.getElementById('refreshAuthorsBtn');
            authorCardTemplate = document.getElementById('authorCardTemplate');
            sortOptions = document.querySelectorAll('.sort-option');
            console.log('Elements found successfully');
        } catch (e) {
            console.error('Error finding elements:', e);
            return;
        }
        
        // Initialize
        console.log('Authors page initialized');
        
        // Test if the API is responding
        console.log('Testing API endpoints...');
        fetch('/api/authors/test')
            .then(r => r.json())
            .then(d => console.log('Test endpoint response:', d))
            .catch(e => console.error('Test endpoint failed:', e));
        
        // Call loadAuthors immediately
        console.log('Calling loadAuthors immediately...');
        loadAuthors();
        console.log('loadAuthors call completed');
        
        // Event listeners
        if (refreshAuthorsBtn) {
            refreshAuthorsBtn.addEventListener('click', function() {
                console.log('Refresh clicked');
                loadAuthors();
            });
        }
        
        // Sort options
        if (sortOptions && sortOptions.length > 0) {
            sortOptions.forEach(option => {
                option.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log('Sort clicked:', this.dataset.sort, this.dataset.order);
                    currentSort = this.dataset.sort;
                    currentOrder = this.dataset.order;
                    currentPage = 1; // Reset to first page
                    loadAuthors();
                });
            });
        }
    
    /**
     * Load authors from the API
     */
    function loadAuthors() {
        console.log('loadAuthors called');
        
        try {
            // Show loading
            console.log('Showing loading indicator...');
            loadingAuthors.classList.remove('d-none');
            console.log('Hiding no authors message...');
            noAuthors.classList.add('d-none');
            console.log('Loading indicator shown');
        } catch (e) {
            console.error('Error showing loading:', e);
        }
        
        try {
            // Clear authors container
            console.log('Clearing authors container...');
            let childCount = 0;
            while (authorsContainer.firstChild) {
                if (authorsContainer.firstChild !== loadingAuthors && authorsContainer.firstChild !== noAuthors) {
                    authorsContainer.removeChild(authorsContainer.firstChild);
                    childCount++;
                }
            }
            console.log('Cleared', childCount, 'children');
        } catch (e) {
            console.error('Error clearing container:', e);
        }
        
        try {
            // Calculate offset
            console.log('Calculating offset...');
            const offset = (currentPage - 1) * itemsPerPage;
            const url = `/api/authors/?limit=${itemsPerPage}&offset=${offset}&sort_by=${currentSort}&sort_order=${currentOrder}`;
            console.log('Fetching from:', url);
            
            // Create timeout promise
            const timeoutPromise = new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Fetch timeout after 3 seconds')), 3000)
            );
            
            // Race between fetch and timeout
            console.log('Starting fetch with 3 second timeout...');
            Promise.race([fetch(url), timeoutPromise])
            .then(response => {
                console.log('Got response:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Got data:', data);
                // Hide loading
                loadingAuthors.classList.add('d-none');
                
                if (data.success) {
                    totalAuthors = data.total;
                    
                    if (data.authors && data.authors.length > 0) {
                        // Render authors
                        renderAuthors(data.authors);
                        
                        // Render pagination
                        renderPagination();
                    } else {
                        // Show no authors message
                        noAuthors.classList.remove('d-none');
                    }
                } else {
                    // Show error
                    showToast('error', 'Error', data.message || 'Failed to load authors');
                    noAuthors.classList.remove('d-none');
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                // Hide loading
                loadingAuthors.classList.add('d-none');
                
                // Show no authors message on error
                noAuthors.classList.remove('d-none');
                
                // Log error but don't show toast to avoid annoying the user
                console.error('Error loading authors:', error);
            });
        } catch (e) {
            console.error('Error in loadAuthors:', e);
        }
    }
    
    /**
     * Render authors
     * @param {Array} authors - The authors to render
     */
    function renderAuthors(authors) {
        authors.forEach(author => {
            // Clone template
            const authorCard = authorCardTemplate.content.cloneNode(true);
            
            // Set author data
            authorCard.querySelector('.author-name').textContent = author.name;
            authorCard.querySelector('.book-count').textContent = author.book_count || 0;
            authorCard.querySelector('.provider').textContent = author.provider || 'Unknown';
            
            // Format date
            const addedDate = new Date(author.created_at);
            authorCard.querySelector('.added-date').textContent = `Added on: ${addedDate.toLocaleDateString()}`;
            
            // Set image
            const authorImage = authorCard.querySelector('.author-image');
            if (author.biography && author.biography.includes('http')) {
                // Extract image URL from biography if present
                const imgMatch = author.biography.match(/!\[.*?\]\((.*?)\)/);
                if (imgMatch && imgMatch[1]) {
                    authorImage.src = `/api/proxy/image?url=${encodeURIComponent(imgMatch[1])}`;
                }
            }
            
            // Set links
            const viewAuthorBtn = authorCard.querySelector('.view-author-btn');
            const viewBooksBtn = authorCard.querySelector('.view-books-btn');
            
            viewAuthorBtn.href = `/authors/${author.id}`;
            viewBooksBtn.href = `/authors/${author.id}/books`;
            
            // Append to container
            authorsContainer.appendChild(authorCard);
        });
    }
    
    /**
     * Render pagination
     */
    function renderPagination() {
        // Clear pagination
        authorsPagination.innerHTML = '';
        
        // Calculate total pages
        const totalPages = Math.ceil(totalAuthors / itemsPerPage);
        
        if (totalPages <= 1) {
            return;
        }
        
        // Previous button
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
        
        const prevLink = document.createElement('a');
        prevLink.className = 'page-link';
        prevLink.href = '#';
        prevLink.setAttribute('aria-label', 'Previous');
        prevLink.innerHTML = '<span aria-hidden="true">&laquo;</span>';
        
        prevLink.addEventListener('click', function(e) {
            e.preventDefault();
            if (currentPage > 1) {
                currentPage--;
                loadAuthors();
            }
        });
        
        prevLi.appendChild(prevLink);
        authorsPagination.appendChild(prevLi);
        
        // Page numbers
        const maxPages = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxPages / 2));
        let endPage = Math.min(totalPages, startPage + maxPages - 1);
        
        if (endPage - startPage + 1 < maxPages) {
            startPage = Math.max(1, endPage - maxPages + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const pageLi = document.createElement('li');
            pageLi.className = `page-item ${i === currentPage ? 'active' : ''}`;
            
            const pageLink = document.createElement('a');
            pageLink.className = 'page-link';
            pageLink.href = '#';
            pageLink.textContent = i;
            
            pageLink.addEventListener('click', function(e) {
                e.preventDefault();
                currentPage = i;
                loadAuthors();
            });
            
            pageLi.appendChild(pageLink);
            authorsPagination.appendChild(pageLi);
        }
        
        // Next button
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
        
        const nextLink = document.createElement('a');
        nextLink.className = 'page-link';
        nextLink.href = '#';
        nextLink.setAttribute('aria-label', 'Next');
        nextLink.innerHTML = '<span aria-hidden="true">&raquo;</span>';
        
        nextLink.addEventListener('click', function(e) {
            e.preventDefault();
            if (currentPage < totalPages) {
                currentPage++;
                loadAuthors();
            }
        });
        
        nextLi.appendChild(nextLink);
        authorsPagination.appendChild(nextLi);
        }
        
    } catch (error) {
        console.error('Error initializing authors page:', error);
        // Show error message to user
        const authorsContainer = document.getElementById('authorsContainer');
        if (authorsContainer) {
            authorsContainer.innerHTML = '<div class="col-12 text-center py-5"><p class="text-danger">Error loading authors page. Please refresh the page.</p></div>';
        }
    }
});
