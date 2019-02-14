# import requests
# from pprint import pprint
# #
# # while(1):
# #     city = input('enter any city')
# #     r = requests.get('https://api.openweathermap.org/data/2.5/weather?q={}&APPID=8b39e46493302d8e2f48506253b2ae65'.format(city))
# #     # print(r)
# #     json_data = r.json()
# #     pprint(json_data)
import requests
from pprint import pprint
from flask import Flask, flash, g, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(25)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/weather'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    Email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    cities = db.relationship('City', backref='user', lazy='dynamic')

class City(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(20), nullable=False)
    temperature = db.Column(db.String(10), nullable=False)
    icon = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(29), nullable=False)
    datetime = db.column(db.DateTime)
    user_sno = db.Column(db.Integer, db.ForeignKey('user.sno'), nullable=False)


# city temperature icon description sno datetime
@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

@app.route('/')
def index():
    if g.user:
        return redirect(url_for('weather', username=g.user))

    return render_template('index.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if g.user:
        return redirect(url_for('weather', username=g.user))

    if request.method == "POST":
        username = request.form.get('uname')
        email = request.form.get('email')
        password = request.form.get('password')
        repassword = request.form.get('repassword')

        hashed_password = generate_password_hash(password, method='sha256')

        if password != repassword:
            # flash('password not matched')
            return render_template('signup.html')

        #else
        user = User(username=username, Email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        session['user'] = username
        return redirect(url_for('weather', username=username))

    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if g.user:
        return redirect(url_for('weather', username=g.user))

    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user'] = user.username
            return redirect(url_for('weather', username=user.username))

        else:
            #invalid credintials
            pass

    return render_template('login.html')

@app.route('/weather/<string:username>', methods=['GET','POST'])
def weather(username):
    if g.user:
        user = User.query.filter_by(username=username).first()

        if request.method == 'POST':
            city = request.form.get('city')
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}"
            api_key = '8b39e46493302d8e2f48506253b2ae65'
            complete_url = url+'&'+'APPID='+api_key
            r = requests.get(complete_url)
            json_data = r.json()
            # pprint(json_data)

            if json_data['cod'] == 200:
                # pprint(json_data)
                temperature = json_data['main']['temp']
                temperature = temperature - 273.15
                description = json_data['weather'][0]['description']
                icon = json_data['weather'][0]['icon']
                print(temperature,description,icon)
                weather = City(city_name=city, temperature=temperature, icon=icon, description=description, datetime=datetime.now(), user=user)
                db.session.add(weather)
                db.session.commit()

            elif json_data['cod'] == '404':
                pass
                # flash('city not found')

        cities = user.cities
        return render_template('weather.html', username=username, cities=cities)
    return render_template('index.html')

@app.route('/logout')
def logout():
    if g.user:
        session.pop('user', None)

    return redirect(url_for('index'))

if __name__=="__main__":
    app.run(debug=True)
