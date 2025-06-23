// DOM references first
const textInput = document.getElementById('textInput');
const summarizeBtn = document.getElementById('summarizeBtn');
const summaryContent = document.getElementById('summaryContent');


const USE_STREAMING = false; // Set to true to enable streaming mode


import { initAgentSelection, selectedAgent } from './agents.js';
import { showError, updateTextStats, animateNumber, updateProgress } from './ui.js';
import { loadHistory, displayHistory, clearHistory } from './history.js';
import { autoSaveDraft, restoreDraft, clearDraft } from './draft.js';
import { initShortcuts } from './shortcuts.js';


// Init UI
initAgentSelection(updateSummarizeButton);
autoSaveDraft(textInput);
restoreDraft(textInput);
updateTextStats(textInput);
initShortcuts({ summarizeBtn, textInput });

updateProgress();

function updateSummarizeButton() {
    const hasText = textInput.value.trim().length > 0;
    const hasAgent = selectedAgent !== null;
    summarizeBtn.disabled = !(hasText && hasAgent);
    summarizeBtn.classList.toggle('pulse', hasText && hasAgent);
}

textInput.addEventListener('input', () => {
    updateProgress();
    updateTextStats(textInput);
    updateSummarizeButton();
   

});

summarizeBtn.addEventListener('click', async () => {
    const text = textInput.value.trim();
    if (!text || !selectedAgent) return;

    summarizeBtn.disabled = true;
    summarizeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';

    summaryContent.innerHTML = '<span class="loading-dots streaming-dots">Processing</span>';

    const startTime = Date.now();
    if (USE_STREAMING) await streamSummary(text, selectedAgent, startTime);
    else await standardSummary(text, selectedAgent, startTime);

    summarizeBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Generate';
    updateSummarizeButton();
});

// Normal fetch fallback
async function standardSummary(text, agent, startTime) {
    const res = await fetch('/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, agent })
    });

    const data = await res.json();
    if (data.success) {
        const duration = ((Date.now() - startTime) / 1000).toFixed(1);
        displayResult(data, text, duration);
        loadHistory(displayHistory);

    } else {
        showError(data.error);
    }
}

// Simplified streaming (uses TextDecoder instead of EventSource)
async function streamSummary(text, agent, startTime) {
    try {
        const res = await fetch('/summarize_stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, agent })
        });

        if (!res.ok || !res.body) {
            showError('Stream failed.');
            return;
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let summary = '';

        summaryContent.innerHTML = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            if (!chunk.trim()) continue;

            summary += chunk;
            summaryContent.innerHTML += `<p">${chunk.trim()}</p>`;
        }

        const duration = ((Date.now() - startTime) / 1000).toFixed(1);
        displayResult({ summary, agent }, text, duration);
        loadHistory(displayHistory);

    } catch (e) {
        showError(e.message);
    }
}


// function displayResult(data, originalText, time) {
//     const resultAgent = document.getElementById('resultAgent');
//     const resultTime = document.getElementById('resultTime');
//     const originalLength = document.getElementById('originalLength');
//     const summaryLength = document.getElementById('summaryLength');
//     const compressionRatio = document.getElementById('compressionRatio');

//     summaryContent.innerHTML = window.marked
//         ? window.marked.parse(data.summary)
//         : data.summary.replace(/\n/g, '<br>');

//     resultAgent.textContent = data.agent;
//     resultTime.textContent = `${new Date().toLocaleString()} (${time}s)`;
//     animateNumber(originalLength, originalText.length);
//     animateNumber(summaryLength, data.summary.length);
//     const ratio = ((1 - data.summary.length / originalText.length) * 100).toFixed(1);
//     animateNumber(compressionRatio, ratio, '%');

//     document.getElementById('results').style.display = 'block';
// }
function displayResult(data, originalText, time) {
    const resultAgent = document.getElementById('resultAgent');
    const resultTime = document.getElementById('resultTime');
    const originalLength = document.getElementById('originalLength');
    const summaryLength = document.getElementById('summaryLength');
    const compressionRatio = document.getElementById('compressionRatio');

    let formatted = '';

    if (window.marked && typeof window.marked.parse === 'function') {
        // Use marked for full Markdown rendering
        formatted = `<div class="markdown-output">${window.marked.parse(data.summary)}</div>`;
    } else {
        // Fallback basic formatter
        const lines = data.summary.split('\n').filter(Boolean);
        const firstLine = lines[0];
        const bullets = lines.slice(1).filter(l => /^[-•]/.test(l));

        formatted = `<div class="markdown-output">`;
        if (firstLine) {
            formatted += `<h4>${firstLine}</h4>`;
        }
        if (bullets.length) {
            formatted += `<ul>`;
            bullets.forEach(line => {
                formatted += `<li>${line.replace(/^[-•]\s*/, '')}</li>`;
            });
            formatted += `</ul>`;
        }
        formatted += `</div>`;
    }

    summaryContent.innerHTML = formatted;

    resultAgent.textContent = data.agent;
    resultTime.textContent = `${new Date().toLocaleString()} (${time}s)`;
    animateNumber(originalLength, originalText.length);
    animateNumber(summaryLength, data.summary.length);

    const ratio = ((1 - data.summary.length / originalText.length) * 100).toFixed(1);
    animateNumber(compressionRatio, ratio, '%');

    document.getElementById('results').style.display = 'block';
}


// Button handlers
document.getElementById('refreshHistory').addEventListener('click', () => loadHistory(displayHistory));
document.getElementById('clearHistory').addEventListener('click', async () => {
    if (confirm('🗑️ Clear all history?')) {
        await clearHistory(() => loadHistory(displayHistory));
        showSuccessToast('History cleared!');
    }
});

