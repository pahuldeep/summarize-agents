export async function loadHistory(displayHistory) {
    const res = await fetch('/history');
    const history = await res.json();
    displayHistory(history);
}

export function displayHistory(history) {
    const container = document.getElementById('historyContainer');
    if (!history.length) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-clipboard-list"></i>
                <h6>No summaries yet</h6>
            </div>`;
        return;
    }

    container.innerHTML = history.reverse().map(item => `
        <div class="history-item p-3">
            <div class="d-flex justify-content-between">
                <span class="badge bg-primary">${item.agent}</span>
                <small class="text-muted">${item.timestamp}</small>
            </div>
            <div class="mt-2">
                <small>Original:</small>
                <p class="small">${item.original_text}</p>
            </div>
            <div>
                <small>Summary:</small>
                <p class="small">${item.summary.replace(/\n/g, '<br>')}</p>
            </div>
        </div>
    `).join('');
}

export async function clearHistory(callback) {
    await fetch('/clear_history', { method: 'POST' });
    callback();
}
