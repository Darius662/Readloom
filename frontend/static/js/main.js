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

// Document ready
$(document).ready(function() {
    // Add CSRF token to all AJAX requests
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrf_token'));
            }
        }
    });
    
    // Get cookie by name
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});
