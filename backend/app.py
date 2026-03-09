import os
import sys

# Ultimate fix for imports on cloud servers
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from flask import Flask, request, jsonify, send_from_directory, make_response
from fpdf import FPDF
import io
from langdetect import detect
from flask_cors import CORS
from dotenv import load_dotenv
import datetime
from reminder_engine import get_next_reminder
from ai_health_model import analyze_health
from voice_service import generate_hindi_audio

load_dotenv()

# Serve static files from the 'frontend' directory
frontend_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
app = Flask(__name__, static_folder=frontend_folder, static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'dashboard.html')

@app.route('/<path:path>')
def serve_html(path):
    # If the user asks for 'something.html' and it exists in frontend, serve it
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    # Default to returning the file (it will 404 if it doesn't exist)
    return send_from_directory(app.static_folder, path)


# In-memory database
db = {
    "users": {},
    "medications": [
        {"id": 1, "name": "Vitamin D", "time": "10:00 AM", "date": "", "last_taken_date": None},
        {"id": 2, "name": "Metformin", "time": "08:00 AM", "date": "", "last_taken_date": None}
    ],
    "appointments": [
        {"id": 1, "title": "Dr. Smith", "date": "Tomorrow", "time": "2 PM"}
    ],
    "health_logs": [],
    "sos_logs": []
}

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not email:
        return jsonify({"message": "Email is required"}), 400
    if email in db['users']:
        return jsonify({"message": "User already exists"}), 400
    db['users'][email] = password
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/add_medication', methods=['POST'])
def add_medication():
    data = request.json
    # Better ID generation to avoid duplicates after deletions
    existing_ids = [m['id'] for m in db['medications']]
    med_id = (max(existing_ids) + 1) if existing_ids else 1
    
    new_med = {
        "id": med_id,
        "name": data.get('name'),
        "time": data.get('time'),
        "date": data.get('date', ''), # Empty means daily
        "last_taken_date": None # Store the YYYY-MM-DD when it was last taken
    }
    db['medications'].append(new_med)
    return jsonify({"message": "Medication added successfully", "medication": new_med}), 201

@app.route('/medications', methods=['GET'])
def get_medications():
    return jsonify({"medications": db['medications']}), 200

@app.route('/delete_medication/<int:med_id>', methods=['DELETE'])
def delete_medication(med_id):
    db['medications'] = [m for m in db['medications'] if m['id'] != med_id]
    return jsonify({"message": "Medication deleted"}), 200

@app.route('/appointments', methods=['GET'])
def get_appointments():
    return jsonify({"appointments": db['appointments']}), 200

@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    data = request.json
    appt_id = len(db['appointments']) + 1
    new_appt = {
        "id": appt_id,
        "title": data.get('title'),
        "date": data.get('date'),
        "time": data.get('time')
    }
    db['appointments'].append(new_appt)
    return jsonify({"message": "Appointment added", "appointment": new_appt}), 201

@app.route('/delete_appointment/<int:appt_id>', methods=['DELETE'])
def delete_appointment(appt_id):
    db['appointments'] = [a for a in db['appointments'] if a['id'] != appt_id]
    return jsonify({"message": "Appointment deleted"}), 200

@app.route('/take_medication', methods=['POST'])
def take_medication():
    data = request.json
    med_id = data.get('id')
    print(f"DEBUG: Processing mark as taken for ID: {med_id}")

    for m in db['medications']:
        if int(m['id']) == int(med_id):
            # Set date it was taken (reset daily)
            m['last_taken_date'] = datetime.datetime.now().strftime('%Y-%m-%d')
            return jsonify({"message": "Medication marked as taken", "status": "taken"}), 200
            
    return jsonify({"message": "Medication not found"}), 404

