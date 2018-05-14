from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask import Flask

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)



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

    def __repr__(self):
        return self.model

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