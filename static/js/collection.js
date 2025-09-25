/**
 * Readloom - Collection Management
 */

// Load collection statistics
function loadCollectionStats() {
    fetch('/api/collection/stats')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateCollectionStats(data.stats);
            } else {
                console.error('Failed to load collection stats:', data.error);
            }
        })
        .catch(error => {
            console.error('Error loading collection stats:', error);
        });
}

// Update collection statistics in the UI
function updateCollectionStats(stats) {
    document.getElementById('total-series').textContent = stats.total_series || 0;
    document.getElementById('owned-volumes').textContent = stats.owned_volumes || 0;
    document.getElementById('read-volumes').textContent = stats.read_volumes || 0;
    
    // Format collection value as currency
    const formatter = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    });
    document.getElementById('total-value').textContent = formatter.format(stats.total_value || 0);
}

// Load collection items
function loadCollectionItems() {
    // Show loading state
    document.getElementById('collection-items').innerHTML = '<tr><td colspan="9" class="text-center py-3"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></td></tr>';
    
    // Get filter values
    const typeFilter = document.getElementById('filter-type').value;
    const ownershipFilter = document.getElementById('filter-ownership').value;
    const readFilter = document.getElementById('filter-read').value;
    const formatFilter = document.getElementById('filter-format').value;
    
    // Build query parameters
    const params = new URLSearchParams();
    if (typeFilter) params.append('type', typeFilter);
    if (ownershipFilter) params.append('ownership', ownershipFilter);
    if (readFilter) params.append('read_status', readFilter);
    if (formatFilter) params.append('format', formatFilter);
    
    // Fetch collection items
    fetch(`/api/collection/items?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayCollectionItems(data.items);
            } else {
                console.error('Failed to load collection items:', data.error);
                document.getElementById('collection-items').innerHTML = '<tr><td colspan="9" class="text-center py-3">Error loading collection items</td></tr>';
            }
        })
        .catch(error => {
            console.error('Error loading collection items:', error);
            document.getElementById('collection-items').innerHTML = '<tr><td colspan="9" class="text-center py-3">Error loading collection items</td></tr>';
        });
}

// Display collection items in the table
function displayCollectionItems(items) {
    const tableBody = document.getElementById('collection-items');
    const noItemsMessage = document.getElementById('no-items-message');
    
    if (!items || items.length === 0) {
        tableBody.innerHTML = '';
        noItemsMessage.classList.remove('d-none');
        return;
    }
    
    noItemsMessage.classList.add('d-none');
    tableBody.innerHTML = '';
    
    items.forEach(item => {
        const row = document.createElement('tr');
        
        // Cover image
        const coverCell = document.createElement('td');
        const coverImg = document.createElement('img');
        coverImg.src = item.cover_url || '/static/img/no-cover.jpg';
        coverImg.alt = item.title;
        coverImg.className = 'series-cover';
        coverCell.appendChild(coverImg);
        row.appendChild(coverCell);
        
        // Title
        const titleCell = document.createElement('td');
        const titleLink = document.createElement('a');
        titleLink.href = `/series/${item.series_id}`;
        titleLink.textContent = item.title;
        titleCell.appendChild(titleLink);
        row.appendChild(titleCell);
        
        // Type
        const typeCell = document.createElement('td');
        typeCell.textContent = item.type || 'N/A';
        row.appendChild(typeCell);
        
        // Ownership
        const ownershipCell = document.createElement('td');
        if (item.ownership) {
            const badge = document.createElement('span');
            badge.className = `badge badge-${item.ownership.toLowerCase()}`;
            badge.textContent = item.ownership;
            ownershipCell.appendChild(badge);
        } else {
            ownershipCell.textContent = 'N/A';
        }
        row.appendChild(ownershipCell);
        
        // Read Status
        const readCell = document.createElement('td');
        if (item.read_status) {
            const badge = document.createElement('span');
            badge.className = `badge badge-${item.read_status.toLowerCase()}`;
            badge.textContent = item.read_status;
            readCell.appendChild(badge);
        } else {
            readCell.textContent = 'N/A';
        }
        row.appendChild(readCell);
        
        // Format
        const formatCell = document.createElement('td');
        formatCell.textContent = item.format || 'N/A';
        row.appendChild(formatCell);
        
        // Purchase Date
        const purchaseDateCell = document.createElement('td');
        purchaseDateCell.textContent = item.purchase_date || 'N/A';
        row.appendChild(purchaseDateCell);
        
        // Price
        const priceCell = document.createElement('td');
        if (item.price) {
            const formatter = new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
            });
            priceCell.textContent = formatter.format(item.price);
        } else {
            priceCell.textContent = 'N/A';
        }
        row.appendChild(priceCell);
        
        // Actions
        const actionsCell = document.createElement('td');
        actionsCell.className = 'collection-actions';
        
        // Edit button
        const editBtn = document.createElement('button');
        editBtn.className = 'btn btn-sm btn-primary me-1';
        editBtn.innerHTML = '<i class="fas fa-edit"></i>';
        editBtn.title = 'Edit';
        editBtn.addEventListener('click', () => editCollectionItem(item.id));
        actionsCell.appendChild(editBtn);
        
        // Delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-sm btn-danger';
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
        deleteBtn.title = 'Remove';
        deleteBtn.addEventListener('click', () => removeCollectionItem(item.id));
        actionsCell.appendChild(deleteBtn);
        
        row.appendChild(actionsCell);
        
        tableBody.appendChild(row);
    });
}

// Edit collection item
function editCollectionItem(itemId) {
    console.log('Edit collection item:', itemId);
    // Implement edit functionality
    alert('Edit functionality not implemented yet');
}

// Remove collection item
function removeCollectionItem(itemId) {
    if (confirm('Are you sure you want to remove this item from your collection?')) {
        fetch(`/api/collection/items/${itemId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadCollectionItems();
                loadCollectionStats();
            } else {
                console.error('Failed to remove collection item:', data.error);
                alert('Failed to remove item from collection');
            }
        })
        .catch(error => {
            console.error('Error removing collection item:', error);
            alert('Error removing item from collection');
        });
    }
}

