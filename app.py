from flask import *
from flask_pymongo import PyMongo
import random
from bson import ObjectId
import qrcode
from io import BytesIO

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb+srv://pingalipraneeth1:DgCwSk9Cn9mTx32a@augatepass.1dvhlzv.mongodb.net/gatepass_db?retryWrites=true&w=majority'
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random, secure value
mongo = PyMongo(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_type = request.form['login_type']

        user_data = None
        if login_type == 'student':
            user_data = mongo.db.studentdata.find_one({'username': username, 'password': password})
        elif login_type == 'faculty':
            user_data = mongo.db.facultydata.find_one({'username': username, 'password': password})

        if user_data:
            session['login_type'] = login_type
            if login_type == 'student':
                return redirect(url_for('student'))
            elif login_type == 'faculty':
                return redirect(url_for('faculty'))
            elif login_type == 'view_requests':
                return redirect(url_for('view_requests'))

    return render_template('login.html')

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
        if existing_user:
            return "Username already exists. Please choose a different username."
        if login_type == 'student':
            mongo.db.studentdata.insert_one({'username': username, 'password': password})
        elif login_type == 'faculty':
            mongo.db.facultydata.insert_one({'username': username, 'password': password})
        return "Registration successful. You can now log in."

    return render_template('register.html')

@app.route('/student', methods=['GET', 'POST'])
def student():
    if 'login_type' not in session or session['login_type'] != 'student':
        return redirect(url_for('login'))

    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        reason = request.form['reason']
        mongo.db.requests.insert_one({'student_id': student_id, 'name': name, 'reason': reason, 'status': 'Pending'})
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

    requests = mongo.db.requests.find({'status': 'Pending'})
    return render_template('faculty.html', requests=requests)

@app.route('/view_requests', methods=['GET', 'POST'])
def view_requests():
    if request.method == 'POST':
        student_id = request.form['student_id']
        requests = list(mongo.db.requests.find({'student_id': student_id}))
        
        approved_requests = [req for req in requests if req['status'] == 'Approved']

        return render_template('view_requests.html', student_id=student_id, requests=requests, approved_requests=approved_requests)

    return render_template('view_requests_form.html')

@app.route('/generate_qr/<key>')
def generate_qr(key):
    qr_url = f"http://augatepass.onrender.com/verifyqr/{key}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the image to a BytesIO object
    img_io = BytesIO()
    img.save(img_io)
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

@app.route('/verifyqr/<key>')
def verify_qr(key):
    request_data = mongo.db.requests.find_one({'key': key, 'status': 'Approved'})
    
    if request_data:
        return render_template('verify_qr.html', student_id=request_data['student_id'], name=request_data['name'], reason=request_data['reason'])
    else:
        return render_template('verify_qr_error.html', message='Invalid QR code or request not approved')

if __name__ == '__main__':
    app.run(debug=True)
