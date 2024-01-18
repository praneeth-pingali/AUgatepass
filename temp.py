from flask import *
from flask_pymongo import PyMongo


app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://pingalipraneeth1:DgCwSk9Cn9mTx32a@augatepass.1dvhlzv.mongodb.net/gatepass_db?retryWrites=true&w=majority'
app.config['SECRET_KEY'] = 'your_secret_key'
mongo = PyMongo(app)


for i in range(301,355):
    strr="20EG112"
    c=str(i)
    username=strr+c
    password="password"
    if(i<331):
        mongo.db.students.insert_one({'username': username, 'faculty': "padmaja"})
    else:
        mongo.db.students.insert_one({'username': username, 'faculty': "anandbabu"})



if __name__ == '__main__':
    app.run(debug=True)