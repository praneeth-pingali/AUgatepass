import base64
from datetime import datetime
from io import BytesIO
import random
from bson import ObjectId
from flask import *
from matplotlib import pyplot as plt
from pyzbar import *
import qrcode
from werkzeug.utils import secure_filename
import os
from flask import Blueprint

# from app import send_email
from .db import get_db
from werkzeug.local import LocalProxy

db= LocalProxy(get_db)

security=Blueprint('security',__name__)

@security.route('/security', methods=['GET', 'POST'])
def securityFunction():
    if 'login_type' not in session or session['login_type'] != 'security':
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        if request.form['action'] == 'entry':

            name = request.form['name']
            reason = request.form['reason']
            number = request.form['number']
            current_datetime = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            db.visitors.insert_one({'name': name, 'reason': reason, 'number': number, 'datetime': current_datetime, 'checkout': False})

            return redirect(url_for('security.securityFunction'))

    return render_template('security.html')

@security.route('/security/visitors_log')
def visitors_log():
    if 'login_type' not in session or session['login_type'] not in ['student', 'faculty', 'security']:
        return redirect(url_for('auth.login'))
    visitors = db.visitors.find()

    return render_template('visitors_log.html', visitors=visitors)

@security.route('/security/checkout/<visitor_id>', methods=['POST'])
def checkout_visitor(visitor_id):
    checkout_time = datetime.now()
    db.visitors.update_one(
        {'_id': ObjectId(visitor_id)},
        {'$set': {'checkout': True, 'checkout_time': checkout_time}}
    )
    return redirect(url_for('security.visitors_log'))  

@security.route('/generate_qr/<key>')
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

@security.route('/verifyqr/<key>')
def verify_qr(key):
    current_date = datetime.now().date().strftime('%d-%m-%Y')
    request_data = db.requests.find_one({'key': key, 'status': 'Approved', 'checkedout': 'False', 'datetime': current_date})
    
    if request_data:
        return render_template('verify_qr.html', key=request_data['key'],student_id=request_data['student_id'], name=request_data['name'], reason=request_data['reason'], datetime=request_data['datetime'])
    else:
        return render_template('verify_qr_error.html', message='Invalid QR code, used , expired or request not approved')
    

@security.route('/checkout/<key>')
def checkout(key):
    current_time = datetime.now().strftime('%H:%M:%S')
    request_data = db.requests.find_one({'key': key})
    db.requests.update_one({'key': key}, {'$set': {'checkedout': 'True'}})
    db.requests.update_one({'key': key}, {'$set': {'checkouttime': current_time}})
    Name=request_data['name']
    id=request_data['student_id']
    subject = "Your Ward Checked Out"
    sender = "poppingaming1@gmail.com"
    recipients = ["pingalipraneeth1@gmail.com"]
    body = f"Your Ward '{Name}' '{id}' has checked out University at {current_time}."
    # send_email(subject, sender, recipients, body)
    return redirect('/cam')


@security.route('/cam')
def index():
    return render_template('cam.html')