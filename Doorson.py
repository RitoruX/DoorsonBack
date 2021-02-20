from flask import Flask, request, render_template, redirect, url_for
from flask_pymongo import PyMongo
from datetime import datetime
import pytz
from flask_cors import CORS, cross_origin
from bson.json_util import dumps
from flask_mongoengine import MongoEngine, Document
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, Length, InputRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://exceed_group12:nhm88g6s@158.108.182.0:2255/exceed_group12'
mongo = MongoEngine(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# cors = CORS(app, resources={r"/": {"origins" : "*"}}, support_credentials=True)
cors = CORS(app, support_credentials=True)

doorsonCollections = mongo.db.data

class User(UserMixin, mongo.Document):
    meta = {'collection': 'data'}
    username = mongo.StringField(max_length=30)
    password = mongo.StringField()

@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()

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
        "date" : now.strftime("%d/%b/%Y"),
        "time" : now.strftime('%H:%M:%S')
    }
    doorsonCollections.insert(check_in_query)
    return {"result" : "Check-In Successfully"}

@app.route('/show_n', methods=['GET'])
# @cross_origin()
def show_n():
    list_pplnum = list(doorsonCollections.aggregate([{
        "$group": {
            "_id": "null",
            "total_users" : {"$sum" : { "$toInt" : "$pplnum"}}
        }}]))[0]
    list_pplnum.pop("_id")
    return dumps(list_pplnum)

@app.route('/check_out', methods=['PATCH'])
# @cross_origin()
def check_out():
    data = request.json
    filt = {'firstname': data['firstname']}
    updated_content = {"$set": {'pplnum' : 0}}
    doorsonCollections.update_one(filt, updated_content)
    return {"result" : "Check-Out Successfully"}

@app.route('/show_admin', methods=['GET'])
# @cross_origin()
def show_admin():
    query = doorsonCollections.find()
    output = []
    for element in query:
        output.append({
            "firstname" : element['firstname'],
            "lastname" : element['lastname'],
            "pplnum" : element['pplnum'],
            "time" : element['time'],
            "date" : element['date']
        })
    return {"result" : output}

@app.route('/show_users', methods=['GET'])
# @cross_origin()
def show_users():
    query = doorsonCollections.find()
    output = []
    for element in query:
        # temp_string = element['firstname'][0:2] + ('x' * (len(element['firstname']) - 1))
        output.append({
            "firstname" : element['firstname'],
            "pplnum" : element['pplnum'],
            "time" : element['time'],
            "date" : element['date']
        })
    return {"result" : output}

class RegForm(FlaskForm):
    username = StringField('username',  validators=[InputRequired(), Length(max=30)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=20)])

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if request.method == 'POST':
        if form.validate():
            existing_user = User.objects(email=form.username.data).first()
            if existing_user is None:
                hashpass = generate_password_hash(form.password.data, method='sha256')
                hey = User(form.username.data,hashpass).save()
                login_user(hey)
                return redirect(url_for('dashboard'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated == True:
        return redirect(url_for('dashboard'))
    form = RegForm()
    if request.method == 'POST':
        if form.validate():
            check_user = User.objects(email=form.username.data).first()
            if check_user:
                if check_password_hash(check_user['password'], form.password.data):
                    login_user(check_user)
                    return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout', methods = ['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3000', debug=True)