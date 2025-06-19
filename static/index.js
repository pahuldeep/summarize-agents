let selectedAgent = null;

// Agent selection with improved animations
document.querySelectorAll('.agent-card').forEach(card => {
    card.addEventListener('click', function() {
        // Remove previous selection
        document.querySelectorAll('.agent-card').forEach(c => {
            c.classList.remove('selected');
            c.querySelector('.agent-icon i').className = 'fas fa-microchip';
        });
        
        // Select current with animation
        this.classList.add('selected');
        this.querySelector('.agent-icon i').className = 'fas fa-check';
        selectedAgent = this.dataset.agent;
        
        // Update UI with smooth transition
        const agentInfo = document.getElementById('agentInfo');
        document.getElementById('selectedAgentName').textContent = selectedAgent;
        agentInfo.style.display = 'block';
        agentInfo.classList.add('fade-in');
        
        updateSummarizeButton();
    });
});

// Enhanced text input handling
const textInput = document.getElementById('textInput');
const charCount = document.getElementById('charCount');
const progressFill = document.getElementById('progressFill');
const summarizeBtn = document.getElementById('summarizeBtn');
const summaryContent = document.getElementById('summaryContent');

textInput.addEventListener('input', function() {
    const count = this.value.length;
    charCount.textContent = count.toLocaleString();
    
    // Update progress bar (assuming 2000 chars as ideal length)
    const progress = Math.min((count / 2000) * 100, 100);
    progressFill.style.width = progress + '%';
    
    // Change color based on length
    if (count < 100) {
        progressFill.style.background = 'linear-gradient(90deg, #ef4444, #dc2626)';
    } else if (count < 500) {
        progressFill.style.background = 'linear-gradient(90deg, #f59e0b, #d97706)';
    } else {
        progressFill.style.background = 'linear-gradient(90deg, #10b981, #059669)';
    }
    
    updateSummarizeButton();
});

function updateSummarizeButton() {
    const hasText = textInput.value.trim().length > 0;
    const hasAgent = selectedAgent !== null;
    const isReady = hasText && hasAgent;
    
    summarizeBtn.disabled = !isReady;
    
    if (isReady) {
        summarizeBtn.classList.add('pulse');
    } else {
        summarizeBtn.classList.remove('pulse');
    }
}

// Clear text with confirmation for large content
document.getElementById('clearText').addEventListener('click', function() {
    const textLength = textInput.value.length;
    if (textLength > 500) {
        if (!confirm('Are you sure you want to clear this text? You have ' + textLength + ' characters.')) {
            return;
        }
    }
    
    textInput.value = '';
    charCount.textContent = '0';
    progressFill.style.width = '0%';
    updateSummarizeButton();
});

// Enhanced summarize function
summarizeBtn.addEventListener('click', async function() {
    const text = textInput.value.trim();
    if (!text || !selectedAgent) return;
    
    // Show loading state
    summarizeBtn.disabled = true;
    summarizeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    
    
    summaryContent.innerHTML = '<span class="loading-dots">Processing</span>';
    try {
        const startTime = Date.now();
        const response = await fetch('/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                agent: selectedAgent
            })
        });

        const data = await response.json();
        const processingTime = ((Date.now() - startTime) / 1000).toFixed(1);
        
        if (data.success) {
            displayResult(data, text, processingTime);
            loadHistory();
            
            // Show success animation
            summarizeBtn.innerHTML = '<i class="fas fa-check me-2"></i>Complete!';
            setTimeout(() => {
                summarizeBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Generate';
            }, 2000);
        } else {
            showError('Error: ' + data.error);
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        // Hide loading
        document.querySelector('.loading-spinner').style.display = 'none';
        updateSummarizeButton();
    }
});

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert after the summarize button
    summarizeBtn.parentNode.insertBefore(errorDiv, summarizeBtn.nextSibling);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 5000);
}

