/**
 * E-book manager for MangaArr
 */

class EbookManager {
    /**
     * Initialize the e-book manager.
     */
    constructor() {
        this.initFormatSelectors();
        this.initFileUploads();
    }

    /**
     * Initialize the format selectors.
     */
    initFormatSelectors() {
        // Add event listeners to format selector elements with class 'format-selector'
        document.querySelectorAll('.format-selector').forEach(selector => {
            selector.addEventListener('change', (event) => {
                this.handleFormatChange(event);
            });
        });
    }

    /**
     * Initialize the file upload elements.
     */
    initFileUploads() {
        // Add event listeners to file upload elements with class 'ebook-upload'
        document.querySelectorAll('.ebook-upload').forEach(upload => {
            upload.addEventListener('change', (event) => {
                this.handleFileUpload(event);
            });
        });

        // Add event listeners to delete buttons with class 'delete-ebook'
        document.querySelectorAll('.delete-ebook').forEach(button => {
            button.addEventListener('click', (event) => {
                this.handleDeleteEbook(event);
            });
        });
    }

    /**
     * Handle format change events.
     * @param {Event} event - The change event.
     */
    handleFormatChange(event) {
        const formatSelector = event.target;
        const volumeId = formatSelector.dataset.volumeId;
        const seriesId = formatSelector.dataset.seriesId;
        const format = formatSelector.value;
        const digitalFormatSelector = document.querySelector(`.digital-format-selector[data-volume-id="${volumeId}"]`);
        
        if (format === 'DIGITAL' || format === 'BOTH') {
            if (digitalFormatSelector) {
                digitalFormatSelector.style.display = 'inline-block';
            }
            
            // Show upload button if it exists
            const uploadButton = document.querySelector(`.ebook-upload-button[data-volume-id="${volumeId}"]`);
            if (uploadButton) {
                uploadButton.style.display = 'inline-block';
            }
        } else {
            if (digitalFormatSelector) {
                digitalFormatSelector.style.display = 'none';
            }
            
            // Hide upload button if it exists
            const uploadButton = document.querySelector(`.ebook-upload-button[data-volume-id="${volumeId}"]`);
            if (uploadButton) {
                uploadButton.style.display = 'none';
            }
        }

        // Update the format in the database
        this.updateVolumeFormat(volumeId, format);
    }

