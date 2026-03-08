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
        {"id": 1, "name": "Vitamin D", "time": "10:00 AM", "date": "", "taken": False},
        {"id": 2, "name": "Metformin", "time": "08:00 AM", "date": "", "taken": False}
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
    med_id = len(db['medications']) + 1
    new_med = {
        "id": med_id,
        "name": data.get('name'),
        "time": data.get('time'),
        "date": data.get('date', ''),
        "taken": False
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
    for m in db['medications']:
        if m['id'] == int(med_id):
            m['taken'] = True
            return jsonify({"message": "Medication marked as taken"}), 200
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

@app.route('/generate_report', methods=['GET'])
def generate_report():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(190, 10, txt="SaharaCare AI - Patient Health Report", ln=True, align='C')
    pdf.set_font("helvetica", '', 12)
    pdf.cell(190, 10, txt=f"Report Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.ln(10)

    # 1. Meds Section
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(0, 10, txt="1. Medication Overview", ln=True)
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(60, 10, border=1, txt="Medicine Name")
    pdf.cell(40, 10, border=1, txt="Schedule Time")
    pdf.cell(40, 10, border=1, txt="Date (if any)")
    pdf.cell(30, 10, border=1, txt="Status", ln=True)

    pdf.set_font("helvetica", '', 10)
    for m in db['medications']:
        pdf.cell(60, 10, border=1, txt=str(m['name']))
        pdf.cell(40, 10, border=1, txt=str(m['time']))
        pdf.cell(40, 10, border=1, txt=str(m.get('date','Daily')))
        pdf.cell(30, 10, border=1, txt="Taken" if m['taken'] else "Pending", ln=True)
    pdf.ln(10)

    # 2. Health Logs Section
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(0, 10, txt="2. Detailed Health Logs (BP & Glucose)", ln=True)
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(50, 10, border=1, txt="Date/Time")
    pdf.cell(40, 10, border=1, txt="BP (sys/dia)")
    pdf.cell(30, 10, border=1, txt="Glucose")
    pdf.cell(60, 10, border=1, txt="AI Analysis", ln=True)

    pdf.set_font("helvetica", '', 10)
    for log in db.get('health_logs', []):
        dt_str = log['date'][:16].replace('T', ' ')
        bp_str = f"{log['systolic']}/{log['diastolic']}"
        glu_str = str(log.get('glucose', '-')) + " mg/dL"
        analysis = analyze_health(log['systolic'], log['diastolic'], log.get('glucose', 0))

        pdf.cell(50, 10, border=1, txt=dt_str)
        pdf.cell(40, 10, border=1, txt=bp_str)
        pdf.cell(30, 10, border=1, txt=glu_str)
        pdf.cell(60, 10, border=1, txt=analysis, ln=True)

    # Return as response with correct headers using BytesIO
    from io import BytesIO
    pdf_bytes = pdf.output()
    # If the output is a string (rare for fpdf2 but possible in some config), encode it
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin1')
    
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=SaharaCare_Report.pdf'
    return response

@app.route('/voice_command', methods=['POST'])
def handle_voice_command():
    data = request.json
    text = data.get('text', '').lower()
    print(f"DEBUG: Received Voice Command: '{text}'")
    
    # Language forced to Hindi as per user request
    lang_code = 'hi-IN'
    is_hindi = True

    # Healthcare terms mapping (Keywords in both scripts for reliability)
    health_keywords = ['sehat', 'health', 'bp', 'sugar', 'सेहत', 'तबीयत', 'कैसी', 'report', 'condition']
    med_keywords = ['goli', 'dawai', 'दवा', 'गोली', 'medicine', 'tablet', 'pill', 'khani', 'khana', 'take', 'schedule', 'meds', 'which']

    # 1. Health Logic
    if any(k in text for k in health_keywords):
        if not db['health_logs']:
            reply = "आपका कोई स्वास्थ्य डेटा नहीं मिला है।"
        else:
            recent_log = db['health_logs'][-1]
            sys = recent_log['systolic']
            dia = recent_log['diastolic']
            analysis = analyze_health(sys, dia, recent_log.get('glucose', 0))
            
            if analysis == "High blood pressure detected":
                reply = f"आपका ब्लड प्रेशर अधिक है। यह {sys} बटा {dia} है। कृपया आराम करें।"
            else:
                reply = f"आपकी सेहत बिल्कुल ठीक है। आपका ब्लड प्रेशर {sys} बटा {dia} नॉर्मल है।"
    
    # 2. Medicine Logic
    elif any(k in text for k in med_keywords):
        today_str = datetime.datetime.now().strftime('%Y-%m-%d')
        un_taken = [m for m in db['medications'] if not m['taken'] and (m.get('date', '') == '' or m.get('date') == today_str)]
        
        if not un_taken:
            reply = "आज के लिए आपकी कोई दवाई बाकी नहीं है।"
        else:
            meds_str_hi = " और ".join([f"{m['name']} {m['time']}" for m in un_taken])
            reply = f"आपको ये दवाइयां खानी हैं: {meds_str_hi}।"
            
    # 3. Fallback
    else:
        reply = "मुझे आपका सवाल समझ नहीं आया। क्या आप दवाई या सेहत के बारे में पूछना चाहते हैं?"
        
    audio_data = generate_hindi_audio(reply, target_language=lang_code)
    return jsonify({"audio": audio_data, "text": reply}), 200

if __name__ == '__main__':
    # Use PORT from environment variable (default to 7860 for Hugging Face)
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port, debug=True)
