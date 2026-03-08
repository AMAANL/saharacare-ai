
# SaharaCare AI - Elderly Care Companion

**SaharaCare AI** is a comprehensive, full-stack companion platform designed specifically for senior citizens (60+) and their caretakers. The application prioritizes extreme accessibility with high-contrast UI, large interactive elements, and a Hindi-speaking voice assistant to ensure ease of use for elderly patients.

---

## 🌟 Key Features

### 👤 Senior Citizen View
- **Accessibility-First Dashboard:** Large fonts and high-contrast buttons designed for easy visibility.
- **Smart Medication Reminders:** Daily and date-specific schedule tracking. Senior citizens can mark doses as "Taken" directly from the UI.
- **Health Log Input:** Simple interface for recording Blood Pressure and Glucose levels.
- **AI Health Analysis:** Backend logic analyzes logs in real-time to alert if high blood pressure is detected.
- **Voice Assistant (Hindi):** Powered by **Sarvam AI** (with Google TTS fallback). The senior can ask "Aaj konsi goli khana hai?" in Hindi and the assistant will speak out their pending schedule.
- **Emergency SOS:** One-tap SOS button that retrieves precise GPS location and alerts the caretaker immediately.

### 👩‍⚕️ Caretaker Dashboard
- **Patient Analytics:** Monthly health report featuring **Chart.js** line graphs for BP trends and Glucose tracking.
- **Adherence Meter:** A premium circular progress gauge that visually tracking medication compliance percentages.
- **Remote Scheduling:** 
  - Add and delete medications (Daily or Date-specific).
  - Manage appointment calendars (Dr. visits, check-ups).
- **Detailed Logs:** Access to the full historical list of patient entries with AI-coded severity status.

---

## 🛠️ Technology Stack

### **Frontend**
- **UI:** HTML5, Semantic CSS.
- **Styling:** TailwindCSS (Accessibility-themed).
- **Charts:** Chart.js (Interactive data visualization).
- **Logic:** Vanilla JavaScript.
- **APIs:** Browser Web Speech API (for Hindi speech recognition).

### **Backend**
- **Language:** Python 3.9+.
- **Framework:** Flask & Flask-CORS.
- **Services:** 
  - **Sarvam AI SDK:** For high-quality Hindi Text-to-Speech.
  - **Google TTS Fallback:** Ensures voice reliability even without active API keys.
- **Environment Management:** `python-dotenv`.

---

## 🚀 Getting Started

### 1. Installation
Clone the repository and install dependencies:

```bash
cd saharacare
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration
Create or update the `.env` file in the root directory:

```env
SARVAM_API_KEY=your_sarvam_api_key_here
```

### 3. Running the Server
Start the Flask backend:

```bash
# Ensure port 5001 is available (MacOS AirPlay fix)
python backend/app.py
```

### 4. Access the Application
Open your browser and navigate to:
- **Senior View:** [http://localhost:5001/dashboard.html](http://localhost:5001/dashboard.html)
- **Caretaker View:** [http://localhost:5001/caretaker.html](http://localhost:5001/caretaker.html)

---

## 📂 Project Structure

```text
├── backend/
│   ├── app.py             # Main Flask server & API routes
│   ├── voice_service.py   # Sarvam AI & Google TTS integration
│   ├── ai_health_model.py # BP analysis logic
│   └── reminder_engine.py # Dose calculation logic
├── frontend/
│   ├── dashboard.html     # Main Senior UI
│   ├── medications.html   # Medicine schedule page
│   ├── caretaker.html     # Analytics & Admin portal
│   └── js/                # Client-Side logic (Voice, SOS, etc)
├── requirements.txt       # Python dependencies
└── .env                   # API Keys (Keep private)
```

## 📜 License
*Designed with ❤️ for our elders.*
