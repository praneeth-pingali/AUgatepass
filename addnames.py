from flask import *
from flask_pymongo import PyMongo


app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://pingalipraneeth1:DgCwSk9Cn9mTx32a@augatepass.1dvhlzv.mongodb.net/gatepass_db?retryWrites=true&w=majority'
app.config['SECRET_KEY'] = 'your_secret_key'
mongo = PyMongo(app)

username = "20EG112347"
name="Karthik"
requests = list(mongo.db.students.find({'username': username}))

if requests:
    mongo.db.students.update_one({'username': username}, {'$set': {'name': name}})


if __name__ == '_main_':
    app.run(debug=True)