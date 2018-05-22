from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask import Flask
import enum
from _datetime import datetime

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import pycountry

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)
from flask_login import UserMixin

class User(UserMixin,db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80),nullable=False, unique=True)
    password = db.Column(db.String(80),nullable=False, server_default='')
    active = db.Column(db.Boolean(),nullable=False,server_default='0')


countries_enum = list(map(lambda country: country.name,pycountry.countries))

class Passenger(db.Model):
    __tablename__ = 'passenger'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),nullable=False)
    surname = db.Column(db.String(80),nullable=False)
    sex = db.Column(db.Enum('male','female'),nullable=False)
    nationality = db.Column(db.Enum(*countries_enum),nullable=False)
    passport = db.Column(db.String(80),nullable=False)
    orders = db.relationship('Order', backref='Orders2')

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    order_data  = db.Column(db.DateTime,nullable=False)
    route_id = db.Column(db.INTEGER, db.ForeignKey('routes.id'))
    seat_number = db.Column(db.INTEGER, nullable=False)
    passenger_id = db.Column(db.INTEGER, db.ForeignKey('passenger.id'))
    email = db.Column(db.String(80))
    telephone = db.Column(db.String(80))


stops_routes = db.Table('stops_routes',
    db.Column('stop_id', db.Integer,db. ForeignKey('stops.id')),
    db.Column('route_id', db.Integer, db.ForeignKey('routes.id'))
    )

companies_routes = db.Table('companies_routes',
    db.Column('companies_id',db.INTEGER,db.ForeignKey('companies.id')),
    db.Column('routes_id',db.INTEGER,db.ForeignKey('routes.id'))
    )



class Stops(db.Model):
    __tablename__ = 'stops'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(80))
    lat = db.Column(db.DECIMAL())
    lng = db.Column(db.DECIMAL())

    def __repr__(self):
        return self.address

class Buses(db.Model):
    __tablename__ = 'buses'
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(80))
    route_id = db.Column(db.INTEGER,db.ForeignKey('routes.id'))
    company_id = db.Column(db.INTEGER,db.ForeignKey('companies.id'))
    driver_id = db.Column(db.INTEGER,db.ForeignKey('drivers.id'))
    number_of_seat = db.Column(db.INTEGER)
    bus_schedule = db.relationship('Schedule', backref="Bus_schedule")

    def __repr__(self):
        return self.model
class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.INTEGER,db.ForeignKey('buses.id'))
    departure_data = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)

    def __repr__(self):
        return 'Schedule at time {0}'.format(self.departure_data)




class Companies(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.INTEGER,primary_key=True)
    name = db.Column(db.String(80))
    manager = db.Column(db.String(80))
    routes = db.relationship('Routes',secondary=companies_routes)
    buses = db.relationship('Buses',backref = "Company's bus " )

    def __repr__(self):
        return self.name

class Routes(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.INTEGER,primary_key=True)
    name = db.Column(db.String(80))
    price = db.Column(db.Float)
    time = db.Column(db.Float)
    buses = db.relationship('Buses',backref="Route's bus")
    stops = db.relationship('Stops', secondary=stops_routes, backref="stops")
    orders = db.relationship('Order',backref='Orders')

    def __repr__(self):
        return self.name

class Drivers(db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(80))
    surname = db.Column(db.String(80))
    birthday = db.Column(db.Date)
    telephone = db.Column(db.String(80))
    buses = db.relationship('Buses', backref="Driver's bus")

    def __repr__(self):
        return ('{} {}'.format(self.name, self.surname))

if __name__ == '__main__':
    manager.run()