@app.route('/health_log', methods=['POST'])
def save_health_log():
    data = request.json
    systolic = int(data.get('systolic', 0))
    diastolic = int(data.get('diastolic', 0))
    glucose = int(data.get('glucose', 0))
    
    log_entry = {
        "id": len(db['health_logs']) + 1,
        "systolic": systolic,
        "diastolic": diastolic,
        "glucose": glucose,
        "date": datetime.datetime.now().isoformat()
    }
    db['health_logs'].append(log_entry)
    
    # Analyze BP
    analysis_result = analyze_health(systolic, diastolic, glucose)
    return jsonify({
        "message": "Health log saved", 
        "analysis": analysis_result,
        "log": log_entry
    }), 201

@app.route('/health_logs', methods=['GET'])
def get_health_logs():
    return jsonify({"logs": db['health_logs']}), 200

@app.route('/sos', methods=['POST'])
def sos_alert():
    data = request.json
    lat = data.get('latitude')
    lng = data.get('longitude')
    
    sos_entry = {
        "id": len(db['sos_logs']) + 1,
        "latitude": lat,
        "longitude": lng,
        "timestamp": datetime.datetime.now().isoformat()
    }
    db['sos_logs'].append(sos_entry)
    return jsonify({"message": "Emergency SOS triggered and logged"}), 200

def safe_str(text):
    """Sanitize strings for PDF (removes non-Latin-1 characters like Hindi to prevent crashes)"""
    if not text:
        return ""
    # Convert to string and encode/decode to strip unsupported characters
    return str(text).encode('latin-1', 'replace').decode('latin-1')