// Load series list for the modal
function loadSeriesList() {
    const seriesSelect = document.getElementById('series-select');
    
    // Clear existing options except the first one
    while (seriesSelect.options.length > 1) {
        seriesSelect.remove(1);
    }
    
    // Show loading state
    const loadingOption = document.createElement('option');
    loadingOption.text = 'Loading series...';
    loadingOption.disabled = true;
    seriesSelect.add(loadingOption);
    
    // Fetch series list
    fetch('/api/series')
        .then(response => response.json())
        .then(data => {
            // Remove loading option
            seriesSelect.remove(seriesSelect.options.length - 1);
            
            if (data.series && data.series.length > 0) {
                // Add series options
                data.series.forEach(series => {
                    const option = document.createElement('option');
                    option.value = series.id;
                    option.text = series.title;
                    seriesSelect.add(option);
                });
            } else {
                const noSeriesOption = document.createElement('option');
                noSeriesOption.text = 'No series available';
                noSeriesOption.disabled = true;
                seriesSelect.add(noSeriesOption);
            }
        })
        .catch(error => {
            console.error('Error loading series list:', error);
            seriesSelect.remove(seriesSelect.options.length - 1);
            
            const errorOption = document.createElement('option');
            errorOption.text = 'Error loading series';
            errorOption.disabled = true;
            seriesSelect.add(errorOption);
        });
}

// Load volumes for selected series
function loadVolumes(seriesId) {
    const volumeSelect = document.getElementById('volume-select');
    const volumeContainer = document.getElementById('volume-select-container');
    
    // Clear existing options except the first one
    while (volumeSelect.options.length > 1) {
        volumeSelect.remove(1);
    }
    
    if (!seriesId) {
        volumeContainer.classList.add('d-none');
        return;
    }
    
    // Show loading state
    volumeContainer.classList.remove('d-none');
    const loadingOption = document.createElement('option');
    loadingOption.text = 'Loading volumes...';
    loadingOption.disabled = true;
    volumeSelect.add(loadingOption);
    
    // Fetch volumes for this series
    fetch(`/api/series/${seriesId}`)
        .then(response => response.json())
        .then(data => {
            // Remove loading option
            volumeSelect.remove(volumeSelect.options.length - 1);
            
            if (data.volumes && data.volumes.length > 0) {
                // Add volume options
                data.volumes.forEach(volume => {
                    const option = document.createElement('option');
                    option.value = volume.id;
                    option.text = `Volume ${volume.volume_number}: ${volume.title || 'Untitled'}`;
                    volumeSelect.add(option);
                });
            } else {
                const noVolumesOption = document.createElement('option');
                noVolumesOption.text = 'No volumes available';
                noVolumesOption.disabled = true;
                volumeSelect.add(noVolumesOption);
            }
        })
        .catch(error => {
            console.error('Error loading volumes:', error);
            volumeSelect.remove(volumeSelect.options.length - 1);
            
            const errorOption = document.createElement('option');
            errorOption.text = 'Error loading volumes';
            errorOption.disabled = true;
            volumeSelect.add(errorOption);
        });
}

