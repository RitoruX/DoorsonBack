from flask import Flask, request
from flask_pymongo import PyMongo
from datetime import datetime
import pytz
from flask_cors import CORS, cross_origin
from bson.json_util import dumps

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://exceed_group12:nhm88g6s@158.108.182.0:2255/exceed_group12'
mongo = PyMongo(app)

# cors = CORS(app, resources={r"/": {"origins" : "*"}}, support_credentials=True)
cors = CORS(app, support_credentials=True)

doorsonCollections = mongo.db.data

@app.route('/check_in', methods=['POST'])
# @cross_origin()
def check_in():
    data = request.json
    now = datetime.now(pytz.timezone('Asia/Bangkok'))
    check_in_query = {
        "firstname" : data["firstname"],
        "lastname" : data["lastname"],
        "pplnum" : data["pplnum"],
        "tel" : data["tel"],
        "store" : "1",
        "date" : now.strftime("%d/%b/%Y"),
        "time" : now.strftime('%H:%M:%S')
    }
    doorsonCollections.insert(check_in_query)
    return {"result" : "Check-In Successfully"}

@app.route('/show_n', methods=['GET'])
# @cross_origin()
def show_n():
    args_name = request.args.get('store')
    search_store = list(doorsonCollections.find({"store" : args_name}))
    num = 0
    for element in search_store:
        num += int(element['pplnum'])
    # list_pplnum = list(doorsonCollections.aggregate(
    #     [
    #         {
    #             "$match" : { "$store" : args_name }
    #         },
    #         {
    #             "$group": { "total_users" : {"$sum" : { "$toInt" : "$pplnum"}} }
    #         }
    #     ]
    #     ))[0]
    # list_pplnum.pop("_id")
    output = {
        "total_users" : num
    }
    return dumps(output)

@app.route('/check_out', methods=['PATCH'])
# @cross_origin()
def check_out():
    data = request.json
    filt = {'firstname': data['firstname'], 'stores' : data['stores']}
    updated_content = {"$set": {'pplnum' : 0}}
    doorsonCollections.update_one(filt, updated_content)
    return {"result" : "Check-Out Successfully"}

@app.route('/show_admin', methods=['GET'])
# @cross_origin()
def show_admin():
    args_name = request.args.get('store')
    list_store = doorsonCollections.find({ "store" : args_name})
    output = []
    for element in list_store:
        output.append({
            "firstname" : element['firstname'],
            "lastname" : element['lastname'],
            "pplnum" : element['pplnum'],
            "tel" : element['tel'],
            "time" : element['time'],
            "date" : element['date'],
            "store" : element['store']
        })
    return {"result" : output}

@app.route('/show_users', methods=['GET'])
# @cross_origin()
def show_users():
    args_name = request.args.get('store')
    list_store = doorsonCollections.find({ "store" : args_name})
    output = []
    for element in list_store:
        # temp_string = element['firstname'][0:2] + ('x' * (len(element['firstname']) - 1))
        output.append({
            "firstname" : element['firstname'],
            "pplnum" : element['pplnum'],
            "time" : element['time'],
            "date" : element['date']
        })
    return {"result" : output}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3000', debug=True)