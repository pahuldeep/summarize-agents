import { selectedAgent } from './agents.js';

export function initShortcuts({ summarizeBtn, textInput }) {
    document.addEventListener('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !summarizeBtn.disabled) {
            summarizeBtn.click();
        }

        if ((e.ctrlKey || e.metaKey) && e.key === 'x') {
            e.preventDefault();
            textInput.value = '';
            textInput.dispatchEvent(new Event('input'));
        }

        if ((e.ctrlKey || e.metaKey) && e.key === 'Q') {
            document.querySelectorAll('.agent-card.selected').forEach(card => {
                card.classList.remove('selected');
                card.querySelector('.agent-icon i').className = 'fas fa-microchip';
            });
            document.getElementById('agentInfo').style.display = 'none';
        }
        
    });
}
