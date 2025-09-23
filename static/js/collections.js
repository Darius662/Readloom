/**
 * MangaArr - Collections Management
 */

// Load collections
function loadCollections() {
    fetch('/api/collections')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayCollections(data.collections);
            } else {
                showError('Failed to load collections: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error loading collections:', error);
            showError('Failed to load collections. Please try again.');
        });
}

// Display collections in the table
function displayCollections(collections) {
    const tableBody = document.getElementById('collectionsTableBody');
    
    if (!collections || collections.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No collections found</td></tr>';
        return;
    }
    
    tableBody.innerHTML = '';
    
    collections.forEach(collection => {
        const row = document.createElement('tr');
        
        // Name column
        const nameCell = document.createElement('td');
        nameCell.textContent = collection.name;
        row.appendChild(nameCell);
        
        // Root folders count column
        const rootFoldersCell = document.createElement('td');
        rootFoldersCell.textContent = collection.root_folder_count || 0;
        row.appendChild(rootFoldersCell);
        
        // Series count column
        const seriesCell = document.createElement('td');
        seriesCell.textContent = collection.series_count || 0;
        row.appendChild(seriesCell);
        
        // Default column
        const defaultCell = document.createElement('td');
        if (collection.is_default) {
            const badge = document.createElement('span');
            badge.className = 'badge bg-success';
            badge.textContent = 'Default';
            defaultCell.appendChild(badge);
        }
        row.appendChild(defaultCell);
        
        // Actions column
        const actionsCell = document.createElement('td');
        
        // View button
        const viewBtn = document.createElement('button');
        viewBtn.className = 'btn btn-sm btn-info me-1';
        viewBtn.innerHTML = '<i class="fas fa-eye"></i>';
        viewBtn.title = 'View Details';
        viewBtn.addEventListener('click', () => viewCollectionDetails(collection.id));
        actionsCell.appendChild(viewBtn);
        
        // Edit button
        const editBtn = document.createElement('button');
        editBtn.className = 'btn btn-sm btn-primary me-1';
        editBtn.innerHTML = '<i class="fas fa-edit"></i>';
        editBtn.title = 'Edit Collection';
        editBtn.addEventListener('click', () => openEditCollectionModal(collection));
        actionsCell.appendChild(editBtn);
        
        // Delete button (disabled for default collection)
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-sm btn-danger';
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
        deleteBtn.title = 'Delete Collection';
        deleteBtn.disabled = collection.is_default;
        if (!collection.is_default) {
            deleteBtn.addEventListener('click', () => deleteCollection(collection.id, collection.name));
        }
        actionsCell.appendChild(deleteBtn);
        
        row.appendChild(actionsCell);
        
        tableBody.appendChild(row);
    });
}

// Load root folders
function loadRootFolders() {
    fetch('/api/root-folders')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayRootFolders(data.root_folders);
            } else {
                showError('Failed to load root folders: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error loading root folders:', error);
            showError('Failed to load root folders. Please try again.');
        });
}

