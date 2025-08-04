/**
 * SpiralBridge Web Interface JavaScript
 * Handles scraping, saving, searching, and UI interactions
 */

// Global state
let currentScrapedData = null;
let isInitialized = false;

/**
 * Initialize all event listeners
 */
function initializeEventListeners() {
    // Scraping functionality
    document.getElementById('scrapeBtn').addEventListener('click', handleScrape);
    document.getElementById('urlInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleScrape();
        }
    });
    
    // Content management
    document.getElementById('saveBtn').addEventListener('click', handleSave);
    document.getElementById('copyBtn').addEventListener('click', handleCopy);
    document.getElementById('clearBtn').addEventListener('click', handleClear);
    
    // Search functionality
    document.getElementById('searchBtn').addEventListener('click', handleSearch);
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
    
    // System functionality
    document.getElementById('refreshStatsBtn').addEventListener('click', refreshStats);
    document.getElementById('healthCheckBtn').addEventListener('click', performHealthCheck);
}

/**
 * Handle URL scraping
 */
async function handleScrape() {
    const urlInput = document.getElementById('urlInput');
    const scrapeBtn = document.getElementById('scrapeBtn');
    const statusArea = document.getElementById('scrapeStatus');
    const progressIndicator = document.getElementById('progressIndicator');
    
    const url = urlInput.value.trim();
    if (!url) {
        showStatus('Please enter a URL to scrape', 'error');
        urlInput.focus();
        return;
    }
    
    // Enhanced URL validation
    if (!isValidURL(url)) {
        showStatus('Please enter a valid URL', 'error');
        urlInput.focus();
        return;
    }
    
    // Check if URL is from supported platform
    if (!isSupportedPlatform(url)) {
        const supportedPlatforms = [
            'claude.ai/share/*',
            'gemini.google.com/share/*',
            'chat.openai.com/share/*',
            'chatgpt.com/share/*',
            'app.warp.dev/session/*'
        ];
        showStatus(`URL must be from supported platforms: ${supportedPlatforms.join(', ')}`, 'error');
        urlInput.focus();
        return;
    }
    
    // Update UI for loading state with enhanced progress indication
    scrapeBtn.disabled = true;
    scrapeBtn.textContent = '🔄 Scraping...';
    urlInput.disabled = true;
    progressIndicator.style.display = 'flex';
    updateProgressText('Initializing scraper...');
    showStatus('Connecting to scraping service...', 'info');
    
    try {
        const response = await fetch('/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentScrapedData = data;
            displayScrapedContent(data);
            showStatus(`Successfully scraped ${data.metadata.word_count} words from ${data.platform.toUpperCase()}`, 'success');
        } else {
            showStatus(`Scraping failed: ${data.message}`, 'error');
            if (data.supported_platforms) {
                showStatus(`Supported platforms: ${data.supported_platforms.join(', ')}`, 'info');
            }
        }
    } catch (error) {
        console.error('Scraping error:', error);
        showStatus('Network error occurred during scraping', 'error');
    } finally {
        // Reset UI state
        resetScrapingUI();
    }
}

/**
 * Display scraped content in the results section
 */
