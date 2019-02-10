# import requests
# from pprint import pprint
#
# while(1):
#     city = input('enter any city')
#     r = requests.get('https://api.openweathermap.org/data/2.5/weather?q={}&APPID=8b39e46493302d8e2f48506253b2ae65'.format(city))
#     print(r)
#     json_data = r.json()
#     pprint(json_data)
from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(25)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/weather'
db = SQLAlchemy(app)

class User(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    Email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    cities = db.relationship('City', backref='user', lazy=True)

class City(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(20), nullable=False)
    temperature = db.Column(db.String(10), nullable=False)
    icon = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(29), nullable=False)
    datetime = db.column(db.DateTime)
    user_sno = db.Column(db.Integer, db.ForeignKey('user.sno'), nullable=False)


# city temperature icon description sno datetime



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == "POST":
        username = request.form.get('uname')
        email = request.form.get('email')
        password = request.form.get('password')
        repassword = request.form.get('repassword')

        hashed_password = generate_password_hash(password, method='sha256')

        if password != repassword:
            return render_template('signup.html')
            # flash('password not matched')


        user = User(username=username, Email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('weather'))

    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('password')

        user = User.query.filter_by(username).first()
        if user:
            if check_password_hash(user.password, password):
                #create session hare
                return redirect(url_for('weather', name=user.username))

    return render_template('login.html')

@app.route('/weather/<string:name>')
@app.route('/weather')
def weather():
    return render_template('weather.html')

if __name__=="__main__":
    app.run(debug=True)
