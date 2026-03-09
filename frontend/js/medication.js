const API_URL = '';

async function fetchMedications() {
    try {
        const response = await fetch(`${API_URL}/medications`, { headers: { "X-User-Id": localStorage.getItem("user_id") } });
        const data = await response.json();
        const meds = data.medications || [];

        const todayStr = new Date().toISOString().split('T')[0];

        // Today's meds (Daily or specifically dated for today)
        const todayMeds = meds.filter(m => !m.date || m.date === todayStr);
        // Future dated meds
        const upcomingMeds = meds.filter(m => m.date && m.date > todayStr);

        renderMedications(todayMeds, upcomingMeds);
    } catch (e) {
        console.error('Failed to fetch medications:', e);
    }
}

async function markAsTaken(id) {
    try {
        // Ensure ID is passed correctly
        const response = await fetch(`${API_URL}/take_medication`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', "X-User-Id": localStorage.getItem("user_id") || "arthur" },
            body: JSON.stringify({ id: Number(id) })
        });
        if (response.ok) {
            fetchMedications();
        }
    } catch (e) {
        console.error('Failed to update medication:', e);
    }
}

function renderMedications(todayMeds, upcomingMeds) {
    const list = document.getElementById('medication-list');
    if (!list) return;

    list.innerHTML = '';
    const todayStr = new Date().toISOString().split('T')[0];

    // 1. Render Today's Section
    if (todayMeds.length > 0) {
        list.innerHTML += '<h2 class="text-2xl font-bold mt-4 mb-4 text-primary">Today</h2>';
        todayMeds.forEach(med => {
            const isTakenToday = med.last_taken_date === todayStr;
            const card = createMedCard(med, isTakenToday);
            list.innerHTML += card;
        });
    }

    // 2. Render Upcoming Section
    if (upcomingMeds.length > 0) {
        list.innerHTML += '<h2 class="text-2xl font-bold mt-8 mb-4 text-slate-400">Upcoming (Dated)</h2>';
        upcomingMeds.forEach(med => {
            const card = createMedCard(med, false, true);
            list.innerHTML += card;
        });
    }
}

function createMedCard(med, isTaken, isUpcoming = false) {
    const colorClass = isTaken ? 'border-primary opacity-50' : (isUpcoming ? 'border-blue-400' : 'border-red-500');

    let actionBtn = '';
    if (isTaken) {
        actionBtn = `<button disabled class="w-full bg-slate-200 dark:bg-slate-800 text-slate-500 dark:text-slate-400 font-bold py-5 rounded-xl text-2xl flex items-center justify-center gap-3 cursor-not-allowed">Taken Today</button>`;
    } else if (isUpcoming) {
        actionBtn = `<div class="text-center py-3 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-xl font-bold italic">Starts on ${med.date}</div>`;
    } else {
        actionBtn = `<button onclick="markAsTaken(${med.id})" class="w-full bg-primary hover:bg-primary/90 text-white font-bold py-5 rounded-xl text-2xl shadow-md flex items-center justify-center gap-3 transition-colors active:scale-95">Mark as Taken</button>`;
    }

    return `
    <div class="bg-white dark:bg-slate-900 rounded-xl shadow-lg border-l-8 ${colorClass} overflow-hidden transform transition-all">
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
            ${actionBtn}
        </div>
    </div>
    `;
}

document.addEventListener('DOMContentLoaded', fetchMedications);
