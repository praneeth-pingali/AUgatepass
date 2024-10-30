from flask import *
from flask_pymongo import PyMongo
from flask_session import Session
import random
from bson import ObjectId
import qrcode
from io import BytesIO
from datetime import datetime
from pyzbar import *
from flask_socketio import SocketIO
import spacy
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from werkzeug.utils import secure_filename
import os
from flask_mail import Mail, Message
import time
from .db import get_db
from . import create_app
from .mail import get_mail
from .socketIo import get_socketio
# app = Flask(__name__)
# socketio = SocketIO(app)
# UPLOAD_FOLDER = 'photos'
# ALLOWED_EXTENSIONS = {'jpg'}

# app.config['MONGO_URI'] = 'mongodb+srv://pingalipraneeth1:DgCwSk9Cn9mTx32a@augatepass.1dvhlzv.mongodb.net/gatepass_db?retryWrites=true&w=majority'
# app.config['SECRET_KEY'] = 'your_secret_key'  
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# mongo = PyMongo(app)
# nlp = spacy.load("en_core_web_sm")

# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = 'poppingaming1@gmail.com'
# app.config['MAIL_PASSWORD'] = 'atjj cynj vkwt ljkn'

# mail = Mail(app)
db = get_db()
mail = get_mail()
socketio = get_socketio()

@app.after_request
def add_cache_control(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

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