@app.route('/generate_report', methods=['GET'])
def generate_report():
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(190, 10, text="SaharaCare - Monthly Health Report", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_font("helvetica", '', 12)
    pdf.cell(190, 10, text=f"Report Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)

    # 1. Meds Section
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(0, 10, text="1. Medication Overview", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(60, 10, border=1, text="Medicine Name")
    pdf.cell(40, 10, border=1, text="Schedule Time")
    pdf.cell(40, 10, border=1, text="Date (if any)")
    pdf.cell(30, 10, border=1, text="Status", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("helvetica", '', 10)
    for m in db['medications']:
        # Sanitize all dynamic inputs
        name = safe_str(m['name'])
        time = safe_str(m['time'])
        date = safe_str(m.get('date','Daily'))
        today_str = datetime.datetime.now().strftime('%Y-%m-%d')
        status = "Taken" if m.get('last_taken_date') == today_str else "Pending"
        
        pdf.cell(60, 10, border=1, text=name)
        pdf.cell(40, 10, border=1, text=time)
        pdf.cell(40, 10, border=1, text=date)
        pdf.cell(30, 10, border=1, text=status, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    # 2. Health Logs Section
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(0, 10, text="2. Detailed Health Logs (BP & Glucose)", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(50, 10, border=1, text="Date/Time")
    pdf.cell(40, 10, border=1, text="BP (sys/dia)")
    pdf.cell(30, 10, border=1, text="Glucose")
    pdf.cell(60, 10, border=1, text="AI Analysis", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("helvetica", '', 10)
    for log in db.get('health_logs', []):
        # Sanitize all dynamic inputs
        dt_str = safe_str(log['date'][:16].replace('T', ' '))
        bp_str = safe_str(f"{log['systolic']}/{log['diastolic']}")
        glu_str = safe_str(str(log.get('glucose', '-')) + " mg/dL")
        analysis_raw = analyze_health(log['systolic'], log['diastolic'], log.get('glucose', 0))
        analysis = safe_str(analysis_raw)

        pdf.cell(50, 10, border=1, text=dt_str)
        pdf.cell(40, 10, border=1, text=bp_str)
        pdf.cell(30, 10, border=1, text=glu_str)
        pdf.cell(60, 10, border=1, text=analysis, new_x="LMARGIN", new_y="NEXT")

    # Return as response with correct headers using BytesIO
    from io import BytesIO
    try:
        # Ensure output is converted to bytes (fpdf2 returns bytearray)
        pdf_bytes = bytes(pdf.output())
    except Exception as e:
        print(f"PDF Generation Error: {e}")
        return jsonify({"message": "Error generating PDF. Please ensure data doesn't contain unsupported characters."}), 500
    
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=SaharaCare_Report.pdf'
    return response

@app.route('/voice_command', methods=['POST'])
def handle_voice_command():
    data = request.json
    text = data.get('text', '').lower()
    print(f"DEBUG: Received Voice Command: '{text}'")
    
    lang_code = 'hi-IN'
    is_hindi = True

    health_keywords = ['sehat', 'health', 'bp', 'sugar', 'सेहत', 'तबीयत', 'कैसी', 'report', 'condition']
    med_keywords = ['goli', 'dawai', 'दवा', 'गोली', 'medicine', 'tablet', 'pill', 'khani', 'khana', 'take', 'schedule', 'meds', 'which']
    appt_keywords = ['doctor', 'appointment', 'visit', 'checkup', 'मिलना', 'अपॉइंटमेंट', 'डॉक्टर', 'dikha', 'milna']

    redirect_url = None

    # 1. Health Logic
    if any(k in text for k in health_keywords):
        if not db['health_logs']:
            reply = "आपका कोई स्वास्थ्य डेटा नहीं मिला है।"
        else:
            recent_log = db['health_logs'][-1]
            sys = recent_log['systolic']
            dia = recent_log['diastolic']
            glu = recent_log.get('glucose', 0)
            analysis = analyze_health(sys, dia, glu)
            
            # Map analysis to Hindi and handle all cases
            bp_mention = f"आपका ब्लड प्रेशर {sys} बटा {dia} है।"
            glu_mention = f" और शुगर लेवल {glu} है।" if glu > 0 else ""
            
            if "Stage 2" in analysis:
                reply = f"सावधान! {bp_mention} यह काफी ज्यादा है (स्टेज 2)। तुरंत डॉक्टर से संपर्क करें।"
            elif "Stage 1" in analysis:
                reply = f"{bp_mention} यह बढ़ा हुआ है (स्टेज 1)। कृपया अपना ख्याल रखें।"
            elif "Pre Hypertension" in analysis:
                reply = f"{bp_mention} यह सामान्य से थोड़ा ज्यादा है। सावधान रहें।"
            elif "Low blood pressure" in analysis:
                reply = f"{bp_mention} यह सामान्य से कम है। कृपया आराम करें।"
            elif "Very high" in analysis:
                 reply = f"सावधान! आपका शुगर लेवल काफी बढ़ा हुआ है ({glu})।"
            elif "Elevated" in analysis:
                 reply = f"आपका शुगर लेवल थोड़ा बढ़ा हुआ है ({glu})।"
            elif "Low sugar" in analysis:
                 reply = f"आपका शुगर लेवल कम है ({glu})। कुछ मीठा लें।"
            else:
                reply = f"आपकी सेहत बिल्कुल ठीक है। {bp_mention}{glu_mention} यह नॉर्मल है।"
    
    # 2. Medicine Logic
    elif any(k in text for k in med_keywords):
        today_str = datetime.datetime.now().strftime('%Y-%m-%d')
        un_taken = [m for m in db['medications'] if m.get('last_taken_date') != today_str and (m.get('date', '') == '' or m.get('date') == today_str)]
        
        if not un_taken:
            reply = "आज के लिए आपकी कोई दवाई बाकी नहीं है।"
        else:
            meds_str_hi = " और ".join([f"{m['name']} {m['time']}" for m in un_taken])
            reply = f"आपको ये दवाइयां खानी हैं: {meds_str_hi}।"

    # 3. Appointment Logic
    elif any(k in text for k in appt_keywords):
        reply = "यहाँ आपके अपॉइंटमेंट्स हैं।"
        redirect_url = "appointments.html"
            
    # 4. Fallback
    else:
        reply = "मुझे आपका सवाल समझ नहीं आया। क्या आप दवाई, सेहत या अपॉइंटमेंट्स के बारे में पूछना चाहते हैं?"
        
    audio_data = generate_hindi_audio(reply, target_language=lang_code)
    return jsonify({"audio": audio_data, "text": reply, "redirect": redirect_url}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port, debug=True)
