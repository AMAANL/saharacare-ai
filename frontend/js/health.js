const API_URL = '';

const saveBtn = document.getElementById('save-health-btn');
if (saveBtn) {
    saveBtn.addEventListener('click', async () => {
        const sys = document.getElementById('systolic').value;
        const dia = document.getElementById('diastolic').value;
        const gluc = document.getElementById('glucose').value;

        try {
            const response = await fetch(`${API_URL}/health_log`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', "X-User-Id": localStorage.getItem("user_id") || "arthur" },
                body: JSON.stringify({
                    systolic: sys,
                    diastolic: dia,
                    glucose: gluc
                })
            });
            const data = await response.json();

            const aiText = document.getElementById('ai-status-text');
            const aiEmoji = document.getElementById('ai-status-emoji');

            aiText.innerText = data.analysis;

            if (data.analysis === 'High blood pressure detected') {
                aiEmoji.innerText = '🚨';
                aiText.classList.add('text-red-500');
            } else {
                aiEmoji.innerText = '✅';
                aiText.classList.remove('text-red-500');
                aiText.classList.add('text-primary');
            }
        } catch (error) {
            console.error('Error saving health log:', error);
        }
    });
}
