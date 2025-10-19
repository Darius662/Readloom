/**
 * Collection.js
 * Handles functionality for the collection view page
 */

$(document).ready(function() {
    // Load collection data
    loadCollectionData();
    
    // Set up event handlers
    setupEventHandlers();
});

/**
 * Load collection data from the API
 */
function loadCollectionData() {
    // Get collection ID from URL if present
    const urlParams = new URLSearchParams(window.location.search);
    const collectionId = urlParams.get('id');
    
    let url = '/api/collection';
    if (collectionId) {
        url += '/' + collectionId;
    }
    
    // Show loading indicator
    $('#collection-loading').removeClass('d-none');
    $('#collection-content').addClass('d-none');
    $('#collection-error').addClass('d-none');
    
    // Fetch collection data
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load collection data');
            }
            return response.json();
        })
        .then(data => {
            // Hide loading indicator
            $('#collection-loading').addClass('d-none');
            $('#collection-content').removeClass('d-none');
            
            // Render collection data
            renderCollection(data);
        })
        .catch(error => {
            console.error('Error loading collection data:', error);
            $('#collection-loading').addClass('d-none');
            $('#collection-error').removeClass('d-none');
            $('#collection-error-message').text(error.message);
        });
}

/**
 * Render collection data
 * @param {Object} data - Collection data from API
 */
function renderCollection(data) {
    // Set collection title
    if (data.collection) {
        $('#collection-title').text(data.collection.name || 'Collection');
        $('#collection-description').text(data.collection.description || '');
    }
    
    // Render series in collection
    if (data.series && data.series.length > 0) {
        renderSeries(data.series);
    } else {
        $('#series-container').html(`
            <div class="text-center py-5">
                <i class="fas fa-book fa-3x text-muted mb-3"></i>
                <h5>No series in this collection</h5>
                <p class="text-muted">Add series to this collection to see them here</p>
                <a href="/search" class="btn btn-primary">
                    <i class="fas fa-search me-1"></i> Search for Series
                </a>
            </div>
        `);
    }
}

/**
 * Render series in the collection
 * @param {Array} series - Array of series objects
 */
function renderSeries(series) {
    const container = $('#series-container');
    container.empty();
    
    const row = $('<div class="row"></div>');
    
    series.forEach(item => {
        const col = $('<div class="col-md-3 col-sm-6 mb-4"></div>');
        const card = $(`
            <div class="card h-100">
                <img src="${item.cover_url || '/static/img/no-cover.png'}" class="card-img-top" alt="${item.title}" style="height: 200px; object-fit: cover;">
                <div class="card-body">
                    <h5 class="card-title">${item.title}</h5>
                    <p class="card-text small text-muted">${item.author || 'Unknown author'}</p>
                </div>
                <div class="card-footer bg-transparent">
                    <a href="/series/${item.id}" class="btn btn-sm btn-outline-primary w-100">View Details</a>
                </div>
            </div>
        `);
        
        col.append(card);
        row.append(col);
    });
    
    container.append(row);
}

/**
 * Set up event handlers
 */
function setupEventHandlers() {
    // Add series to collection button
    $('#add-series-btn').click(function() {
        // Implementation depends on your UI flow
        // Could open a modal or redirect to search page
        window.location.href = '/search';
    });
    
    // Remove series from collection button
    $(document).on('click', '.remove-series-btn', function() {
        const seriesId = $(this).data('series-id');
        const collectionId = $(this).data('collection-id');
        
        if (confirm('Are you sure you want to remove this series from the collection?')) {
            removeSeriesFromCollection(seriesId, collectionId);
        }
    });
}

/**
 * Remove a series from a collection
 * @param {number} seriesId - Series ID
 * @param {number} collectionId - Collection ID
 */
function removeSeriesFromCollection(seriesId, collectionId) {
    fetch(`/api/collection/${collectionId}/series/${seriesId}`, {
        method: 'DELETE'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to remove series from collection');
            }
            return response.json();
        })
        .then(data => {
            // Reload collection data
            loadCollectionData();
        })
        .catch(error => {
            console.error('Error removing series from collection:', error);
            alert('Failed to remove series from collection: ' + error.message);
        });
}

/**
 * Process image URL to handle missing covers
 * @param {string} url - Image URL
 * @returns {string} - Processed URL or default image
 */
function processImageUrl(url) {
    if (!url) {
        return '/static/img/no-cover.png';
    }
    return url;
}
