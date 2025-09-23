/**
 * MangaArr - Main JavaScript file
 */

// Show loading spinner
function showSpinner() {
    // Create spinner overlay if it doesn't exist
    if (!document.getElementById('spinner-overlay')) {
        const overlay = document.createElement('div');
        overlay.id = 'spinner-overlay';
        overlay.className = 'spinner-overlay';
        
        const container = document.createElement('div');
        container.className = 'spinner-container';
        
        const spinner = document.createElement('div');
        spinner.className = 'spinner-border text-primary';
        spinner.setAttribute('role', 'status');
        
        const span = document.createElement('span');
        span.className = 'visually-hidden';
        span.textContent = 'Loading...';
        
        spinner.appendChild(span);
        container.appendChild(spinner);
        
        const message = document.createElement('div');
        message.className = 'mt-2';
        message.textContent = 'Loading...';
        container.appendChild(message);
        
        overlay.appendChild(container);
        document.body.appendChild(overlay);
    } else {
        document.getElementById('spinner-overlay').style.display = 'flex';
    }
}

// Hide loading spinner
function hideSpinner() {
    const overlay = document.getElementById('spinner-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Format date to YYYY-MM-DD
function formatDate(date) {
    const d = new Date(date);
    let month = '' + (d.getMonth() + 1);
    let day = '' + d.getDate();
    const year = d.getFullYear();

    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;

    return [year, month, day].join('-');
}

// Format date to locale string
function formatDateLocale(date) {
    const d = new Date(date);
    return d.toLocaleDateString();
}

// Handle AJAX errors
function handleAjaxError(error) {
    console.error('AJAX Error:', error);
    
    let errorMessage = 'An error occurred while communicating with the server.';
    
    if (error.responseJSON && error.responseJSON.error) {
        errorMessage = error.responseJSON.error;
    }
    
    alert(errorMessage);
}

// Setup Wizard Functions
function initSetupWizard() {
    const steps = document.querySelectorAll('.setup-wizard .step');
    const nextButtons = document.querySelectorAll('.setup-wizard .btn-next');
    const prevButtons = document.querySelectorAll('.setup-wizard .btn-prev');
    const stepIndicators = document.querySelectorAll('.setup-wizard .step-indicator .step-circle');
    const stepLines = document.querySelectorAll('.setup-wizard .step-indicator .step-line');
    
    let currentStep = 0;
    
    // Initialize first step
    steps[currentStep].classList.add('active');
    stepIndicators[currentStep].classList.add('active');
    
    // Next button click handler
    nextButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Validate current step
            if (validateStep(currentStep)) {
                // Hide current step
                steps[currentStep].classList.remove('active');
                
                // Update step indicator
                stepIndicators[currentStep].classList.remove('active');
                stepIndicators[currentStep].classList.add('completed');
                
                if (currentStep < steps.length - 1) {
                    // Update step line
                    stepLines[currentStep].classList.add('completed');
                }
                
                // Show next step
                currentStep++;
                steps[currentStep].classList.add('active');
                stepIndicators[currentStep].classList.add('active');
            }
        });
    });
    
    // Previous button click handler
    prevButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Hide current step
            steps[currentStep].classList.remove('active');
            
            // Update step indicator
            stepIndicators[currentStep].classList.remove('active');
            
            if (currentStep > 0) {
                // Update step line
                stepLines[currentStep - 1].classList.remove('completed');
            }
            
            // Show previous step
            currentStep--;
            steps[currentStep].classList.add('active');
            stepIndicators[currentStep].classList.add('active');
            stepIndicators[currentStep].classList.remove('completed');
        });
    });
}

// Validate step
function validateStep(stepIndex) {
    switch (stepIndex) {
        case 0:
            // Validate collection name
            const collectionName = document.getElementById('collectionName').value;
            if (!collectionName) {
                alert('Please enter a collection name.');
                return false;
            }
            
            // Create collection
            return createCollection();
            
        case 1:
            // Validate root folder
            const rootFolderPath = document.getElementById('rootFolderPath').value;
            const rootFolderName = document.getElementById('rootFolderName').value;
            
            if (!rootFolderPath || !rootFolderName) {
                alert('Please enter both root folder path and name.');
                return false;
            }
            
            // Create root folder
            return createRootFolder();
            
        default:
            return true;
    }
}

// Create collection
function createCollection() {
    const collectionName = document.getElementById('collectionName').value;
    const collectionDescription = document.getElementById('collectionDescription').value;
    const isDefault = document.getElementById('isDefaultCollection').checked;
    
    const data = {
        name: collectionName,
        description: collectionDescription,
        is_default: isDefault
    };
    
    showSpinner();
    
    return fetch('/api/collections', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        hideSpinner();
        if (!response.ok) {
            throw new Error('Failed to create collection');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Store collection ID for later use
            document.getElementById('collectionId').value = data.collection.id;
            return true;
        } else {
            alert(data.error || 'Failed to create collection');
            return false;
        }
    })
    .catch(error => {
        hideSpinner();
        console.error('Error:', error);
        alert('An error occurred while creating the collection');
        return false;
    });
}

// Create root folder
function createRootFolder() {
    const rootFolderPath = document.getElementById('rootFolderPath').value;
    const rootFolderName = document.getElementById('rootFolderName').value;
    const contentType = document.getElementById('contentType').value;
    
    const data = {
        path: rootFolderPath,
        name: rootFolderName,
        content_type: contentType
    };
    
    showSpinner();
    
    return fetch('/api/root-folders', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            hideSpinner();
            throw new Error('Failed to create root folder');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Store root folder ID for later use
            const rootFolderId = data.root_folder.id;
            const collectionId = document.getElementById('collectionId').value;
            
            // Add root folder to collection
            return fetch(`/api/collections/${collectionId}/root-folders/${rootFolderId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        } else {
            hideSpinner();
            alert(data.error || 'Failed to create root folder');
            return false;
        }
    })
    .then(response => {
        hideSpinner();
        if (!response || !response.ok) {
            throw new Error('Failed to add root folder to collection');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            return true;
        } else {
            alert(data.error || 'Failed to add root folder to collection');
            return false;
        }
    })
    .catch(error => {
        hideSpinner();
        console.error('Error:', error);
        alert('An error occurred while setting up the root folder');
        return false;
    });
}

// Document ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize setup wizard if on setup wizard page
    if (document.querySelector('.setup-wizard')) {
        initSetupWizard();
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function(tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.forEach(function(popoverTriggerEl) {
        new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Setup Next button click handlers
    document.getElementById('nextStep1')?.addEventListener('click', function() {
        const nextButton = document.querySelector('.btn-next');
        if (nextButton) {
            nextButton.click();
        }
    });
});
