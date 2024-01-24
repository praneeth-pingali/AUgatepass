from flask import *
from flask_pymongo import PyMongo


app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://pingalipraneeth1:DgCwSk9Cn9mTx32a@augatepass.1dvhlzv.mongodb.net/gatepass_db?retryWrites=true&w=majority'
app.config['SECRET_KEY'] = 'your_secret_key'
mongo = PyMongo(app)

delete_result = mongo.db.students.delete_many({'name': {'$exists': False}})

if __name__ == '__main__':
    app.run(debug=True)
