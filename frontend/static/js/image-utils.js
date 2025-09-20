/**
 * Image utility functions for MangaARR
 */

/**
 * Process an image URL to use the proxy for external images
 * @param {string} url - The original image URL
 * @returns {string} - The processed URL, using proxy if needed
 */
function processImageUrl(url) {
    // If no URL provided, use the fallback
    if (!url) {
        return '/static/img/no-cover.png';
    }
    
    // If URL is already relative, just return it
    if (!url.startsWith('http')) {
        return url;
    }
    
    // Use the proxy for external URLs
    return `/api/proxy/image?url=${encodeURIComponent(url)}`;
}

// Add this function to the global scope
if (typeof window !== 'undefined') {
    window.processImageUrl = processImageUrl;
}