function displayScrapedContent(data) {
    const resultsSection = document.getElementById('resultsSection');
    const contentArea = document.getElementById('contentArea');
    const contentLength = document.getElementById('contentLength');
    const contentPlatform = document.getElementById('contentPlatform');
    const wordCount = document.getElementById('wordCount');
    
    // Update metadata display
    contentLength.textContent = `${data.metadata.content_length} chars`;
    contentPlatform.textContent = `Platform: ${data.platform.toUpperCase()}`;
    wordCount.textContent = `${data.metadata.word_count} words`;
    
    // Update content area
    contentArea.value = data.content;
    contentArea.style.height = 'auto';
    contentArea.style.height = Math.min(contentArea.scrollHeight, 400) + 'px';
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Handle saving content to memory system
 */
async function handleSave() {
    if (!currentScrapedData) {
        showStatus('No content to save', 'error');
        return;
    }
    
    const saveBtn = document.getElementById('saveBtn');
    saveBtn.disabled = true;
    saveBtn.textContent = '💾 Saving...';
    
    try {
        const response = await fetch('/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: currentScrapedData.content,
                platform: currentScrapedData.platform,
                url: currentScrapedData.metadata.url,
                session_type: 'scraped_conversation',
                tags: [currentScrapedData.platform, 'scraped_conversation', 'ai_conversation']
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showStatus(`Content saved to memory system successfully`, 'success');
            updateStats(data.stats);
        } else {
            showStatus(`Save failed: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('Save error:', error);
        showStatus('Network error occurred while saving', 'error');
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = '💾 Save to Memory';
    }
}

/**
 * Handle copying content to clipboard
 */
async function handleCopy() {
    if (!currentScrapedData) {
        showStatus('No content to copy', 'error');
        return;
    }
    
    const copyBtn = document.getElementById('copyBtn');
    const originalText = copyBtn.textContent;
    
    copyBtn.disabled = true;
    copyBtn.textContent = '📋 Copying...';
    
    try {
        const success = await copyToClipboard(currentScrapedData.content);
        
        if (success) {
            showStatus('Content copied to clipboard successfully', 'success');
            copyBtn.textContent = '✅ Copied!';
            
            // Reset button text after 2 seconds
            setTimeout(() => {
                copyBtn.textContent = originalText;
            }, 2000);
        } else {
            throw new Error('All clipboard methods failed');
        }
    } catch (error) {
        console.error('Copy error:', error);
        showStatus('Failed to copy content to clipboard', 'error');
    } finally {
        copyBtn.disabled = false;
    }
}

/**
 * Handle clearing content
 */
function handleClear() {
    currentScrapedData = null;
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('contentArea').value = '';
    document.getElementById('urlInput').value = '';
    showStatus('Content cleared', 'info');
}

/**
 * Handle memory search
 */
async function handleSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const searchResults = document.getElementById('searchResults');
    
    const query = searchInput.value.trim();
    if (!query) {
        showStatus('Please enter a search query', 'error');
        return;
    }
    
    searchBtn.disabled = true;
    searchBtn.textContent = '🔍 Searching...';
    
    try {
        const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.success) {
            displaySearchResults(data.results, query);
            showStatus(`Found ${data.count} results for "${query}"`, 'success');
        } else {
            showStatus(`Search failed: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('Search error:', error);
        showStatus('Network error occurred during search', 'error');
    } finally {
        searchBtn.disabled = false;
        searchBtn.textContent = 'Search';
    }
}

/**
 * Display search results
 */
function displaySearchResults(results, query) {
    const searchResults = document.getElementById('searchResults');
    
    if (results.length === 0) {
        searchResults.innerHTML = '<p class="no-results">No results found</p>';
        return;
    }
    
    const resultsHtml = results.map(result => `
        <div class="search-result">
            <div class="result-header">
                <span class="result-file">${result.file}</span>
                <span class="result-category">${result.category}</span>
            </div>
            <div class="result-date">${new Date(result.created).toLocaleDateString()}</div>
            <div class="result-snippet">${result.snippet}</div>
        </div>
    `).join('');
    
    searchResults.innerHTML = resultsHtml;
}

/**
 * Refresh statistics
 */
async function refreshStats() {
    const refreshBtn = document.getElementById('refreshStatsBtn');
    refreshBtn.disabled = true;
    refreshBtn.textContent = '🔄 Refreshing...';
    
    try {
        const response = await fetch('/stats');
        const data = await response.json();
        
        if (data.success) {
            updateStats(data.stats);
            showStatus('Statistics refreshed', 'success');
        } else {
            showStatus('Failed to refresh statistics', 'error');
        }
    } catch (error) {
        console.error('Stats refresh error:', error);
        showStatus('Network error occurred while refreshing stats', 'error');
    } finally {
        refreshBtn.disabled = false;
        refreshBtn.textContent = '🔄 Refresh Stats';
    }
}

/**
 * Perform health check
 */
async function performHealthCheck() {
    const healthBtn = document.getElementById('healthCheckBtn');
    const systemStatus = document.getElementById('systemStatus');
    
    healthBtn.disabled = true;
    healthBtn.textContent = '🏥 Checking...';
    
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        if (data.success) {
            updateSystemStatus('healthy', 'System Operational');
            showStatus('System health check passed', 'success');
        } else {
            updateSystemStatus('unhealthy', 'System Issues Detected');
            showStatus('System health check failed', 'error');
        }
    } catch (error) {
        console.error('Health check error:', error);
        updateSystemStatus('unhealthy', 'System Unreachable');
        showStatus('Health check failed - network error', 'error');
    } finally {
        healthBtn.disabled = false;
        healthBtn.textContent = '🏥 Health Check';
    }
}

/**
 * Update system status display
 */
function updateSystemStatus(status, text) {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');
    
    statusDot.className = `status-dot ${status}`;
    statusText.textContent = text;
}

/**
 * Update statistics display
 */
function updateStats(stats) {
    document.getElementById('totalConversations').textContent = stats.total_conversations || 0;
    document.getElementById('storageSize').textContent = stats.storage_size_mb || 0;
    document.getElementById('knowledgeEntries').textContent = stats.knowledge_entries || 0;
}

/**
 * Load initial statistics
 */
async function loadInitialStats() {
    try {
        const response = await fetch('/stats');
        const data = await response.json();
        
        if (data.success) {
            updateStats(data.stats);
        }
    } catch (error) {
        console.error('Failed to load initial stats:', error);
    }
}

/**
 * Show status message
 */
function showStatus(message, type = 'info') {
    const statusArea = document.getElementById('scrapeStatus');
    
    const typeEmojis = {
        'success': '✅',
        'error': '❌',
        'info': 'ℹ️',
        'warning': '⚠️'
    };
    
    statusArea.innerHTML = `
        <div class="status-message ${type}">
            ${typeEmojis[type] || 'ℹ️'} ${message}
        </div>
    `;
    
    statusArea.style.display = 'block';
    
    // Auto-hide success and info messages after 5 seconds
    if (type === 'success' || type === 'info') {
        setTimeout(() => {
            statusArea.style.display = 'none';
        }, 5000);
    }
}

// =======================
// UTILITY FUNCTIONS
// =======================

/**
 * Validate URL format
 * @param {string} url - The URL to validate
 * @returns {boolean} - True if valid URL
 */
function isValidURL(url) {
    try {
        const urlObject = new URL(url);
        return urlObject.protocol === 'http:' || urlObject.protocol === 'https:';
    } catch {
        return false;
    }
}

/**
 * Check if URL is from a supported platform
 * @param {string} url - The URL to check
 * @returns {boolean} - True if from supported platform
 */
function isSupportedPlatform(url) {
    try {
        const urlObject = new URL(url);
        const hostname = urlObject.hostname.toLowerCase();
        
        // Check for Claude
        if (hostname.includes('claude.ai')) {
            return true;
        }
        
        // Check for Gemini (multiple domains)
        if (hostname.includes('gemini.google.com') || 
            hostname.includes('g.co') || 
            hostname.includes('bard.google.com')) {
            return true;
        }
        
        // Check for ChatGPT (multiple domains)
        if (hostname.includes('chat.openai.com') || 
            hostname.includes('chatgpt.com')) {
            return true;
        }
        
        // Check for Warp
        if (hostname.includes('app.warp.dev')) {
            return true;
        }
        
        return false;
    } catch (error) {
        console.error('URL validation error:', error);
        return false;
    }
}

/**
 * Update progress indicator text
 * @param {string} text - Progress text to display
 */
function updateProgressText(text) {
    const progressText = document.querySelector('.progress-text');
    if (progressText) {
        progressText.textContent = text;
    }
}

/**
 * Reset scraping UI to default state
 */
function resetScrapingUI() {
    const scrapeBtn = document.getElementById('scrapeBtn');
    const urlInput = document.getElementById('urlInput');
    const progressIndicator = document.getElementById('progressIndicator');
    
    // Reset button
    scrapeBtn.disabled = false;
    scrapeBtn.textContent = 'Scrape Conversation';
    
    // Re-enable input
    urlInput.disabled = false;
    
    // Hide progress indicator
    if (progressIndicator) {
        progressIndicator.style.display = 'none';
    }
}

/**
 * Debounce function for input validation
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} - Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Format file size for display
 * @param {number} bytes - Size in bytes
 * @returns {string} - Formatted size string
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Animate element with fade effect
 * @param {HTMLElement} element - Element to animate
 * @param {string} direction - 'in' or 'out'
 * @param {number} duration - Animation duration in ms
 */
function fadeAnimation(element, direction, duration = 300) {
    if (direction === 'in') {
        element.style.opacity = '0';
        element.style.display = 'block';
        element.style.transition = `opacity ${duration}ms ease-in-out`;
        
        requestAnimationFrame(() => {
            element.style.opacity = '1';
        });
    } else if (direction === 'out') {
        element.style.transition = `opacity ${duration}ms ease-in-out`;
        element.style.opacity = '0';
        
        setTimeout(() => {
            element.style.display = 'none';
        }, duration);
    }
}

/**
 * Handle form submission with preventDefault
 * @param {Event} event - Form submit event
 */
function handleFormSubmit(event) {
    event.preventDefault();
    
    // Determine which form was submitted
    const form = event.target;
    const formId = form.id;
    
    switch (formId) {
        case 'scrapeForm':
            handleScrape();
            break;
        case 'searchForm':
            handleSearch();
            break;
        default:
            console.warn('Unknown form submitted:', formId);
    }
}

/**
 * Initialize form event listeners with proper preventDefault handling
 */
function initializeFormHandlers() {
    // Handle form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // Real-time URL validation
    const urlInput = document.getElementById('urlInput');
    if (urlInput) {
        const debouncedValidation = debounce((url) => {
            if (url && !isValidURL(url)) {
                urlInput.classList.add('invalid');
            } else if (url && !isSupportedPlatform(url)) {
                urlInput.classList.add('unsupported');
            } else {
                urlInput.classList.remove('invalid', 'unsupported');
            }
        }, 500);
        
        urlInput.addEventListener('input', (e) => {
            debouncedValidation(e.target.value.trim());
        });
    }
}

/**
 * Enhanced initialization with form handlers
 */
function enhancedInitialization() {
    if (isInitialized) return;
    
    try {
        initializeEventListeners();
        initializeFormHandlers();
        loadInitialStats();
        isInitialized = true;
        console.log('SpiralBridge JavaScript initialized successfully');
    } catch (error) {
        console.error('Failed to initialize SpiralBridge:', error);
    }
}

/**
 * Enhanced clipboard functionality with multiple fallbacks
 * @param {string} text - Text to copy to clipboard
 * @returns {Promise<boolean>} - Success status
 */
async function copyToClipboard(text) {
    // Method 1: Modern Clipboard API
    if (navigator.clipboard && window.isSecureContext) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (error) {
            console.warn('Clipboard API failed:', error);
        }
    }
    
    // Method 2: Legacy execCommand fallback
    try {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-9999px';
        textArea.style.top = '-9999px';
        document.body.appendChild(textArea);
        
        textArea.focus();
        textArea.select();
        const success = document.execCommand('copy');
        document.body.removeChild(textArea);
        
        if (success) {
            return true;
        }
    } catch (error) {
        console.warn('execCommand copy failed:', error);
    }
    
    // Method 3: Try to use content area selection
    try {
        const contentArea = document.getElementById('contentArea');
        if (contentArea) {
            contentArea.select();
            contentArea.setSelectionRange(0, 99999); // For mobile devices
            const success = document.execCommand('copy');
            if (success) {
                return true;
            }
        }
    } catch (error) {
        console.warn('Content area copy failed:', error);
    }
    
    return false;
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', enhancedInitialization);