function displayResult(data, originalText, processingTime) {
    const results = document.getElementById('results');
    const summaryContent = document.getElementById('summaryContent');
    const resultAgent = document.getElementById('resultAgent');
    const resultTime = document.getElementById('resultTime');
    const originalLength = document.getElementById('originalLength');
    const summaryLength = document.getElementById('summaryLength');
    const compressionRatio = document.getElementById('compressionRatio');
    
    // Format summary with proper line breaks and styling
    const formattedSummary = data.summary
        .replace(/\n/g, '<br>')
        .replace(/^- /gm, '<i class="fas fa-arrow-right text-primary me-2"></i>');
    
    summaryContent.innerHTML = formattedSummary;
    resultAgent.textContent = data.agent;
    resultTime.textContent = `${new Date().toLocaleString()} (${processingTime}s)`;
    
    // Animate numbers
    animateNumber(originalLength, originalText.length);
    animateNumber(summaryLength, data.summary.length);
    
    const ratio = ((1 - data.summary.length / originalText.length) * 100).toFixed(1);
    animateNumber(compressionRatio, ratio, '%');
    
    results.style.display = 'block';
    results.classList.add('fade-in');
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function animateNumber(element, target, suffix = '') {
    let current = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current).toLocaleString() + suffix;
    }, 20);
}

// Enhanced history functions
async function loadHistory() {
    try {
        const response = await fetch('/history');
        const history = await response.json();
        displayHistory(history);
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

function displayHistory(history) {
    const container = document.getElementById('historyContainer');
    
    if (history.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-clipboard-list"></i>
                <h6>No summaries yet</h6>
                <p class="small mb-0">Your recent summaries will appear here</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = history.reverse().map((item, index) => `
        <div class="history-item p-3" style="animation-delay: ${index * 0.1}s">
            <div class="d-flex justify-content-between align-items-center mb-2">                        

                <span class="badge bg-primary">${item.agent}</span>
                <small class="text-muted">${item.timestamp}</small>
            </div>
            <div class="mb-2">
                <small class="text-muted fw-semibold">Original:</small>
                <p class="small mb-1 text-truncate">${item.original_text}</p>
            </div>
            <div>
                <small class="text-muted fw-semibold">Summary:</small>
                <p class="small mb-0">${item.summary.replace(/\n/g, '<br>').substring(0, 200)}${item.summary.length > 200 ? '...' : ''}</p>
            </div>
            <div class="mt-2 d-flex justify-content-between align-items-center">
                <small class="text-muted">
                    <i class="fas fa-compress-alt me-1"></i>
                    ${Math.round((1 - item.summary.length / item.original_text.length) * 100)}% compression
                </small>
                <button class="btn btn-sm btn-outline-primary copy-summary" data-summary="${item.summary.replace(/"/g, '&quot;')}">
                    <i class="fas fa-copy"></i>
                </button>
            </div>
        </div>
    `).join('');
    
    // Add copy functionality
    container.querySelectorAll('.copy-summary').forEach(btn => {
        btn.addEventListener('click', function() {
            const summary = this.dataset.summary.replace(/&quot;/g, '"');
            navigator.clipboard.writeText(summary).then(() => {
                const originalIcon = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check text-success"></i>';
                setTimeout(() => {
                    this.innerHTML = originalIcon;
                }, 2000);
            });
        });
    });
}

// History controls with confirmation
document.getElementById('refreshHistory').addEventListener('click', function() {
    this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    loadHistory().then(() => {
        setTimeout(() => {
            this.innerHTML = '<i class="fas fa-sync-alt"></i>';
        }, 500);
    });
});

document.getElementById('clearHistory').addEventListener('click', async function() {
    if (confirm('🗑️ Clear all history?\n\nThis action cannot be undone.')) {
        try {
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            await fetch('/clear_history', { method: 'POST' });
            loadHistory();
            
            // Show success message
            const toast = document.createElement('div');
            toast.className = 'alert alert-success position-fixed top-0 end-0 m-3 fade-in';
            toast.style.zIndex = '9999';
            toast.innerHTML = `
                <i class="fas fa-check-circle me-2"></i>
                History cleared successfully!
            `;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.remove();
            }, 3000);
            
        } catch (error) {
            showError('Error clearing history: ' + error.message);
        } finally {
            this.innerHTML = '<i class="fas fa-trash"></i>';
        }
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to summarize
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (!summarizeBtn.disabled) {
            summarizeBtn.click();
        }
    }
    
    // Ctrl/Cmd + K to clear text
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('clearText').click();
    }
    
    // Escape to clear selection
    if (e.key === 'Escape') {
        document.querySelectorAll('.agent-card.selected').forEach(card => {
            card.classList.remove('selected');
            card.querySelector('.agent-icon i').className = 'fas fa-microchip';
        });
        selectedAgent = null;
        document.getElementById('agentInfo').style.display = 'none';
        updateSummarizeButton();
    }
});