    /**
     * Update the volume format in the database.
     * @param {number} volumeId - The volume ID.
     * @param {string} format - The format.
     */
    updateVolumeFormat(volumeId, format) {
        const data = {
            format: format
        };

        // If format is not DIGITAL or BOTH, reset the digital format
        if (format !== 'DIGITAL' && format !== 'BOTH') {
            data.digital_format = 'NONE';
        }

        fetch(`/api/collection/volume/${volumeId}/format`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error updating format:', data.error);
                showToast('Error updating format: ' + data.error, 'error');
            } else {
                console.log('Format updated successfully');
                showToast('Format updated successfully', 'success');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error updating format', 'error');
        });
    }

    /**
     * Handle digital format change events.
     * @param {Event} event - The change event.
     */
    handleDigitalFormatChange(event) {
        const formatSelector = event.target;
        const volumeId = formatSelector.dataset.volumeId;
        const seriesId = formatSelector.dataset.seriesId;
        const digitalFormat = formatSelector.value;

        // Update the digital format in the database
        fetch(`/api/collection/volume/${volumeId}/digital-format`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                digital_format: digitalFormat
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error updating digital format:', data.error);
                showToast('Error updating digital format: ' + data.error, 'error');
            } else {
                console.log('Digital format updated successfully');
                showToast('Digital format updated successfully', 'success');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error updating digital format', 'error');
        });
    }

    /**
     * Handle file upload events.
     * @param {Event} event - The change event.
     */
    handleFileUpload(event) {
        const fileInput = event.target;
        const volumeId = fileInput.dataset.volumeId;
        const seriesId = fileInput.dataset.seriesId;
        
        if (!fileInput.files || fileInput.files.length === 0) {
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);
        formData.append('volume_id', volumeId);
        formData.append('series_id', seriesId);

        // Determine file type from extension
        const fileName = file.name;
        const fileExtension = fileName.split('.').pop().toLowerCase();
        let fileType = 'NONE';

        switch (fileExtension) {
            case 'pdf':
                fileType = 'PDF';
                break;
            case 'epub':
                fileType = 'EPUB';
                break;
            case 'cbz':
                fileType = 'CBZ';
                break;
            case 'cbr':
                fileType = 'CBR';
                break;
            case 'mobi':
                fileType = 'MOBI';
                break;
            case 'azw':
            case 'azw3':
                fileType = 'AZW';
                break;
        }

        formData.append('file_type', fileType);

        // Show loading indicator
        const uploadButton = document.querySelector(`.ebook-upload-button[data-volume-id="${volumeId}"]`);
        if (uploadButton) {
            uploadButton.disabled = true;
            uploadButton.textContent = 'Uploading...';
        }

        // Upload the file
        fetch('/api/ebooks/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error uploading file:', data.error);
                showToast('Error uploading file: ' + data.error, 'error');
            } else {
                console.log('File uploaded successfully');
                showToast('File uploaded successfully', 'success');
                
                // Update the UI to show the file is attached
                this.updateFileAttachmentUI(volumeId, data.file);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error uploading file', 'error');
        })
        .finally(() => {
            // Reset the file input and button
            fileInput.value = '';
            if (uploadButton) {
                uploadButton.disabled = false;
                uploadButton.textContent = 'Upload File';
            }
        });
    }

    /**
     * Handle delete e-book events.
     * @param {Event} event - The click event.
     */
    handleDeleteEbook(event) {
        const deleteButton = event.target;
        const fileId = deleteButton.dataset.fileId;
        const volumeId = deleteButton.dataset.volumeId;

        if (!confirm('Are you sure you want to delete this e-book file? This cannot be undone.')) {
            return;
        }

        // Show loading indicator
        deleteButton.disabled = true;
        deleteButton.textContent = 'Deleting...';

        // Delete the file
        fetch(`/api/ebooks/${fileId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error deleting file:', data.error);
                showToast('Error deleting file: ' + data.error, 'error');
            } else {
                console.log('File deleted successfully');
                showToast('File deleted successfully', 'success');
                
                // Update the UI to show the file is no longer attached
                this.removeFileAttachmentUI(volumeId, fileId);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error deleting file', 'error');
        })
        .finally(() => {
            // Reset the button
            deleteButton.disabled = false;
            deleteButton.textContent = 'Delete';
        });
    }

    /**
     * Update the UI to show a file is attached to a volume.
     * @param {number} volumeId - The volume ID.
     * @param {Object} fileInfo - The file information.
     */
    updateFileAttachmentUI(volumeId, fileInfo) {
        const fileContainer = document.querySelector(`.ebook-file-container[data-volume-id="${volumeId}"]`);
        if (!fileContainer) {
            return;
        }

        // Clear existing files
        fileContainer.innerHTML = '';

        // Create file item
        const fileItem = document.createElement('div');
        fileItem.className = 'ebook-file-item';
        fileItem.dataset.fileId = fileInfo.id;

        // Create file info
        const fileInfoElement = document.createElement('span');
        fileInfoElement.className = 'ebook-file-info';
        fileInfoElement.textContent = fileInfo.original_name || fileInfo.file_name;
        fileItem.appendChild(fileInfoElement);

        // Create download link
        const downloadLink = document.createElement('a');
        downloadLink.className = 'ebook-download-link';
        downloadLink.href = `/api/ebooks/${fileInfo.id}`;
        downloadLink.textContent = 'Download';
        downloadLink.target = '_blank';
        fileItem.appendChild(downloadLink);

        // Create delete button
        const deleteButton = document.createElement('button');
        deleteButton.className = 'delete-ebook btn btn-sm btn-danger';
        deleteButton.textContent = 'Delete';
        deleteButton.dataset.fileId = fileInfo.id;
        deleteButton.dataset.volumeId = volumeId;
        deleteButton.addEventListener('click', (event) => {
            this.handleDeleteEbook(event);
        });
        fileItem.appendChild(deleteButton);

        // Add file item to container
        fileContainer.appendChild(fileItem);

        // Update the digital format dropdown if it exists
        const digitalFormatSelector = document.querySelector(`.digital-format-selector[data-volume-id="${volumeId}"]`);
        if (digitalFormatSelector) {
            digitalFormatSelector.value = fileInfo.file_type;
            digitalFormatSelector.dispatchEvent(new Event('change'));
        }

        // Update the format dropdown if it exists
        const formatSelector = document.querySelector(`.format-selector[data-volume-id="${volumeId}"]`);
        if (formatSelector) {
            // If format is PHYSICAL, change to BOTH since we now have a digital file
            if (formatSelector.value === 'PHYSICAL') {
                formatSelector.value = 'BOTH';
                formatSelector.dispatchEvent(new Event('change'));
            }
        }
    }

    /**
     * Remove a file attachment from the UI.
     * @param {number} volumeId - The volume ID.
     * @param {number} fileId - The file ID.
     */
    removeFileAttachmentUI(volumeId, fileId) {
        const fileItem = document.querySelector(`.ebook-file-item[data-file-id="${fileId}"]`);
        if (fileItem) {
            fileItem.remove();
        }
    }
}

/**
 * Show a toast message.
 * @param {string} message - The message to show.
 * @param {string} type - The type of toast (success, error, warning, info).
 */
function showToast(message, type = 'info') {
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

    // Create the toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center ${type === 'error' ? 'bg-danger' : type === 'success' ? 'bg-success' : 'bg-info'} text-white`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    // Create the toast content
    const toastContent = document.createElement('div');
    toastContent.className = 'd-flex';

    // Create the toast body
    const toastBody = document.createElement('div');
    toastBody.className = 'toast-body';
    toastBody.textContent = message;

    // Create the close button
    const closeButton = document.createElement('button');
    closeButton.className = 'btn-close btn-close-white me-2 m-auto';
    closeButton.setAttribute('data-bs-dismiss', 'toast');
    closeButton.setAttribute('aria-label', 'Close');

    // Assemble the toast
    toastContent.appendChild(toastBody);
    toastContent.appendChild(closeButton);
    toast.appendChild(toastContent);

    // Add the toast to the container
    toastContainer.appendChild(toast);

    // Initialize the toast and show it
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    // Remove the toast after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Initialize the e-book manager when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.ebookManager = new EbookManager();
});
