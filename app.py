from flask import *
from flask_pymongo import PyMongo
from flask_session import Session
import random
from bson import ObjectId
import qrcode
from io import BytesIO
from datetime import datetime
from pyzbar import *
import numpy as np
from pyzbar import pyzbar
from flask_socketio import SocketIO
import spacy

app = Flask(__name__)
socketio = SocketIO(app)

app.config['MONGO_URI'] = 'mongodb+srv://pingalipraneeth1:DgCwSk9Cn9mTx32a@augatepass.1dvhlzv.mongodb.net/gatepass_db?retryWrites=true&w=majority'
app.config['SECRET_KEY'] = 'your_secret_key'  
mongo = PyMongo(app)
nlp = spacy.load("en_core_web_sm")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def prioritize_text(text):
    doc = nlp(text.lower())  
    
    priority_keywords = {
        "urgent": 2,
        "health issue": 2,
        "family emergency": 2,
        "personal reasons": 1,
        "vacation": 1,
        "wedding": 1,
        "birth of a child": 1,
        "bereavement": 2,
        "educational purposes": 1,
        "unplanned event": 1,
    }

    priority_labels = {
    3: "high",
    2: "medium",
    1: "low",
    }

    priority = 1  

    for keyword, weight in priority_keywords.items():
        if keyword in doc.text:
            priority = max(priority, weight)

    return priority_labels[priority]