// Enhanced drag and drop functionality
const dropZone = textInput;

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
    dropZone.style.borderColor = 'var(--primary-color)';
    dropZone.style.backgroundColor = 'rgba(99, 102, 241, 0.05)';
}

function unhighlight(e) {
    dropZone.style.borderColor = 'var(--border-color)';
    dropZone.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
}

dropZone.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        const file = files[0];
        if (file.type === 'text/plain') {
            const reader = new FileReader();
            reader.onload = function(e) {
                textInput.value = e.target.result;
                textInput.dispatchEvent(new Event('input'));
            };
            reader.readAsText(file);
        } else {
            showError('Please drop a text file (.txt)');
        }
    }
}

// Auto-save draft functionality
let saveTimeout;
textInput.addEventListener('input', function() {
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(() => {
        localStorage.setItem('draft_text', this.value);
    }, 1000);
});

// Load draft on page load
window.addEventListener('load', function() {
    const draft = localStorage.getItem('draft_text');
    if (draft && draft.length > 0) {
        const shouldRestore = confirm('📝 Restore previous draft?\n\nWe found unsaved text from your last session.');
        if (shouldRestore) {
            textInput.value = draft;
            textInput.dispatchEvent(new Event('input'));
        } else {
            localStorage.removeItem('draft_text');
        }
    }
});

// Clear draft when successfully summarized
function clearDraft() {
    localStorage.removeItem('draft_text');
}

// Add word count and reading time estimation
function updateTextStats() {
    const text = textInput.value;
    const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
    const readingTime = Math.ceil(wordCount / 200); // Average 200 words per minute
    
    const statsHtml = `
        <div class="d-flex gap-3 small text-muted mt-2">
            <span><i class="fas fa-file-word me-1"></i>${wordCount.toLocaleString()} words</span>
            <span><i class="fas fa-clock me-1"></i>~${readingTime} min read</span>
        </div>
    `;
    
    let statsContainer = document.getElementById('textStats');
    if (!statsContainer) {
        statsContainer = document.createElement('div');
        statsContainer.id = 'textStats';
        textInput.parentNode.appendChild(statsContainer);
    }
    statsContainer.innerHTML = statsHtml;
}

textInput.addEventListener('input', updateTextStats);

// Initialize
loadHistory();
updateTextStats();

// Add smooth scrolling for better UX
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Performance monitoring
let performanceData = {
    pageLoadTime: Date.now(),
    summariesGenerated: 0,
    totalProcessingTime: 0
};

// Track page performance
window.addEventListener('load', () => {
    performanceData.pageLoadTime = Date.now() - performanceData.pageLoadTime;
});

// Add a footer with performance stats (for development)
if (window.location.hostname === 'localhost') {
    const footer = document.createElement('div');
    footer.className = 'text-center py-3 text-muted small';
    footer.innerHTML = `
        <div class="container">
            <i class="fas fa-code me-1"></i>
            Development Mode | 
            <span id="perfStats">Page loaded in ${performanceData.pageLoadTime}ms</span>
        </div>
    `;
    document.body.appendChild(footer);
}

// Add tooltips for better UX
const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});

// Accessibility improvements
document.addEventListener('keydown', function(e) {
    // Tab navigation improvements
    if (e.key === 'Tab') {
        document.body.classList.add('keyboard-navigation');
    }
});

document.addEventListener('mousedown', function() {
    document.body.classList.remove('keyboard-navigation');
});

// Add focus styles for keyboard navigation
const style = document.createElement('style');
style.textContent = `
    .keyboard-navigation *:focus {
        outline: 2px solid var(--primary-color) !important;
        outline-offset: 2px !important;
    }
`;
document.head.appendChild(style);