// Load chapters for selected series/volume
function loadChapters(seriesId, volumeId) {
    const chapterSelect = document.getElementById('chapter-select');
    const chapterContainer = document.getElementById('chapter-select-container');
    
    // Clear existing options except the first one
    while (chapterSelect.options.length > 1) {
        chapterSelect.remove(1);
    }
    
    if (!seriesId || document.getElementById('item-type').value !== 'CHAPTER') {
        chapterContainer.classList.add('d-none');
        return;
    }
    
    // Show loading state
    chapterContainer.classList.remove('d-none');
    const loadingOption = document.createElement('option');
    loadingOption.text = 'Loading chapters...';
    loadingOption.disabled = true;
    chapterSelect.add(loadingOption);
    
    // Fetch chapters for this series
    fetch(`/api/series/${seriesId}`)
        .then(response => response.json())
        .then(data => {
            // Remove loading option
            chapterSelect.remove(chapterSelect.options.length - 1);
            
            if (data.chapters && data.chapters.length > 0) {
                let chapters = data.chapters;
                
                // Filter by volume if specified
                if (volumeId) {
                    chapters = chapters.filter(chapter => chapter.volume_id === parseInt(volumeId));
                }
                
                if (chapters.length > 0) {
                    // Add chapter options
                    chapters.forEach(chapter => {
                        const option = document.createElement('option');
                        option.value = chapter.id;
                        option.text = `Chapter ${chapter.chapter_number}: ${chapter.title || 'Untitled'}`;
                        chapterSelect.add(option);
                    });
                } else {
                    const noChaptersOption = document.createElement('option');
                    noChaptersOption.text = 'No chapters available';
                    noChaptersOption.disabled = true;
                    chapterSelect.add(noChaptersOption);
                }
            } else {
                const noChaptersOption = document.createElement('option');
                noChaptersOption.text = 'No chapters available';
                noChaptersOption.disabled = true;
                chapterSelect.add(noChaptersOption);
            }
        })
        .catch(error => {
            console.error('Error loading chapters:', error);
            chapterSelect.remove(chapterSelect.options.length - 1);
            
            const errorOption = document.createElement('option');
            errorOption.text = 'Error loading chapters';
            errorOption.disabled = true;
            chapterSelect.add(errorOption);
        });
}

// Reset the form to default values
function resetItemForm() {
    document.getElementById('item-form').reset();
    document.getElementById('item-id').value = '';
    document.getElementById('series-select').selectedIndex = 0;
    document.getElementById('item-type').selectedIndex = 0;
    document.getElementById('volume-select-container').classList.add('d-none');
    document.getElementById('chapter-select-container').classList.add('d-none');
    document.getElementById('ownership-status').value = 'OWNED';
    document.getElementById('read-status').value = 'UNREAD';
    document.getElementById('format').value = 'PHYSICAL';
    document.getElementById('condition').value = 'NEW';
    
    // Set purchase date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('purchase-date').value = today;
}

// Add item to collection
function addItemToCollection() {
    // Reset form and load series list
    resetItemForm();
    loadSeriesList();
    
    // Set modal title
    document.getElementById('itemModalLabel').textContent = 'Add to Library';
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('itemModal'));
    modal.show();
}

