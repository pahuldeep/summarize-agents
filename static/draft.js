export function autoSaveDraft(inputElement) {
    let saveTimeout;
    inputElement.addEventListener('input', () => {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            localStorage.setItem('draft_text', inputElement.value);
        }, 1000);
    });
}

export function restoreDraft(inputElement) {
    const draft = localStorage.getItem('draft_text');
    if (draft && draft.length > 0) {
        if (confirm('📝 Restore previous draft?')) {
            inputElement.value = draft;
            inputElement.dispatchEvent(new Event('input'));
        } else {
            localStorage.removeItem('draft_text');
        }
    }
}

export function clearDraft() {
    localStorage.removeItem('draft_text');
}
