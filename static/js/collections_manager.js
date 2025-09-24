/**
 * Readloom - Collections Manager
 * Handles the management of multiple collections and their root folders
 */

// Global variables
let collections = [];
let rootFolders = [];
let selectedCollectionId = null;

// Load collections
function loadCollections() {
    fetch('/api/collections')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                collections = data.collections;
                displayCollections();
                
                // Select the first collection by default
                if (collections.length > 0 && !selectedCollectionId) {
                    selectCollection(collections[0].id);
                }
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
function displayCollections() {
    const tableBody = document.getElementById('collectionsTableBody');
    
    if (!collections || collections.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No collections found</td></tr>';
        return;
    }
    
    tableBody.innerHTML = '';
    
    collections.forEach(collection => {
        const row = document.createElement('tr');
        
        // Add selected class if this is the selected collection
        if (selectedCollectionId === collection.id) {
            row.classList.add('table-active');
        }
        
        // Name column
        const nameCell = document.createElement('td');
        nameCell.textContent = collection.name;
        row.appendChild(nameCell);
        
        // Description column
        const descriptionCell = document.createElement('td');
        descriptionCell.textContent = collection.description || '';
        row.appendChild(descriptionCell);
        
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
        
        // Select button
        const selectBtn = document.createElement('button');
        selectBtn.className = 'btn btn-sm btn-info me-1';
        selectBtn.innerHTML = '<i class="fas fa-check"></i>';
        selectBtn.title = 'Select Collection';
        selectBtn.addEventListener('click', () => selectCollection(collection.id));
        actionsCell.appendChild(selectBtn);
        
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
                rootFolders = data.root_folders;
                displayRootFolders();
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
function displayRootFolders() {
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
        
        // Add to collection button (only if a collection is selected)
        if (selectedCollectionId) {
            const addBtn = document.createElement('button');
            addBtn.className = 'btn btn-sm btn-success me-1';
            addBtn.innerHTML = '<i class="fas fa-plus"></i>';
            addBtn.title = 'Add to Selected Collection';
            addBtn.addEventListener('click', () => addRootFolderToCollection(folder.id, selectedCollectionId));
            actionsCell.appendChild(addBtn);
        }
        
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

// Select a collection
function selectCollection(collectionId) {
    selectedCollectionId = collectionId;
    
    // Update UI to show selected collection
    displayCollections();
    displayRootFolders(); // Refresh to show add buttons
    
    // Load collection details
    loadCollectionDetails(collectionId);
    
    // Update selected collection name in the header
    const selectedCollection = collections.find(c => c.id === collectionId);
    if (selectedCollection) {
        document.getElementById('selectedCollectionName').textContent = selectedCollection.name;
        document.getElementById('collectionDetailsCard').classList.remove('d-none');
    }
}

// Load collection details
function loadCollectionDetails(collectionId) {
    // Load root folders for this collection
    fetch(`/api/collections/${collectionId}/root-folders`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayCollectionRootFolders(data.root_folders);
            } else {
                showError('Failed to load collection root folders: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error loading collection root folders:', error);
            showError('Failed to load collection root folders. Please try again.');
        });
    
    // Load series for this collection
    fetch(`/api/collections/${collectionId}/series`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayCollectionSeries(data.series);
            } else {
                showError('Failed to load collection series: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error loading collection series:', error);
            showError('Failed to load collection series. Please try again.');
        });
}

// Display collection root folders
function displayCollectionRootFolders(folders) {
    const tableBody = document.getElementById('collectionRootFoldersTableBody');
    
    if (!folders || folders.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="3" class="text-center">No root folders in this collection</td></tr>';
        return;
    }
    
    tableBody.innerHTML = '';
    
    folders.forEach(folder => {
        const row = document.createElement('tr');
        
        // Name column
        const nameCell = document.createElement('td');
        nameCell.textContent = folder.name;
        row.appendChild(nameCell);
        
        // Path column
        const pathCell = document.createElement('td');
        pathCell.textContent = folder.path;
        row.appendChild(pathCell);
        
        // Actions column
        const actionsCell = document.createElement('td');
        
        // Remove button
        const removeBtn = document.createElement('button');
        removeBtn.className = 'btn btn-sm btn-danger';
        removeBtn.innerHTML = '<i class="fas fa-times"></i>';
        removeBtn.title = 'Remove from Collection';
        removeBtn.addEventListener('click', () => removeRootFolderFromCollection(folder.id, selectedCollectionId));
        actionsCell.appendChild(removeBtn);
        
        row.appendChild(actionsCell);
        
        tableBody.appendChild(row);
    });
}

// Display collection series
function displayCollectionSeries(series) {
    const tableBody = document.getElementById('collectionSeriesTableBody');
    
    if (!series || series.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="3" class="text-center">No series in this collection</td></tr>';
        return;
    }
    
    tableBody.innerHTML = '';
    
    series.forEach(item => {
        const row = document.createElement('tr');
        
        // Title column
        const titleCell = document.createElement('td');
        const titleLink = document.createElement('a');
        titleLink.href = `/series/${item.id}`;
        titleLink.textContent = item.title;
        titleCell.appendChild(titleLink);
        row.appendChild(titleCell);
        
        // Type column
        const typeCell = document.createElement('td');
        typeCell.textContent = item.type || 'MANGA';
        row.appendChild(typeCell);
        
        // Actions column
        const actionsCell = document.createElement('td');
        
        // Remove button
        const removeBtn = document.createElement('button');
        removeBtn.className = 'btn btn-sm btn-danger';
        removeBtn.innerHTML = '<i class="fas fa-times"></i>';
        removeBtn.title = 'Remove from Collection';
        removeBtn.addEventListener('click', () => removeSeriesFromCollection(item.id, selectedCollectionId));
        actionsCell.appendChild(removeBtn);
        
        row.appendChild(actionsCell);
        
        tableBody.appendChild(row);
    });
}

// Add root folder to collection
function addRootFolderToCollection(rootFolderId, collectionId) {
    fetch(`/api/collections/${collectionId}/root-folders/${rootFolderId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Refresh collection details
            loadCollectionDetails(collectionId);
            // Refresh collections list to update counts
            loadCollections();
        } else {
            showError('Failed to add root folder to collection: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error adding root folder to collection:', error);
        showError('Failed to add root folder to collection. Please try again.');
    });
}

// Remove root folder from collection
function removeRootFolderFromCollection(rootFolderId, collectionId) {
    // Convert IDs to integers to ensure proper comparison
    rootFolderId = parseInt(rootFolderId, 10);
    collectionId = parseInt(collectionId, 10);
    
    if (confirm('Are you sure you want to remove this root folder from the collection?')) {
        console.log(`Attempting to remove root folder ${rootFolderId} from collection ${collectionId}`);
        
        fetch(`/api/collections/${collectionId}/root-folders/${rootFolderId}`, {
            method: 'DELETE'
        })
        .then(response => {
            console.log('Remove root folder response status:', response.status);
            return response.json().catch(err => {
                console.error('Error parsing JSON response:', err);
                return { success: false, error: 'Invalid server response' };
            });
        })
        .then(data => {
            console.log('Remove root folder response data:', data);
            if (data.success) {
                console.log(`Successfully removed root folder ${rootFolderId} from collection ${collectionId}`);
                // Refresh collection details
                loadCollectionDetails(collectionId);
                // Refresh collections list to update counts
                loadCollections();
            } else {
                showError('Failed to remove root folder from collection: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error removing root folder from collection:', error);
            showError('Failed to remove root folder from collection. Please try again.');
        });
    }
}

// Remove series from collection
function removeSeriesFromCollection(seriesId, collectionId) {
    // Convert IDs to integers to ensure proper comparison
    seriesId = parseInt(seriesId, 10);
    collectionId = parseInt(collectionId, 10);
    
    if (confirm('Are you sure you want to remove this series from the collection?')) {
        console.log(`Attempting to remove series ${seriesId} from collection ${collectionId}`);
        
        fetch(`/api/collections/${collectionId}/series/${seriesId}`, {
            method: 'DELETE'
        })
        .then(response => {
            console.log('Remove series response status:', response.status);
            return response.json().catch(err => {
                console.error('Error parsing JSON response:', err);
                return { success: false, error: 'Invalid server response' };
            });
        })
        .then(data => {
            console.log('Remove series response data:', data);
            if (data.success) {
                console.log(`Successfully removed series ${seriesId} from collection ${collectionId}`);
                // Refresh collection details
                loadCollectionDetails(collectionId);
                // Refresh collections list to update counts
                loadCollections();
            } else {
                showError('Failed to remove series from collection: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error removing series from collection:', error);
            showError('Failed to remove series from collection. Please try again.');
        });
    }
}

// Open add collection modal
function openAddCollectionModal() {
    // Reset form
    document.getElementById('collectionName').value = '';
    document.getElementById('collectionDescription').value = '';
    document.getElementById('collectionIsDefault').checked = false;
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('addCollectionModal'));
    modal.show();
}

// Save new collection
function saveCollection() {
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
            // Hide modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addCollectionModal'));
            modal.hide();
            
            // Refresh collections
            loadCollections();
            
            // Select the new collection
            if (data.collection && data.collection.id) {
                selectCollection(data.collection.id);
            }
        } else {
            showError('Failed to create collection: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error creating collection:', error);
        showError('Failed to create collection. Please try again.');
    });
}

// Open edit collection modal
function openEditCollectionModal(collection) {
    // Set form values
    document.getElementById('editCollectionId').value = collection.id;
    document.getElementById('editCollectionName').value = collection.name;
    document.getElementById('editCollectionDescription').value = collection.description || '';
    document.getElementById('editCollectionIsDefault').checked = collection.is_default;
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('editCollectionModal'));
    modal.show();
}

// Update collection
function updateCollection() {
    const id = document.getElementById('editCollectionId').value;
    const name = document.getElementById('editCollectionName').value;
    const description = document.getElementById('editCollectionDescription').value;
    const isDefault = document.getElementById('editCollectionIsDefault').checked;
    
    if (!name) {
        showError('Collection name is required');
        return;
    }
    
    const data = {
        name: name,
        description: description,
        is_default: isDefault
    };
    
    fetch(`/api/collections/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Hide modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editCollectionModal'));
            modal.hide();
            
            // Refresh collections
            loadCollections();
            
            // Refresh collection details if this is the selected collection
            if (selectedCollectionId === parseInt(id)) {
                loadCollectionDetails(selectedCollectionId);
                
                // Update selected collection name in the header
                if (data.collection) {
                    document.getElementById('selectedCollectionName').textContent = data.collection.name;
                }
            }
        } else {
            showError('Failed to update collection: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error updating collection:', error);
        showError('Failed to update collection. Please try again.');
    });
}

// Delete collection
function deleteCollection(collectionId, collectionName) {
    // Convert collectionId to integer to ensure proper comparison
    collectionId = parseInt(collectionId, 10);
    
    if (confirm(`Are you sure you want to delete the collection "${collectionName}"?`)) {
        console.log(`Attempting to delete collection ${collectionId}: ${collectionName}`);
        
        fetch(`/api/collections/${collectionId}`, {
            method: 'DELETE'
        })
        .then(response => {
            console.log('Delete collection response status:', response.status);
            return response.json().catch(err => {
                console.error('Error parsing JSON response:', err);
                return { success: false, error: 'Invalid server response' };
            });
        })
        .then(data => {
            console.log('Delete collection response data:', data);
            if (data.success) {
                console.log(`Successfully deleted collection ${collectionId}`);
                // Refresh collections
                loadCollections();
                
                // If this was the selected collection, clear selection
                if (selectedCollectionId === collectionId) {
                    selectedCollectionId = null;
                    document.getElementById('collectionDetailsCard').classList.add('d-none');
                }
            } else {
                showError('Failed to delete collection: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error deleting collection:', error);
            showError('Failed to delete collection. Please try again.');
        });
    }
}

// Open add root folder modal
function openAddRootFolderModal() {
    // Reset form
    document.getElementById('rootFolderPath').value = '';
    document.getElementById('rootFolderName').value = '';
    document.getElementById('rootFolderContentType').value = 'MANGA';
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('addRootFolderModal'));
    modal.show();
}

// Save new root folder
function saveRootFolder() {
    const path = document.getElementById('rootFolderPath').value;
    const name = document.getElementById('rootFolderName').value;
    const contentType = document.getElementById('rootFolderContentType').value;
    
    if (!path || !name) {
        showError('Root folder path and name are required');
        return;
    }
    
    const data = {
        path: path,
        name: name,
        content_type: contentType
    };
    
    fetch('/api/root-folders', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Hide modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addRootFolderModal'));
            modal.hide();
            
            // Refresh root folders
            loadRootFolders();
            
            // If a collection is selected, ask if user wants to add this root folder to the collection
            if (selectedCollectionId && confirm('Do you want to add this root folder to the selected collection?')) {
                addRootFolderToCollection(data.root_folder.id, selectedCollectionId);
            }
        } else {
            showError('Failed to create root folder: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error creating root folder:', error);
        showError('Failed to create root folder. Please try again.');
    });
}

// Open edit root folder modal
function openEditRootFolderModal(folder) {
    // Set form values
    document.getElementById('editRootFolderId').value = folder.id;
    document.getElementById('editRootFolderPath').value = folder.path;
    document.getElementById('editRootFolderName').value = folder.name;
    document.getElementById('editRootFolderContentType').value = folder.content_type || 'MANGA';
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('editRootFolderModal'));
    modal.show();
}

