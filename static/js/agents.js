export let selectedAgent = null;

export function initAgentSelection(updateUI) {
    document.querySelectorAll('.agent-card').forEach(card => {
        card.addEventListener('click', function () {
            document.querySelectorAll('.agent-card').forEach(c => {
                c.classList.remove('selected');
                c.querySelector('.agent-icon i').className = 'fas fa-microchip';
            });

            this.classList.add('selected');
            this.querySelector('.agent-icon i').className = 'fas fa-check';
            selectedAgent = this.dataset.agent;

            document.getElementById('selectedAgentName').textContent = selectedAgent;
            document.getElementById('agentInfo').style.display = 'block';
            document.getElementById('agentInfo').classList.add('fade-in');

            updateUI();
        });
    });
}
