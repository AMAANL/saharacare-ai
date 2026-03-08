const API_URL = '';

async function fetchCaretakerData() {
    try {
        // Fetch Medications to calculate adherence
        const medRes = await fetch(`${API_URL}/medications`, { headers: { "X-User-Id": localStorage.getItem("user_id") } });
        const medData = await medRes.json();
        const meds = medData.medications || [];

        let takenCount = 0;
        meds.forEach(m => { if (m.taken) takenCount++; });

        const adherencePercent = meds.length > 0 ? Math.round((takenCount / meds.length) * 100) : 100;

        // Update Circular Meter
        document.getElementById('med-circle').setAttribute('stroke-dasharray', `${adherencePercent}, 100`);
        document.getElementById('med-percent').textContent = `${adherencePercent}%`;

        // Fetch Health Logs for graph and table
        const healthRes = await fetch(`${API_URL}/health_logs`, { headers: { "X-User-Id": localStorage.getItem("user_id") } });
        const healthData = await healthRes.json();
        const logs = healthData.logs || [];

        renderHealthTable(logs);
        renderBPChart(logs);

    } catch (e) {
        console.error("Failed to load caretaker dashboard data:", e);
    }
}

function renderHealthTable(logs) {
    const tbody = document.getElementById('health-log-tbody');
    tbody.innerHTML = '';
    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="py-4 px-6 text-gray-500 text-center">No health logs found for this period.</td></tr>';
        return;
    }

    logs.reverse().forEach(log => {
        const dateObj = new Date(log.date);
        const dateString = dateObj.toLocaleDateString() + ' ' + dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        // Basic re-analysis for table format UI
        let statusHtml = '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Normal</span>';
        if (log.systolic > 150) {
            statusHtml = '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">High BP Alert</span>';
        }

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="py-4 px-6 text-sm text-gray-900">${dateString}</td>
            <td class="py-4 px-6 text-sm font-medium ${log.systolic > 150 ? 'text-red-600' : 'text-gray-900'}">${log.systolic}/${log.diastolic} mmHg</td>
            <td class="py-4 px-6 text-sm text-gray-500">${log.glucose > 0 ? log.glucose + ' mg/dL' : '-'}</td>
            <td class="py-4 px-6 text-sm">${statusHtml}</td>
        `;
        tbody.appendChild(tr);
    });
}

function renderBPChart(logs) {
    // If no logs, put dummy data for demo purposes so graph isn't empty
    let chartParams = {
        labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5'],
        systolic: [120, 122, 118, 125, 121],
        diastolic: [80, 82, 79, 81, 80]
    };

    if (logs.length > 0) {
        chartParams.labels = logs.map((_, i) => `Log ${i + 1}`);
        chartParams.systolic = logs.map(l => l.systolic);
        chartParams.diastolic = logs.map(l => l.diastolic);
    }

    const ctx = document.getElementById('bpChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartParams.labels,
            datasets: [
                {
                    label: 'Systolic',
                    data: chartParams.systolic,
                    borderColor: 'rgba(239, 68, 68, 1)', // Red
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.3
                },
                {
                    label: 'Diastolic',
                    data: chartParams.diastolic,
                    borderColor: 'rgba(59, 130, 246, 1)', // Blue
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    suggestedMin: 60,
                    suggestedMax: 160
                }
            },
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    fetchCaretakerData();
    fetchAdminMeds();
    fetchAdminAppts();

    document.getElementById('add-med-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('med-name').value;
        const time = document.getElementById('med-time').value;
        const date = document.getElementById('med-date').value;

        await fetch(`${API_URL}/add_medication`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', "X-User-Id": localStorage.getItem("user_id") || "arthur" },
            body: JSON.stringify({ name, time, date })
        });
        document.getElementById('add-med-form').reset();
        fetchAdminMeds();
    });

    document.getElementById('add-appt-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = document.getElementById('appt-title').value;
        const date = document.getElementById('appt-date').value;
        const time = document.getElementById('appt-time').value;

        await fetch(`${API_URL}/add_appointment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', "X-User-Id": localStorage.getItem("user_id") || "arthur" },
            body: JSON.stringify({ title, date, time })
        });
        document.getElementById('add-appt-form').reset();
        fetchAdminAppts();
    });
});

window.downloadReport = function () {
    window.location.href = `${API_URL}/generate_report`;
};

async function fetchAdminMeds() {
    const res = await fetch(`${API_URL}/medications`, { headers: { "X-User-Id": localStorage.getItem("user_id") } });
    const data = await res.json();
    const list = document.getElementById('med-list-admin');
    list.innerHTML = '';
    (data.medications || []).forEach(m => {
        const li = document.createElement('li');
        li.className = 'py-3 flex justify-between items-center';
        li.innerHTML = `
            <div>
                <span class="font-bold">${m.name}</span> <span class="text-gray-500">at ${m.time}</span>
                <span class="text-xs text-blue-500 block">${m.date ? 'Date: ' + m.date : 'Daily'}</span>
            </div>
            <button onclick="deleteMed(${m.id})" class="text-red-500 hover:text-red-700 font-bold">Delete</button>
        `;
        list.appendChild(li);
    });
}

window.deleteMed = async function (id) {
    await fetch(`${API_URL}/delete_medication/${id}`, { method: 'DELETE' });
    fetchAdminMeds();
}

async function fetchAdminAppts() {
    const res = await fetch(`${API_URL}/appointments`, { headers: { "X-User-Id": localStorage.getItem("user_id") } });
    const data = await res.json();
    const list = document.getElementById('appt-list-admin');
    list.innerHTML = '';
    (data.appointments || []).forEach(a => {
        const li = document.createElement('li');
        li.className = 'py-3 flex justify-between items-center';
        li.innerHTML = `
            <div>
                <span class="font-bold">${a.title}</span> <span class="text-gray-500 block">${a.date} at ${a.time}</span>
            </div>
            <button onclick="deleteAppt(${a.id})" class="text-red-500 hover:text-red-700 font-bold">Delete</button>
        `;
        list.appendChild(li);
    });
}

window.deleteAppt = async function (id) {
    await fetch(`${API_URL}/delete_appointment/${id}`, { method: 'DELETE' });
    fetchAdminAppts();
}
