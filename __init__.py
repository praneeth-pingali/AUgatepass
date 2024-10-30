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

def create_app():
    app = Flask(__name__)
    UPLOAD_FOLDER = 'photos'

    app.config['MONGO_URI'] = 'mongodb+srv://pingalipraneeth1:DgCwSk9Cn9mTx32a@augatepass.1dvhlzv.mongodb.net/gatepass_db?retryWrites=true&w=majority'
    app.config['SECRET_KEY'] = 'your_secret_key'  
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'poppingaming1@gmail.com'
    app.config['MAIL_PASSWORD'] = 'atjj cynj vkwt ljkn'

    from .auth import auth
    app.register_blueprint(auth)

    from .student import student
    app.register_blueprint(student)

    from .faculty import faculty
    app.register_blueprint(faculty)

    from .security import security
    app.register_blueprint(security)

    return app

