from flask import *
from pyzbar import *
from werkzeug.utils import secure_filename
import os
from flask import Blueprint
from .db import get_db
from .student import student
from werkzeug.local import LocalProxy

auth=Blueprint('auth',__name__)


db= LocalProxy(get_db)
ALLOWED_EXTENSIONS = {'jpg'}

@auth.route('/', methods=['GET', 'POST'])
def login():
    if session.get("login_type"):
        if (session["login_type"] == 'wrong'):
            return redirect('/wrong')
        if (session["login_type"] == "student"):
            return redirect(url_for('student.studentFunction'))
        if (session["login_type"] == "faculty"):
            return redirect(url_for('faculty.facultyFunction'))
        if (session["login_type"] == "security"):
            return redirect(url_for('security.securityFunction'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_type = request.form['login_type']
        session["username"] = request.form['username']
        session["login_type"] = request.form['login_type']

        user_data = None
        if login_type == 'student':
            user_data = db.studentdata.find_one({'username': username, 'password': password})
            user = db.students.find_one({'username': username})
            if user_data:
                session['name'] = user.get('name', '')
                fac=db.students.find_one({'username': session['username']})
                session['mentor'] = fac.get("faculty")
        elif login_type == 'faculty':
            user_data = db.facultydata.find_one({'username': username, 'password': password})
        elif login_type == 'security':
            user_data = db.securitydata.find_one({'username': username, 'password': password})

        if user_data:
            session['login_type'] = login_type
            if login_type == 'student':
                return redirect(url_for('student.studentFunction'))
            elif login_type == 'faculty':
                return redirect(url_for('faculty.facultyFunction'))
            elif login_type == 'security':
                return redirect(url_for('security.securityFunction'))
        else:
            session["username"] = None
            session["name"] = None
            session["login_type"] = 'wrong'
            return redirect("/")

    return render_template('index.html')

@auth.route("/logout")
def logout():
    session["login_type"] = None
    session["username"] = None
    session["name"] = None
    
    return redirect("/")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_type = request.form['login_type']
        photo = request.files['photo']

        # Check if the photo has been uploaded
        if photo.filename == '':
            return "No selected file"
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            # Rename the file to the username before saving
            filename = secure_filename(username) + os.path.splitext(filename)[1]
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            return "Unsupported file format. Please upload an image."

        existing_user = None
        if login_type == 'student':
            existing_user = db.studentdata.find_one({'username': username})
        elif login_type == 'faculty':
            existing_user = db.facultydata.find_one({'username': username})
        elif login_type == 'security':
            existing_user = db.securitydata.find_one({'username': username})
        if existing_user:
            return "Username already exists. Please choose a different username."
        if login_type == 'student':
            db.studentdata.insert_one({'username': username, 'password': password, 'photo': filename})
        elif login_type == 'faculty':
            db.facultydata.insert_one({'username': username, 'password': password, 'photo': filename})
        elif login_type == 'security':
            db.securitydata.insert_one({'username': username, 'password': password, 'photo': filename})
        return "Registration successful. You can now log in."

    return render_template('register.html')

@auth.route('/change', methods=['GET', 'POST'])
def change():
    if 'login_type' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        username = session['username']
        current_password = request.form['current_password']
        new_password = request.form['new_password']

        if session["login_type"] == 'student':
            user = db.studentdata.find_one({'username': username, 'password': current_password})
        elif session["login_type"] == 'security':
            user = db.securitydata.find_one({'username': username, 'password': current_password})
        elif session["login_type"] == 'faculty':
            user = db.facultydata.find_one({'username': username, 'password': current_password})
        else:
            return "Invalid login type."

        if user:
            if session["login_type"] == 'student':
                db.studentdata.update_one({'_id': user['_id']}, {'$set': {'password': new_password}})
            elif session["login_type"] == 'security':
                db.securitydata.update_one({'_id': user['_id']}, {'$set': {'password': new_password}})
            elif session["login_type"] == 'faculty':
                db.facultydata.update_one({'_id': user['_id']}, {'$set': {'password': new_password}})
            return redirect("/logout")
        else:
            return "Incorrect username or password. Please try again."
    return render_template('change.html')



@auth.route('/wrong')
def wrong():
    session["login_type"] = 'wrongggg'
    return render_template('wrong.html')