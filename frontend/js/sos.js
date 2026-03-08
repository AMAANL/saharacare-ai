const API_URL = 'http://localhost:5001';

const sosBtn = document.getElementById('sos-btn');
const sosStatus = document.getElementById('sos-status');

if (sosBtn) {
    sosBtn.addEventListener('click', () => {
        sosStatus.innerText = "Getting Location...";

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(async (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;

                try {
                    const response = await fetch(`${API_URL}/sos`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', "X-User-Id": localStorage.getItem("user_id") || "arthur" },
                        body: JSON.stringify({
                            latitude: lat,
                            longitude: lng
                        })
                    });

                    if (response.ok) {
                        sosStatus.innerText = "Emergency contacts alerted! Help is on the way.";
                        sosStatus.classList.add('text-emergency');
                    } else {
                        sosStatus.innerText = "Failed to send SOS.";
                    }
                } catch (error) {
                    sosStatus.innerText = "Network Error: Could not send SOS.";
                    console.error('Error sending SOS:', error);
                }
            }, (error) => {
                sosStatus.innerText = "Could not get location. Ensure permissions are granted.";
                console.error('Geolocation error:', error);
            });
        } else {
            sosStatus.innerText = "Geolocation is not supported by this browser.";
        }
    });
}
