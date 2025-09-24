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

// Add item to collection
function addItemToCollection() {
    // Implement add functionality
    alert('Add functionality not implemented yet');
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
    
    // Import/Export buttons
    document.getElementById('import-collection').addEventListener('click', function() {
        alert('Import functionality not implemented yet');
    });
    
    document.getElementById('export-collection').addEventListener('click', function() {
        alert('Export functionality not implemented yet');
    });
});
