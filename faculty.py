import base64
from datetime import datetime
from io import BytesIO
import random
from bson import ObjectId
from flask import *
from matplotlib import pyplot as plt
from pyzbar import *
import spacy
from werkzeug.utils import secure_filename
import os
from flask import Blueprint
from werkzeug.local import LocalProxy
from .db import get_db

db= LocalProxy(get_db)

faculty=Blueprint('faculty',__name__)


@faculty.route('/faculty', methods=['GET', 'POST'])
def facultyFunction():
    if 'login_type' not in session or session['login_type'] != 'faculty':
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        request_id = request.form['request_id']
        action = request.form['action']

        if action == 'allow':
            random_key = str(random.randint(100000, 999999))
            db.requests.update_one({'_id': ObjectId(request_id)}, {'$set': {'status': 'Approved', 'key': random_key}})
        
        elif action == 'deny':
            db.requests.update_one({'_id': ObjectId(request_id)}, {'$set': {'status': 'Denied', 'key': None}})
        
        return redirect(url_for('faculty.facultyFunction'))
    

    requests = db.requests.find({'status': 'Pending', 'faculty': session['username']})

    return render_template('faculty.html', requests=requests)

@faculty.route('/stats', methods=['GET', 'POST'])
def stats():
    plot_url1 = None
    plot_url2 = None
    if request.method == 'POST':
        student_id = request.form['student_id']

        # Plot 1: Requests received by date
        requests_data = db.requests.find({'faculty': session.get('username')})
        date_counts = {}
        for request_ in requests_data:
            date = request_['datetime'][0:2] + '-' + request_['datetime'][3:5]  # Convert date to string format
            current_month = datetime.now().month
            if int(request_['datetime'][3:5]) == current_month:
                date_counts[date] = date_counts.get(date, 0) + 1

        dates = list(date_counts.keys())
        counts = list(date_counts.values())

        plt.bar(dates, counts)
        plt.xlabel('Date')
        plt.title('Requests Received by Date')
        plt.xticks(rotation=45)

        for i in range(len(dates)):
            plt.text(i, counts[i], str(counts[i]), ha='center', va='bottom')

        plt.yticks([])
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url1 = base64.b64encode(img.getvalue()).decode()
        plt.close()

        # Plot 2: Requests made by specific student ID
        requests_data = db.requests.find({'student_id': student_id})
        date_counts = {}
        for request_ in requests_data:
            date = request_['datetime'][0:2] + '-' + request_['datetime'][3:5]  # Convert date to string format
            date_counts[date] = date_counts.get(date, 0) + 1

        dates = list(date_counts.keys())
        counts = list(date_counts.values())

        plt.bar(dates, counts, color='orange')
        plt.xlabel('Date')
        plt.title('Requests Received by Date for Student ID: {}'.format(student_id))
        plt.xticks(rotation=45)

        for i in range(len(dates)):
            plt.text(i, counts[i], str(counts[i]), ha='center', va='bottom')

        plt.yticks([])
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url2 = base64.b64encode(img.getvalue()).decode()
        plt.close()

    return render_template('stats.html', plot_url1=plot_url1, plot_url2=plot_url2)

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