// Save item to collection
function saveItemToCollection() {
    // Get form values
    const seriesId = document.getElementById('series-select').value;
    const itemType = document.getElementById('item-type').value;
    const volumeId = document.getElementById('volume-select').value;
    const chapterId = document.getElementById('chapter-select').value;
    const ownershipStatus = document.getElementById('ownership-status').value;
    const readStatus = document.getElementById('read-status').value;
    const format = document.getElementById('format').value;
    const condition = document.getElementById('condition').value;
    const purchaseDate = document.getElementById('purchase-date').value;
    const purchasePrice = document.getElementById('purchase-price').value;
    const purchaseLocation = document.getElementById('purchase-location').value;
    const notes = document.getElementById('notes').value;
    const customTags = document.getElementById('custom-tags').value;
    
    // Validate required fields
    if (!seriesId) {
        alert('Please select a series');
        return;
    }
    
    if (!itemType) {
        alert('Please select an item type');
        return;
    }
    
    if (itemType === 'VOLUME' && !volumeId) {
        alert('Please select a volume');
        return;
    }
    
    if (itemType === 'CHAPTER' && !chapterId) {
        alert('Please select a chapter');
        return;
    }
    
    // Prepare data
    const itemData = {
        series_id: parseInt(seriesId),
        type: itemType,
        ownership_status: ownershipStatus,
        read_status: readStatus,
        format: format,
        condition: condition,
        notes: notes,
        custom_tags: customTags ? customTags.split(',').map(tag => tag.trim()) : []
    };
    
    // Add optional fields
    if (purchaseDate) {
        itemData.purchase_date = purchaseDate;
    }
    
    if (purchasePrice) {
        itemData.price = parseFloat(purchasePrice);
    }
    
    if (purchaseLocation) {
        itemData.purchase_location = purchaseLocation;
    }
    
    // Add volume or chapter ID if applicable
    if (itemType === 'VOLUME' && volumeId) {
        itemData.volume_id = parseInt(volumeId);
    } else if (itemType === 'CHAPTER' && chapterId) {
        itemData.chapter_id = parseInt(chapterId);
    }
    
    // Disable save button and show loading state
    const saveButton = document.getElementById('save-item');
    const originalText = saveButton.textContent;
    saveButton.disabled = true;
    saveButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
    
    // Send request to API
    fetch('/api/collection/items', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(itemData)
    })
    .then(response => response.json())
    .then(data => {
        // Reset button
        saveButton.disabled = false;
        saveButton.textContent = originalText;
        
        if (data.success) {
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('itemModal')).hide();
            
            // Reload collection data
            loadCollectionItems();
            loadCollectionStats();
            
            // Show success message
            alert('Item added to collection successfully');
        } else {
            console.error('Failed to add item to collection:', data.error);
            alert(`Failed to add item to collection: ${data.error || 'Unknown error'}`);
        }
    })
    .catch(error => {
        // Reset button
        saveButton.disabled = false;
        saveButton.textContent = originalText;
        
        console.error('Error adding item to collection:', error);
        alert('Error adding item to collection');
    });
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Load collection data
    loadCollectionStats();
    loadCollectionItems();
    
    // Set up event listeners
    document.getElementById('refresh-stats').addEventListener('click', loadCollectionStats);
    document.getElementById('add-to-collection').addEventListener('click', addItemToCollection);
    document.getElementById('add-first-item')?.addEventListener('click', addItemToCollection);
    
    // Filter change events
    document.getElementById('filter-type').addEventListener('change', loadCollectionItems);
    document.getElementById('filter-ownership').addEventListener('change', loadCollectionItems);
    document.getElementById('filter-read').addEventListener('change', loadCollectionItems);
    document.getElementById('filter-format').addEventListener('change', loadCollectionItems);
    
    // Form field change events
    document.getElementById('series-select').addEventListener('change', function() {
        const seriesId = this.value;
        loadVolumes(seriesId);
        loadChapters(seriesId);
    });
    
    document.getElementById('item-type').addEventListener('change', function() {
        const seriesId = document.getElementById('series-select').value;
        const itemType = this.value;
        
        if (itemType === 'VOLUME') {
            loadVolumes(seriesId);
            document.getElementById('chapter-select-container').classList.add('d-none');
        } else if (itemType === 'CHAPTER') {
            loadVolumes(seriesId);
            loadChapters(seriesId, document.getElementById('volume-select').value);
        } else {
            document.getElementById('volume-select-container').classList.add('d-none');
            document.getElementById('chapter-select-container').classList.add('d-none');
        }
    });
    
    document.getElementById('volume-select').addEventListener('change', function() {
        const seriesId = document.getElementById('series-select').value;
        const volumeId = this.value;
        const itemType = document.getElementById('item-type').value;
        
        if (itemType === 'CHAPTER') {
            loadChapters(seriesId, volumeId);
        }
    });
    
    // Save button click
    document.getElementById('save-item').addEventListener('click', saveItemToCollection);
    
    // Import/Export buttons
    document.getElementById('import-collection').addEventListener('click', function() {
        alert('Import functionality not implemented yet');
    });
    
    document.getElementById('export-collection').addEventListener('click', function() {
        alert('Export functionality not implemented yet');
    });
});
