from flask import Flask, render_template, json,jsonify, redirect, url_for, request, flash, g, session, Response
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, expose, BaseView, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_bootstrap import Bootstrap
from functools import wraps
from flask_login import LoginManager, UserMixin, logout_user, login_user, login_required
import stripe
import stripe
import os

from collections import OrderedDict
from marshmallow import Schema, fields, pprint

from SQLAlchemy_drive_db import User, Stops, Drivers, Buses, Companies, Routes\
    , Passenger, Order,Schedule
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, IntegerField, PasswordField


app = Flask(__name__)
app.secret_key = 'super secret key'
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class MyIterator:
    def __init__(self,iterable_obj):
        self.iterable_obj = iterable_obj
        self.index = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.index +=1
        if self.index == len(self.iterable_obj):
            raise StopIteration
        else:
            return self.iterable_obj[self.index]


class StopsMapView(BaseView):
    """return stop map view which extend base view"""
    @expose('/')
    def index(self):
        points = []

        stops_list = db.session.query(Stops).all()
        for item in MyIterator(stops_list):
            stops_dict = item.__dict__
            if '_sa_instance_state' in stops_dict:
                del stops_dict['_sa_instance_state']
            points.append(stops_dict)

        return self.render('admin/stopsMap.html',points=json.dumps(points))

class StopsAddPoint(ModelView):
    create_template = 'stops_create.html'
    # form_columns = ['address','lat','lng']

class RouteListInfo(ModelView):
    list_template = 'routesInfo.html'


admin = Admin(app)
admin.add_view(ModelView(User, db.session))
admin.add_view(StopsAddPoint(Stops,db.session))
admin.add_view(StopsMapView(name='Map of stops'))
admin.add_view(ModelView(Drivers,db.session))
admin.add_view(ModelView(Buses, db.session))
admin.add_view(ModelView(Companies, db.session))
admin.add_view(RouteListInfo(Routes, db.session))
admin.add_view(ModelView(Passenger,db.session))
admin.add_view(ModelView(Order,db.session))
admin.add_view(ModelView(Schedule,db.session))

@app.route('/')
def start():
    return redirect(url_for('routes2'))


@app.route('/routes',defaults={'ids':None})
@app.route('/routes/<ids>',methods=['POST','GET'])
def routes2(ids):
    """at first return default route, then after query return
    selected route which connected with its ids"""
    points = None
    curent_route = None
    routes_name = db.session.query(Routes)
    if ids:
        points = []
        curent_route = db.session.query(Routes).filter(Routes.id == ids).first()

        for u in db.session.query(Stops) \
                .join(Routes.stops).filter(Routes.id == ids):
            stops_dict = u.__dict__
            if '_sa_instance_state' in stops_dict:
                del stops_dict['_sa_instance_state']
            points.append(stops_dict)


    return render_template('RoutesMap.html',routes= routes_name,points=json.dumps(points), curent_route=curent_route)

class PassangerForm(FlaskForm):
    name = StringField('Enter name')
    surname = StringField('Enter surname')
    sex = SelectField(choices=[(g, g)for g in Passenger.sex.property.columns[0].type.enums])
    nationality = SelectField(choices=[(g, g)for g in Passenger.nationality.property.columns[0].type.enums])
    passport = StringField('Enter passport series and number')


class UserForm(FlaskForm):
    login = StringField('Enter login')
    password = PasswordField('Enter password')


@app.route('/buy_tickets/<route_id>/<schedule_id>',methods=['POST','GET'])
@login_required
def buy_tickets(route_id,schedule_id):
    route = db.session.query(Routes).filter(Routes.id == route_id).first()
    schedule = db.session.query(Schedule).filter(Schedule.id == schedule_id).first()
    form = PassangerForm()
    if request.method=='POST':
        if form.validate_on_submit():
            new_passanger = Passenger(name=form.name.data,surname=form.surname.data,sex=form.sex.data,nationality=form.nationality.data\
                                      ,passport=form.passport.data)
            db.session.add(new_passanger)
            db.session.commit()
            flash('Passenger has been registered')

    return render_template('BuyTicket.html',form=form, route = route, schedule=schedule)

def counted(f):
    def wrapped(*args, **kwargs):
        wrapped.calls += 1
        print('{} has been call {} times'.format(f,wrapped.calls))
        return f(*args, **kwargs)
    wrapped.calls = 0
    return wrapped

@app.route('/schedule/<route_id>',methods=['POST','GET'])
@counted
def schedule(route_id):
    schedules = db.session.query(Routes,Schedule,Buses).join(Schedule).filter(Schedule.route_id == route_id).join(Buses).filter(Schedule.bus_id == Buses.id)

    return render_template('Schedule.html', schedules=schedules)




@app.route('/login',methods=['GET','POST'])
def login():
    form = UserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user_data = db.session.query(User).filter(User.login == form.login.data).first()
            if user_data:
                if user_data.password == form.password.data:
                    login_user(user_data)
                    return redirect(url_for('routes2'))
    return render_template('logIn.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return 'You has been logout'

@app.errorhandler(401)
def custom_401(error):
    return render_template('Unauthorized_error.html')

stripe.api_key = app.secret_key

@app.route('/pay',methods=['POST'])
def pay():
    customer = stripe.Customer.create(email = request.form['stripeEmail'], source = request.form['stripeToken'])

    charge = stripe.Charge.create(
        customer = customer.id,
        amount = 111,
        currency = 'usd',
        description = 'The product'
    )

    return redirect(url_for('routes'))

pub_key = 'pk_test'

@app.route('/payment')
def payment():
    return render_template('Payment.html', pub_key=pub_key)






if __name__ == '__main__':
    app.run(debug=True)