// Update root folder
function updateRootFolder() {
    const id = document.getElementById('editRootFolderId').value;
    const path = document.getElementById('editRootFolderPath').value;
    const name = document.getElementById('editRootFolderName').value;
    const contentType = document.getElementById('editRootFolderContentType').value;
    
    if (!path || !name) {
        showError('Root folder path and name are required');
        return;
    }
    
    const data = {
        path: path,
        name: name,
        content_type: contentType
    };
    
    fetch(`/api/root-folders/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Hide modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editRootFolderModal'));
            modal.hide();
            
            // Refresh root folders
            loadRootFolders();
            
            // Refresh collection details if this root folder is in the selected collection
            if (selectedCollectionId) {
                loadCollectionDetails(selectedCollectionId);
            }
        } else {
            showError('Failed to update root folder: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error updating root folder:', error);
        showError('Failed to update root folder. Please try again.');
    });
}

// Delete root folder
function deleteRootFolder(rootFolderId, rootFolderName) {
    if (confirm(`Are you sure you want to delete the root folder "${rootFolderName}"?`)) {
        console.log(`Attempting to delete root folder ${rootFolderId}: ${rootFolderName}`);
        
        fetch(`/api/root-folders/${rootFolderId}`, {
            method: 'DELETE'
        })
        .then(response => {
            console.log('Delete root folder response status:', response.status);
            return response.json().catch(err => {
                console.error('Error parsing JSON response:', err);
                return { success: false, error: 'Invalid server response' };
            });
        })
        .then(data => {
            console.log('Delete root folder response data:', data);
            if (data.success) {
                console.log(`Successfully deleted root folder ${rootFolderId}`);
                // Refresh root folders
                loadRootFolders();
                
                // Refresh collection details if a collection is selected
                if (selectedCollectionId) {
                    loadCollectionDetails(selectedCollectionId);
                }
                
                // Refresh collections list to update counts
                loadCollections();
            } else {
                showError('Failed to delete root folder: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error deleting root folder:', error);
            showError('Failed to delete root folder. Please try again.');
        });
    }
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
    document.getElementById('addCollectionBtn').addEventListener('click', openAddCollectionModal);
    
    // Save collection button
    document.getElementById('saveCollectionBtn').addEventListener('click', saveCollection);
    
    // Update collection button
    document.getElementById('updateCollectionBtn').addEventListener('click', updateCollection);
    
    // Add root folder button
    document.getElementById('addRootFolderBtn').addEventListener('click', openAddRootFolderModal);
    
    // Save root folder button
    document.getElementById('saveRootFolderBtn').addEventListener('click', saveRootFolder);
    
    // Update root folder button
    document.getElementById('updateRootFolderBtn').addEventListener('click', updateRootFolder);
});
