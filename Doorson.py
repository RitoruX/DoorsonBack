from flask import Flask, request
from flask_pymongo import PyMongo
from datetime import datetime
import pytz
from flask_cors import CORS, cross_origin
from bson.json_util import dumps

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
        "firstname" : data["firstname"],
        "lastname" : data["lastname"],
        "pplnum" : data["pplnum"],
        "tel" : data["tel"],
        "date" : now.strftime("%d/%b/%Y"),
        "time" : now.strftime('%H:%M:%S')
    }
    doorsonCollections.insert(check_in_query)
    return {"result" : "Checkin Successfully"}

@app.route('/show_n', methods=['GET'])
def show_n():
    list_pplnum = list(doorsonCollections.aggregate([{
        "$group": {
            "_id": "null",
            "total_users" : {"$sum" : "$pplnum"}
        }}]))[0]
    list_pplnum.pop("_id")
    return dumps(list_pplnum)

@app.route('/check_out', methods=['UPDATE'])
def check_out():
    data = request.json
    filt = {'firstname': data['firstname']}
    updated_content = {"$set": {'pplnum' : 0}}
    doorsonCollections.update_one(filt, updated_content)
    return {"result" : "Check-Out Successfully"}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3000', debug=True)
# @app.route("/check_out", methods=["DELETE"])
# def checkout():
#     data = request.json()
