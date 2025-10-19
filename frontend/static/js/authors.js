/**
 * Authors page functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Variables
    let currentPage = 1;
    let itemsPerPage = 20;
    let totalAuthors = 0;
    let currentSort = 'name';
    let currentOrder = 'asc';
    
    // Elements
    const authorsContainer = document.getElementById('authorsContainer');
    const loadingAuthors = document.getElementById('loadingAuthors');
    const noAuthors = document.getElementById('noAuthors');
    const authorsPagination = document.getElementById('authorsPagination');
    const refreshAuthorsBtn = document.getElementById('refreshAuthorsBtn');
    const authorCardTemplate = document.getElementById('authorCardTemplate');
    const sortOptions = document.querySelectorAll('.sort-option');
    
    // Initialize
    loadAuthors();
    
    // Event listeners
    if (refreshAuthorsBtn) {
        refreshAuthorsBtn.addEventListener('click', function() {
            loadAuthors();
        });
    }
    
    // Sort options
    sortOptions.forEach(option => {
        option.addEventListener('click', function(e) {
            e.preventDefault();
            currentSort = this.dataset.sort;
            currentOrder = this.dataset.order;
            currentPage = 1; // Reset to first page
            loadAuthors();
        });
    });
    
    /**
     * Load authors from the API
     */
    function loadAuthors() {
        // Show loading
        loadingAuthors.classList.remove('d-none');
        noAuthors.classList.add('d-none');
        
        // Clear authors container
        while (authorsContainer.firstChild) {
            if (authorsContainer.firstChild !== loadingAuthors && authorsContainer.firstChild !== noAuthors) {
                authorsContainer.removeChild(authorsContainer.firstChild);
            }
        }
        
        // Calculate offset
        const offset = (currentPage - 1) * itemsPerPage;
        
        // Fetch authors
        fetch(`/api/authors?limit=${itemsPerPage}&offset=${offset}&sort_by=${currentSort}&sort_order=${currentOrder}`)
            .then(response => response.json())
            .then(data => {
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
                }
            })
            .catch(error => {
                // Hide loading
                loadingAuthors.classList.add('d-none');
                
                // Show error
                console.error('Error loading authors:', error);
                showToast('error', 'Error', 'Failed to load authors');
            });
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
});