// Display root folders in the table
function displayRootFolders(rootFolders) {
    const tableBody = document.getElementById('rootFoldersTableBody');
    
    if (!rootFolders || rootFolders.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No root folders found</td></tr>';
        return;
    }
    
    tableBody.innerHTML = '';
    
    rootFolders.forEach(folder => {
        const row = document.createElement('tr');
        
        // Name column
        const nameCell = document.createElement('td');
        nameCell.textContent = folder.name;
        row.appendChild(nameCell);
        
        // Path column
        const pathCell = document.createElement('td');
        pathCell.textContent = folder.path;
        row.appendChild(pathCell);
        
        // Content type column
        const contentTypeCell = document.createElement('td');
        contentTypeCell.textContent = folder.content_type || 'MANGA';
        row.appendChild(contentTypeCell);
        
        // Status column
        const statusCell = document.createElement('td');
        if (folder.exists) {
            const badge = document.createElement('span');
            badge.className = 'badge bg-success';
            badge.textContent = 'Available';
            statusCell.appendChild(badge);
        } else {
            const badge = document.createElement('span');
            badge.className = 'badge bg-danger';
            badge.textContent = 'Not Found';
            statusCell.appendChild(badge);
        }
        row.appendChild(statusCell);
        
        // Actions column
        const actionsCell = document.createElement('td');
        
        // Edit button
        const editBtn = document.createElement('button');
        editBtn.className = 'btn btn-sm btn-primary me-1';
        editBtn.innerHTML = '<i class="fas fa-edit"></i>';
        editBtn.title = 'Edit Root Folder';
        editBtn.addEventListener('click', () => openEditRootFolderModal(folder));
        actionsCell.appendChild(editBtn);
        
        // Delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-sm btn-danger';
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
        deleteBtn.title = 'Delete Root Folder';
        deleteBtn.addEventListener('click', () => deleteRootFolder(folder.id, folder.name));
        actionsCell.appendChild(deleteBtn);
        
        row.appendChild(actionsCell);
        
        tableBody.appendChild(row);
    });
}

// Show error message
function showError(message) {
    // You can implement this function to show error messages
    console.error(message);
    alert(message);
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Load collections and root folders
    loadCollections();
    loadRootFolders();
    
    // Add collection button
    document.getElementById('addCollectionBtn').addEventListener('click', function() {
        const modal = new bootstrap.Modal(document.getElementById('addCollectionModal'));
        modal.show();
    });
    
    // Save collection button
    document.getElementById('saveCollectionBtn').addEventListener('click', function() {
        const name = document.getElementById('collectionName').value;
        const description = document.getElementById('collectionDescription').value;
        const isDefault = document.getElementById('collectionIsDefault').checked;
        
        if (!name) {
            showError('Collection name is required');
            return;
        }
        
        const data = {
            name: name,
            description: description,
            is_default: isDefault
        };
        
        fetch('/api/collections', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const modal = bootstrap.Modal.getInstance(document.getElementById('addCollectionModal'));
                modal.hide();
                
                // Reset form
                document.getElementById('collectionName').value = '';
                document.getElementById('collectionDescription').value = '';
                document.getElementById('collectionIsDefault').checked = false;
                
                // Reload collections
                loadCollections();
            } else {
                showError('Failed to create collection: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error creating collection:', error);
            showError('Failed to create collection. Please try again.');
        });
    });
    
    // Add root folder button
    document.getElementById('addRootFolderBtn').addEventListener('click', function() {
        // Implement this functionality
        alert('Add root folder functionality not implemented yet');
    });
});

// View collection details
function viewCollectionDetails(collectionId) {
    // Implement this functionality
    console.log('View collection details:', collectionId);
    alert('View collection details functionality not implemented yet');
}

// Open edit collection modal
function openEditCollectionModal(collection) {
    // Implement this functionality
    console.log('Edit collection:', collection);
    alert('Edit collection functionality not implemented yet');
}

// Delete collection
function deleteCollection(collectionId, collectionName) {
    if (confirm(`Are you sure you want to delete the collection "${collectionName}"?`)) {
        fetch(`/api/collections/${collectionId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reload collections
                loadCollections();
            } else {
                showError('Failed to delete collection: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error deleting collection:', error);
            showError('Failed to delete collection. Please try again.');
        });
    }
}

// Open edit root folder modal
function openEditRootFolderModal(folder) {
    // Implement this functionality
    console.log('Edit root folder:', folder);
    alert('Edit root folder functionality not implemented yet');
}

// Delete root folder
function deleteRootFolder(folderId, folderName) {
    if (confirm(`Are you sure you want to delete the root folder "${folderName}"?`)) {
        fetch(`/api/root-folders/${folderId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reload root folders
                loadRootFolders();
            } else {
                showError('Failed to delete root folder: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error deleting root folder:', error);
            showError('Failed to delete root folder. Please try again.');
        });
    }
}
