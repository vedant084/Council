const API_URL = 'http://localhost:8000';

document.getElementById('discussion-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const topic = document.getElementById('topic').value;
    const rounds = parseInt(document.getElementById('rounds').value);
    const submitBtn = document.getElementById('submit-btn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const discussionContent = document.getElementById('discussion-content');
    
    // Reset UI
    submitBtn.disabled = true;
    loading.classList.remove('hidden');
    results.classList.add('hidden');
    discussionContent.innerHTML = '';
    
    try {
        const response = await fetch(`${API_URL}/council/discuss`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                topic: topic,
                rounds: rounds
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        discussionContent.innerHTML = `
            <div class="error">
                <strong>Error:</strong> ${error.message}
                <br><br>
                Make sure the backend server is running on ${API_URL}
            </div>
        `;
        results.classList.remove('hidden');
    } finally {
        loading.classList.add('hidden');
        submitBtn.disabled = false;
    }
});

function displayResults(data) {
    const discussionContent = document.getElementById('discussion-content');
    let html = '';
    
    data.rounds.forEach((round, index) => {
        const isSummary = round.round === 'Summary';
        const roundTitle = isSummary ? 'Final Summary' : `Round ${round.round}`;
        
        html += `
            <div class="round-container">
                <div class="round-header">${roundTitle}</div>
        `;
        
        Object.entries(round.responses).forEach(([name, content]) => {
            const isChairman = name.includes('Chairman');
            html += `
                <div class="response-card">
                    <div class="response-header">
                        <span class="response-name ${isChairman ? 'chairman' : ''}">${name}</span>
                    </div>
                    <div class="response-content">${escapeHtml(content)}</div>
                </div>
            `;
        });
        
        html += `</div>`;
    });
    
    discussionContent.innerHTML = html;
    document.getElementById('results').classList.remove('hidden');
    
    // Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

