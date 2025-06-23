export function animateNumber(element, target, suffix = '') {
    let current = 0;
    const step = target / 50;
    function update() {
        current += step;
        if (current >= target) current = target;
        element.textContent = Math.floor(current).toLocaleString() + suffix;
        if (current < target) requestAnimationFrame(update);
    }
    update();
}


export function updateProgress() {

    const charCount = document.getElementById('charCount');
    const progressFill = document.getElementById('progressFill');

    const count = textInput.value.length;
    charCount.textContent = count.toLocaleString();
    const progress = Math.min((count / 2000) * 100, 100);
    progressFill.style.width = progress + '%';

    progressFill.style.background =
        count < 100 ? 'linear-gradient(90deg, #ef4444, #dc2626)' :
        count < 500 ? 'linear-gradient(90deg, #f59e0b, #d97706)' :
        'linear-gradient(90deg, #10b981, #059669)';
}

export function updateTextStats(textInput) {
    const text = textInput.value.trim();
    const wordCount = text ? text.split(/\s+/).length : 0;
    const readingTime = Math.ceil(wordCount / 200);
    const statsHtml = `
        <div class="d-flex gap-3 small text-muted mt-2">
            <span><i class="fas fa-file-word me-1"></i>${wordCount} words</span>
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

export function showError(msg) {
    const div = document.createElement('div');
    div.className = 'alert alert-danger fade show mt-3';
    div.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>${msg}`;
    document.getElementById('summarizeBtn').parentNode.appendChild(div);
    setTimeout(() => div.remove(), 5000);
}


export function showSuccessToast(msg) {
    const toast = document.createElement('div');
    toast.className = 'alert alert-success fade show position-fixed top-0 end-0 m-3';
    toast.innerHTML = `<i class="fas fa-check-circle me-2"></i> ${msg}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

