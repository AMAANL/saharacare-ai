const API_URL = 'http://localhost:5001';

async function fetchMedications() {
    try {
        const response = await fetch(`${API_URL}/medications`, { headers: { "X-User-Id": localStorage.getItem("user_id") } });
        const data = await response.json();
        const meds = data.medications || [];

        // Filter meds to just today or daily (empty date)
        const todayStr = new Date().toISOString().split('T')[0];
        const activeMeds = meds.filter(m => !m.date || m.date === todayStr);

        renderMedications(activeMeds);
    } catch (e) {
        console.error('Failed to fetch medications:', e);
    }
}

async function markAsTaken(id) {
    try {
        const response = await fetch(`${API_URL}/take_medication`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', "X-User-Id": localStorage.getItem("user_id") || "arthur" },
            body: JSON.stringify({ id })
        });
        if (response.ok) {
            fetchMedications();
        }
    } catch (e) {
        console.error('Failed to update medication:', e);
    }
}

function renderMedications(medications) {
    const list = document.getElementById('medication-list');
    if (!list) return;

    list.innerHTML = '';

    medications.forEach(med => {
        const isTaken = med.taken;
        const colorClass = isTaken ? 'border-primary opacity-50' : 'border-red-500';
        const takingBtn = isTaken ?
            `<button disabled class="w-full bg-slate-200 dark:bg-slate-800 text-slate-500 dark:text-slate-400 font-bold py-5 rounded-xl text-2xl flex items-center justify-center gap-3 cursor-not-allowed">Already Taken</button>` :
            `<button onclick="markAsTaken(${med.id})" class="w-full bg-primary hover:bg-primary/90 text-white font-bold py-5 rounded-xl text-2xl shadow-md flex items-center justify-center gap-3 transition-colors">Mark as Taken</button>`;

        const html = `
        <div class="bg-white dark:bg-slate-900 rounded-xl shadow-lg border-l-8 ${colorClass} overflow-hidden">
            <div class="p-6">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h3 class="text-3xl font-black">${med.name}</h3>
                        <div class="flex items-center gap-2 text-slate-500 dark:text-slate-400 mt-1">
                            <span class="material-symbols-outlined">schedule</span>
                            <span class="text-xl font-medium">${med.time}</span>
                        </div>
                    </div>
                </div>
                ${takingBtn}
            </div>
        </div>
        `;
        list.innerHTML += html;
    });
}

document.addEventListener('DOMContentLoaded', fetchMedications);
