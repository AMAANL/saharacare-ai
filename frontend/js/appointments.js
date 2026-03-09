const APPT_API_URL = '/appointments';

async function fetchAppointments() {
    const listElement = document.getElementById('appointment-list');

    try {
        const response = await fetch(APPT_API_URL);
        const data = await response.json();
        const appointments = data.appointments || [];

        if (appointments.length === 0) {
            listElement.innerHTML = `
                <div class="p-8 bg-white dark:bg-slate-800 rounded-2xl shadow-lg border-2 border-dashed border-slate-200 dark:border-slate-700 text-center">
                    <span class="material-symbols-outlined text-6xl text-slate-300 mb-4">event_busy</span>
                    <p class="text-2xl font-bold text-slate-400">No appointments scheduled</p>
                </div>
            `;
            return;
        }

        listElement.innerHTML = '';
        appointments.forEach(appt => {
            const card = document.createElement('div');
            card.className = "p-6 bg-white dark:bg-slate-800 rounded-3xl shadow-xl border-l-8 border-blue-500 flex items-center justify-between gap-4 transform transition-all hover:scale-[1.02]";

            card.innerHTML = `
                <div class="flex items-center gap-6">
                    <div class="size-20 bg-blue-500 text-white rounded-2xl flex flex-col items-center justify-center p-2 shadow-inner">
                        <span class="text-lg font-black uppercase text-blue-100">${appt.date.split('-')[2]}</span>
                        <span class="text-sm font-bold opacity-80 uppercase">${new Date(appt.date).toLocaleString('default', { month: 'short' })}</span>
                    </div>
                    <div>
                        <h3 class="text-3xl font-black text-slate-900 dark:text-white mb-2 leading-tight">${appt.title}</h3>
                        <div class="flex items-center gap-4 text-slate-500 dark:text-slate-400">
                            <div class="flex items-center gap-1">
                                <span class="material-symbols-outlined text-xl">schedule</span>
                                <span class="text-xl font-bold">${appt.time}</span>
                            </div>
                            <div class="flex items-center gap-1">
                                <span class="material-symbols-outlined text-xl">event</span>
                                <span class="text-xl font-bold">${appt.date}</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="hidden sm:flex size-16 bg-blue-50 dark:bg-blue-900/20 text-blue-500 rounded-full items-center justify-center">
                    <span class="material-symbols-outlined text-4xl">arrow_forward_ios</span>
                </div>
            `;
            listElement.appendChild(card);
        });

    } catch (error) {
        console.error('Error fetching appointments:', error);
        listElement.innerHTML = '<p class="text-red-500 text-xl font-bold text-center p-8 bg-white dark:bg-slate-800 rounded-2xl shadow-lg">Failed to load appointments. Please check your internet connection.</p>';
    }
}

document.addEventListener('DOMContentLoaded', fetchAppointments);