@app.route('/', methods=['GET', 'POST'])
def login():
    if session.get("login_type"):
        if (session["login_type"] == "student"):
            return redirect(url_for('student'))
        if (session["login_type"] == "faculty"):
            return redirect(url_for('faculty'))
        if (session["login_type"] == "security"):
            return redirect(url_for('security'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_type = request.form['login_type']
        session["username"] = request.form['username']
        session["login_type"] = request.form['login_type']

        user_data = None
        if login_type == 'student':
            user_data = mongo.db.studentdata.find_one({'username': username, 'password': password})
            user = mongo.db.students.find_one({'username': username})
            session['name'] = user.get('name', '')
        elif login_type == 'faculty':
            user_data = mongo.db.facultydata.find_one({'username': username, 'password': password})
        elif login_type == 'security':
            user_data = mongo.db.securitydata.find_one({'username': username, 'password': password})

        if user_data:
            session['login_type'] = login_type
            if login_type == 'student':
                return redirect(url_for('student'))
            elif login_type == 'faculty':
                return redirect(url_for('faculty'))
            elif login_type == 'security':
                return redirect(url_for('security'))
            elif login_type == 'view_requests':
                return redirect(url_for('view_requests'))

    return render_template('login.html')

@app.route("/logout")
def logout():
    session["login_type"] = None
    return redirect("/")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_type = request.form['login_type']

        existing_user = None
        if login_type == 'student':
            existing_user = mongo.db.studentdata.find_one({'username': username})
        elif login_type == 'faculty':
            existing_user = mongo.db.facultydata.find_one({'username': username})
        elif login_type == 'security':
            existing_user = mongo.db.securitydata.find_one({'username': username})
        if existing_user:
            return "Username already exists. Please choose a different username."
        if login_type == 'student':
            mongo.db.studentdata.insert_one({'username': username, 'password': password})
        elif login_type == 'faculty':
            mongo.db.facultydata.insert_one({'username': username, 'password': password})
        elif login_type == 'security':
            mongo.db.securitydata.insert_one({'username': username, 'password': password})
        return "Registration successful. You can now log in."

    return render_template('register.html')

@app.route('/student', methods=['GET', 'POST'])
def student():
    if 'login_type' not in session or session['login_type'] != 'student':
        return redirect(url_for('login'))

    if request.method == 'POST':
        student_id = session['username']
        name = session['name']
        reason = request.form['reason']
        priority = prioritize_text(reason)
        current_date = datetime.now().date().strftime('%d-%m-%Y')
        fac=mongo.db.students.find_one({'username': session['username']})
        facc=fac.get("faculty")
        mongo.db.requests.insert_one({'student_id': student_id, 'name': name, 'reason': reason, 'status': 'Pending', 'datetime': current_date, 'priority': priority, 'faculty': facc})
        return redirect(url_for('student'))

    return render_template('student.html')

@app.route('/faculty', methods=['GET', 'POST'])
def faculty():
    if 'login_type' not in session or session['login_type'] != 'faculty':
        return redirect(url_for('login'))

    if request.method == 'POST':
        request_id = request.form['request_id']
        action = request.form['action']

        if action == 'allow':
            random_key = str(random.randint(100000, 999999))
            mongo.db.requests.update_one({'_id': ObjectId(request_id)}, {'$set': {'status': 'Approved', 'key': random_key}})
        
        elif action == 'deny':
            mongo.db.requests.update_one({'_id': ObjectId(request_id)}, {'$set': {'status': 'Denied', 'key': None}})
        
        return redirect(url_for('faculty'))
    

    requests = mongo.db.requests.find({'status': 'Pending', 'faculty': session['username']})

    return render_template('faculty.html', requests=requests)

@app.route('/security', methods=['GET', 'POST'])
def security():
    if 'login_type' not in session or session['login_type'] not in ['student', 'faculty', 'security']:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if request.form['action'] == 'entry':

            name = request.form['name']
            reason = request.form['reason']
            number = request.form['number']
            current_datetime = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            mongo.db.visitors.insert_one({'name': name, 'reason': reason, 'number': number, 'datetime': current_datetime})

            return redirect(url_for('security'))

    return render_template('security.html')

@app.route('/security/visitors_log')
def visitors_log():
    if 'login_type' not in session or session['login_type'] not in ['student', 'faculty', 'security']:
        return redirect(url_for('login'))
    visitors = mongo.db.visitors.find()

    return render_template('visitors_log.html', visitors=visitors)

@app.route('/view_requests', methods=['GET', 'POST'])
def view_requests():
    
        student_id = session['username']
        requests = list(mongo.db.requests.find({'student_id': student_id}))
        
        approved_requests = [req for req in requests if req['status'] == 'Approved']

        return render_template('view_requests.html', student_id=student_id, requests=requests, approved_requests=approved_requests)  

@app.route('/generate_qr/<key>')
def generate_qr(key):
    qr_url = f"https://augatepass.onrender.com/verifyqr/{key}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    img_io = BytesIO()
    img.save(img_io)
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

@app.route('/verifyqr/<key>')
def verify_qr(key):
    request_data = mongo.db.requests.find_one({'key': key, 'status': 'Approved'})
    
    if request_data:
        return render_template('verify_qr.html', student_id=request_data['student_id'], name=request_data['name'], reason=request_data['reason'], datetime=request_data['datetime'])
    else:
        return render_template('verify_qr_error.html', message='Invalid QR code or request not approved')
    
@app.route('/change', methods=['GET', 'POST'])
def change():
    if 'login_type' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = session['username']
        current_password = request.form['current_password']
        new_password = request.form['new_password']

        if session["login_type"] == 'student':
            user = mongo.db.studentdata.find_one({'username': username, 'password': current_password})
        elif session["login_type"] == 'security':
            user = mongo.db.securitydata.find_one({'username': username, 'password': current_password})
        elif session["login_type"] == 'faculty':
            user = mongo.db.facultydata.find_one({'username': username, 'password': current_password})
        else:
            return "Invalid login type."

        if user:
            if session["login_type"] == 'student':
                mongo.db.studentdata.update_one({'_id': user['_id']}, {'$set': {'password': new_password}})
            elif session["login_type"] == 'security':
                mongo.db.securitydata.update_one({'_id': user['_id']}, {'$set': {'password': new_password}})
            elif session["login_type"] == 'faculty':
                mongo.db.facultydata.update_one({'_id': user['_id']}, {'$set': {'password': new_password}})
            return "Password updated successfully!"
        else:
            return "Incorrect username or password. Please try again."
    return render_template('change.html')


    

@app.route('/cam')
def index():
    return render_template('cam.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('qr_scanned')
def handle_qr_scanned(data):
    print('QR Code Scanned:', data['data'])


if __name__ == '__main__':
    socketio.run(app, debug=True,allow_unsafe_werkzeug=True)
