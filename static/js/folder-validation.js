/**
 * Folder validation utilities for the MangaArr UI.
 */

/**
 * Validate if a folder exists and is writable.
 * 
 * @param {string} folderPath - The path to the folder to validate.
 * @param {function} callback - Callback function to handle the validation result.
 */
function validateFolder(folderPath, callback) {
    fetch('/api/folders/validate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ path: folderPath }),
    })
    .then(response => response.json())
    .then(data => {
        callback(data);
    })
    .catch(error => {
        console.error('Error validating folder:', error);
        callback({
            success: false,
            exists: false,
            writable: false,
            message: 'Error validating folder: ' + error.message
        });
    });
}

/**
 * Create a folder if it doesn't exist and validate it.
 * 
 * @param {string} folderPath - The path to the folder to create and validate.
 * @param {function} callback - Callback function to handle the creation result.
 */
function createFolder(folderPath, callback) {
    fetch('/api/folders/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ path: folderPath }),
    })
    .then(response => response.json())
    .then(data => {
        callback(data);
    })
    .catch(error => {
        console.error('Error creating folder:', error);
        callback({
            success: false,
            exists: false,
            writable: false,
            created: false,
            message: 'Error creating folder: ' + error.message
        });
    });
}

/**
 * Add folder validation UI to a form.
 * 
 * @param {string} inputId - The ID of the folder path input field.
 * @param {string} validationContainerId - The ID of the container for validation messages.
 * @param {string} validateButtonId - The ID of the validate button.
 * @param {string} createButtonId - The ID of the create button (optional).
 */
function setupFolderValidation(inputId, validationContainerId, validateButtonId, createButtonId = null) {
    const folderInput = document.getElementById(inputId);
    const validationContainer = document.getElementById(validationContainerId);
    const validateButton = document.getElementById(validateButtonId);
    const createButton = createButtonId ? document.getElementById(createButtonId) : null;
    
    if (!folderInput || !validationContainer || !validateButton) {
        console.error('Missing required elements for folder validation');
        return;
    }
    
    // Add validation button click handler
    validateButton.addEventListener('click', function(event) {
        event.preventDefault();
        
        const folderPath = folderInput.value.trim();
        if (!folderPath) {
            showValidationMessage(validationContainer, 'Please enter a folder path', 'warning');
            return;
        }
        
        // Show loading state
        showValidationMessage(validationContainer, 'Validating folder...', 'info');
        
        validateFolder(folderPath, function(result) {
            if (result.success) {
                showValidationMessage(validationContainer, result.message, 'success');
                folderInput.classList.add('is-valid');
                folderInput.classList.remove('is-invalid');
                
                // Enable create button if it exists
                if (createButton) {
                    createButton.disabled = false;
                }
            } else {
                showValidationMessage(validationContainer, result.message, 'danger');
                folderInput.classList.add('is-invalid');
                folderInput.classList.remove('is-valid');
                
                // Show create button if folder doesn't exist and create button exists
                if (!result.exists && createButton) {
                    createButton.disabled = false;
                    createButton.style.display = 'inline-block';
                }
            }
        });
    });
    
    // Add create button click handler if it exists
    if (createButton) {
        createButton.addEventListener('click', function(event) {
            event.preventDefault();
            
            const folderPath = folderInput.value.trim();
            if (!folderPath) {
                showValidationMessage(validationContainer, 'Please enter a folder path', 'warning');
                return;
            }
            
            // Show loading state
            showValidationMessage(validationContainer, 'Creating folder...', 'info');
            
            createFolder(folderPath, function(result) {
                if (result.success) {
                    showValidationMessage(validationContainer, result.message, 'success');
                    folderInput.classList.add('is-valid');
                    folderInput.classList.remove('is-invalid');
                    
                    // Enable create button
                    createButton.disabled = false;
                } else {
                    showValidationMessage(validationContainer, result.message, 'danger');
                    folderInput.classList.add('is-invalid');
                    folderInput.classList.remove('is-valid');
                }
            });
        });
    }
    
    // Add input change handler to reset validation
    folderInput.addEventListener('input', function() {
        folderInput.classList.remove('is-valid', 'is-invalid');
        validationContainer.innerHTML = '';
        
        // Disable create button if it exists
        if (createButton) {
            createButton.disabled = true;
            createButton.style.display = 'none';
        }
    });
}

/**
 * Show a validation message in the specified container.
 * 
 * @param {HTMLElement} container - The container element for the message.
 * @param {string} message - The message to display.
 * @param {string} type - The message type (success, danger, warning, info).
 */
function showValidationMessage(container, message, type) {
    container.innerHTML = `
        <div class="alert alert-${type} mt-2 mb-0">
            ${message}
        </div>
    `;
}
