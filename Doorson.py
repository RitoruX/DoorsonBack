from flask import Flask, request
from flask_pymongo import PyMongo
from datetime import datetime
import pytz
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://exceed_group12:nhm88g6s@158.108.182.0:2255/exceed_group12'
mongo = PyMongo(app)

cors = CORS(app, support_credentials=True)

doorsonCollections = mongo.db.data

@app.route('/check_in', methods=['POST'])
def check_in():
    data = request.json
    now = datetime.now(pytz.timezone('Asia/Bangkok'))
    check_in_query = {
        "first_name" : data["first_name"],
        "last_name" : data["last_name"],
        "n_persons" : data["n_persons"],
        "tel" : data["tel"],
        "date" : now.strftime("%d/%b/%Y"),
        "time" : now.strftime('%H:%M:%S')
    }
    doorsonCollections.insert(check_in_query)
    return {"result" : "Checkin Successfully"}

@app.route('/show_n', methods=['GET'])
def show_n():
    return doorsonCollections.aggregate([
            {
                "$project": {
                    "total_users" : {"$sum" : "$n_persons"}
                } 
            }
        ]).findall()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3000', debug=True)
# @app.route("/check_out", methods=["DELETE"])
# def checkout():
#     data = request.json()
