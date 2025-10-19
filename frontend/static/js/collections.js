/**
 * Collections.js
 * Handles functionality for the collections list page
 */

$(document).ready(function() {
    // Load collections data
    loadCollectionsData();
    
    // Set up event handlers
    setupEventHandlers();
});

/**
 * Load collections data from the API
 */
function loadCollectionsData() {
    // Show loading indicator
    $('#collections-loading').removeClass('d-none');
    $('#collections-content').addClass('d-none');
    $('#collections-error').addClass('d-none');
    
    // Fetch collections data
    fetch('/api/collections')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load collections data');
            }
            return response.json();
        })
        .then(data => {
            // Hide loading indicator
            $('#collections-loading').addClass('d-none');
            $('#collections-content').removeClass('d-none');
            
            // Render collections data
            renderCollections(data.collections || []);
        })
        .catch(error => {
            console.error('Error loading collections data:', error);
            $('#collections-loading').addClass('d-none');
            $('#collections-error').removeClass('d-none');
            $('#collections-error-message').text(error.message);
        });
}

/**
 * Render collections
 * @param {Array} collections - Array of collection objects
 */
function renderCollections(collections) {
    const container = $('#collections-container');
    container.empty();
    
    if (collections.length === 0) {
        container.html(`
            <div class="text-center py-5">
                <i class="fas fa-layer-group fa-3x text-muted mb-3"></i>
                <h5>No collections found</h5>
                <p class="text-muted">Create a collection to organize your series</p>
                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addCollectionModal">
                    <i class="fas fa-plus me-1"></i> Create Collection
                </button>
            </div>
        `);
        return;
    }
    
    const row = $('<div class="row"></div>');
    
    collections.forEach(collection => {
        const col = $('<div class="col-md-4 col-sm-6 mb-4"></div>');
        const card = $(`
            <div class="card h-100">
                <div class="card-body">
                    <h5 class="card-title">${collection.name}</h5>
                    <p class="card-text">${collection.description || 'No description'}</p>
                    <p class="card-text">
                        <small class="text-muted">
                            ${collection.series_count || 0} series
                        </small>
                    </p>
                </div>
                <div class="card-footer bg-transparent">
                    <a href="/collection/${collection.id}" class="btn btn-sm btn-outline-primary me-2">View</a>
                    <button class="btn btn-sm btn-outline-secondary edit-collection-btn" 
                            data-collection-id="${collection.id}"
                            data-collection-name="${collection.name}"
                            data-collection-description="${collection.description || ''}"
                            data-collection-type="${collection.content_type || ''}">
                        Edit
                    </button>
                    <button class="btn btn-sm btn-outline-danger ms-2 delete-collection-btn" 
                            data-collection-id="${collection.id}"
                            data-collection-name="${collection.name}">
                        Delete
                    </button>
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
    // Add collection form submission
    $('#add-collection-form').submit(function(e) {
        e.preventDefault();
        
        const name = $('#collection-name').val().trim();
        const description = $('#collection-description').val().trim();
        const contentType = $('#collection-type').val();
        
        if (!name) {
            alert('Collection name is required');
            return;
        }
        
        addCollection(name, description, contentType);
    });
    
    // Edit collection button
    $(document).on('click', '.edit-collection-btn', function() {
        const collectionId = $(this).data('collection-id');
        const name = $(this).data('collection-name');
        const description = $(this).data('collection-description');
        const contentType = $(this).data('collection-type');
        
        // Populate edit form
        $('#edit-collection-id').val(collectionId);
        $('#edit-collection-name').val(name);
        $('#edit-collection-description').val(description);
        $('#edit-collection-type').val(contentType);
        
        // Show edit modal
        $('#editCollectionModal').modal('show');
    });
    
    // Edit collection form submission
    $('#edit-collection-form').submit(function(e) {
        e.preventDefault();
        
        const collectionId = $('#edit-collection-id').val();
        const name = $('#edit-collection-name').val().trim();
        const description = $('#edit-collection-description').val().trim();
        const contentType = $('#edit-collection-type').val();
        
        if (!name) {
            alert('Collection name is required');
            return;
        }
        
        updateCollection(collectionId, name, description, contentType);
    });
    
    // Delete collection button
    $(document).on('click', '.delete-collection-btn', function() {
        const collectionId = $(this).data('collection-id');
        const name = $(this).data('collection-name');
        
        // Populate delete confirmation
        $('#delete-collection-name').text(name);
        $('#confirm-delete-btn').data('collection-id', collectionId);
        
        // Show delete modal
        $('#deleteCollectionModal').modal('show');
    });
    
    // Confirm delete button
    $('#confirm-delete-btn').click(function() {
        const collectionId = $(this).data('collection-id');
        deleteCollection(collectionId);
    });
}

/**
 * Add a new collection
 * @param {string} name - Collection name
 * @param {string} description - Collection description
 * @param {string} contentType - Collection content type
 */
function addCollection(name, description, contentType) {
    // Disable submit button and show loading
    const submitBtn = $('#add-collection-submit');
    const originalText = submitBtn.text();
    submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Adding...');
    
    fetch('/api/collections', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            description: description,
            content_type: contentType
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to add collection');
            }
            return response.json();
        })
        .then(data => {
            // Reset form
            $('#add-collection-form')[0].reset();
            
            // Close modal
            $('#addCollectionModal').modal('hide');
            
            // Reload collections
            loadCollectionsData();
        })
        .catch(error => {
            console.error('Error adding collection:', error);
            alert('Failed to add collection: ' + error.message);
        })
        .finally(() => {
            // Reset button
            submitBtn.prop('disabled', false).text(originalText);
        });
}

/**
 * Update an existing collection
 * @param {number} collectionId - Collection ID
 * @param {string} name - Collection name
 * @param {string} description - Collection description
 * @param {string} contentType - Collection content type
 */
function updateCollection(collectionId, name, description, contentType) {
    // Disable submit button and show loading
    const submitBtn = $('#edit-collection-submit');
    const originalText = submitBtn.text();
    submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...');
    
    fetch(`/api/collections/${collectionId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            description: description,
            content_type: contentType
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to update collection');
            }
            return response.json();
        })
        .then(data => {
            // Close modal
            $('#editCollectionModal').modal('hide');
            
            // Reload collections
            loadCollectionsData();
        })
        .catch(error => {
            console.error('Error updating collection:', error);
            alert('Failed to update collection: ' + error.message);
        })
        .finally(() => {
            // Reset button
            submitBtn.prop('disabled', false).text(originalText);
        });
}

/**
 * Delete a collection
 * @param {number} collectionId - Collection ID
 */
function deleteCollection(collectionId) {
    // Disable button and show loading
    const deleteBtn = $('#confirm-delete-btn');
    const originalText = deleteBtn.text();
    deleteBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...');
    
    fetch(`/api/collections/${collectionId}`, {
        method: 'DELETE'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to delete collection');
            }
            return response.json();
        })
        .then(data => {
            // Close modal
            $('#deleteCollectionModal').modal('hide');
            
            // Reload collections
            loadCollectionsData();
        })
        .catch(error => {
            console.error('Error deleting collection:', error);
            alert('Failed to delete collection: ' + error.message);
        })
        .finally(() => {
            // Reset button
            deleteBtn.prop('disabled', false).text(originalText);
        });
}
