const API_URL = '';

async function registerUser(email, password) {
    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', "X-User-Id": localStorage.getItem("user_id") || "arthur" },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        console.log("Auth:", data);
    } catch (error) {
        console.error("Error during register:", error);
    }
}
