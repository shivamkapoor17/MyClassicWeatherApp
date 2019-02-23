# favicon icon
# city already added
# code cleaning
# sql not start error
# man kar gaya to forget password

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
from sqlalchemy.exc import IntegrityError
from requests.exceptions import ConnectionError
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
    datetime = db.Column(db.DateTime)
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
        confirm_password = request.form.get('confirmpassword')

        if username == "" or email == "" or password == "" or confirm_password == "":
            flash('You miss some of the entries. Please complete the entries')

        elif password != confirm_password:
            flash('Password fields not matched. Please enter same password in both the password fields')


        else:
            hashed_password = generate_password_hash(password, method='sha256')
            try:
                user = User(username=username, Email=email, password=hashed_password)
                db.session.add(user)
                db.session.commit()
            except IntegrityError:
                flash('Username already exists Please choose different Username ')
            else:
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
            flash('Please enter correct Username and Password')


    return render_template('login.html')

@app.route('/weather/<string:username>', methods=['GET','POST'])
def weather(username):
    if g.user:
        user = User.query.filter_by(username=username).first()

        if request.method == 'POST':
            city = request.form.get('city')
            api_key = '8b39e46493302d8e2f48506253b2ae65'
            payload = {'q': city, 'APPID': api_key}
            url = f"https://api.openweathermap.org/data/2.5/weather"

            try:
                r = requests.get(url, payload)
            except ConnectionError:
                flash('Please check the Internet connection', 'info')
            else:
                json_data = r.json()
            # pprint(json_data)

                if json_data['cod'] == 200:
                    # pprint(json_data)
                    temperature = json_data['main']['temp']
                    temperature = round((temperature - 273.15), 3)
                    description = json_data['weather'][0]['description']
                    icon = json_data['weather'][0]['icon']

                    weather = City(city_name=city, temperature=temperature, icon=icon, datetime=datetime.now(), description=description, user=user)
                    db.session.add(weather)
                    db.session.commit()

                elif json_data['cod'] == '404':
                    flash('Please enter valid city', 'error')

        cities = user.cities
        # for city in cities:
        #     print(city.city_name)
        return render_template('weather.html', username=username, cities=cities)
    return render_template('index.html')

@app.route('/logout')
def logout():
    if g.user:
        session.pop('user', None)

    return redirect(url_for('index'))

@app.route('/update/<string:sno>')
def update(sno):
    if g.user:
        city = City.query.get(sno)
        api_key = '8b39e46493302d8e2f48506253b2ae65'
        payload = {'q': city.city_name, 'APPID': api_key}
        url = f"https://api.openweathermap.org/data/2.5/weather"
        try:
            r = requests.get(url, payload)
        except ConnectionError:
            flash('Please check the Internet connection', 'info')
        else:
            json_data = r.json()

            temperature = json_data['main']['temp']
            temperature = round((temperature - 273.15), 3)
            description = json_data['weather'][0]['description']
            icon = json_data['weather'][0]['icon']
            dateTime = datetime.now()

            city.temperature = temperature
            city.description = description
            city.icon = icon
            city.datetime = dateTime
            db.session.commit()
            # pprint(json_data)
            # city_name temperature icon description sno datetime
            # city.city_nam


    return redirect(url_for('index'))

@app.route('/remove/<string:sno>')
def remove(sno):
    if g.user:
        remove_city = City.query.get(sno)
        db.session.delete(remove_city)
        db.session.commit()

    return redirect(url_for('index'))

if __name__=="__main__":
    app.run(debug=True)
