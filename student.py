import base64
from datetime import datetime
from io import BytesIO
from mailbox import Message
from flask import *
from matplotlib import pyplot as plt
from pyzbar import *
import spacy
from werkzeug.utils import secure_filename
import os
from flask import Blueprint
from .db import get_db
from werkzeug.local import LocalProxy

db= LocalProxy(get_db)

student=Blueprint('student',__name__)

@student.route('/photos/<path:filename>')
def photos(filename):
    if filename=="20EG112331.jpg":
        return send_from_directory('photos', filename)
    else:
        filename="person.jpg"
        return send_from_directory('photos', 'person.jpg')
    

@student.route('/view_requests', methods=['GET', 'POST'])
def view_requests():
    
        student_id = session['username']
        requests = list(db.requests.find({'student_id': student_id}))
        current_date = datetime.now().date().strftime('%d-%m-%Y')
        
        approved_requests = [req for req in requests if req['status'] == 'Approved' and req['datetime'] == current_date]

        return render_template('view_requests.html', student_id=student_id, requests=requests, approved_requests=approved_requests)

@student.route('/stats2', methods=['GET', 'POST'])
def stats2():
    plot_url2 = None
    requests_data = db.requests.find({'student_id': session["username"]})
    date_counts = {}
    for request_ in requests_data:
            date = request_['datetime'][0:2] + '-' + request_['datetime'][3:5]  # Convert date to string format
            date_counts[date] = date_counts.get(date, 0) + 1

    dates = list(date_counts.keys())
    counts = list(date_counts.values())

    plt.bar(dates, counts, color='orange')
    plt.xlabel('Date')
    plt.title('Requests Received by Date: ')
    plt.xticks(rotation=45)

    for i in range(len(dates)):
            plt.text(i, counts[i], str(counts[i]), ha='center', va='bottom')

    plt.yticks([])
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url2 = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return render_template('stats2.html', plot_url2=plot_url2)

@student.route('/student', methods=['GET', 'POST'])
def studentFunction():
    if 'login_type' not in session or session['login_type'] != 'student':
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        student_id = session['username']
        name = session['name']
        reason = request.form['reason']
        priority = prioritize_text(reason)
        current_date = datetime.now().date().strftime('%d-%m-%Y')
        fac=db.students.find_one({'username': session['username']})
        facc=fac.get("faculty")
        checkk="False"
        db.requests.insert_one({'student_id': student_id, 'name': name, 'reason': reason, 'status': 'Pending', 'datetime': current_date, 'priority': priority, 'faculty': facc, 'checkedout': checkk, 'checkouttime': "Null"})
        subject = "New GatePass Request"
        sender = "poppingaming1@gmail.com"
        recipients = ["pingalipraneeth1@gmail.com"]
        body = f"New Gatepass request from '{name}' '{student_id}'."
        # send_email(subject, sender, recipients, body)
        return redirect(url_for('student.studentFunction'))

    return render_template('student.html')


nlp = spacy.load("en_core_web_sm")
def prioritize_text(text):
    doc = nlp(text.lower())  
    
    priority_keywords = {
        "urgent": 3,
        "health": 2,
        "emergency": 3,
        "family emergency": 2,
        "personal reasons": 1,
        "vacation": 1,
        "wedding": 1,
        "birth of a child": 1,
        "fever": 2,
        "headache": 2,
        "stomach pain": 2,
        "educational purposes": 1,
        "unplanned event": 1,
        "death": 3,
        "injury": 3,
        "exam": 3,
        "education": 3,    
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

# from .mail import get_mail
# mail=get_mail()
# def send_email(subject, sender, recipients, body):
#     msg = Message(subject, sender=sender, recipients=recipients)
#     msg.body = body
#     mail.send(msg)