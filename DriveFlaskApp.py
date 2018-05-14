from flask import Flask, render_template, json,jsonify, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, expose, BaseView, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from collections import OrderedDict
from marshmallow import Schema, fields, pprint

from SQLAlchemy_drive_db import User, Stops, Drivers, Buses, Companies, Routes,stops_routes

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)


class StopsMapView(BaseView):
    @expose('/')
    def index(self):
        points = []
        for u in db.session.query(Stops).all():
            stops_dict = u.__dict__
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
admin.add_view(StopsAddPoint(Stops,db.session))
admin.add_view(StopsMapView(name='Map of stops'))
admin.add_view(ModelView(Drivers,db.session))
admin.add_view(ModelView(Buses, db.session))
admin.add_view(ModelView(Companies, db.session))
admin.add_view(RouteListInfo(Routes, db.session))

@app.route('/')
def start():
    return redirect(url_for('routes2'))


@app.route('/routes',defaults={'ids':None})
@app.route('/routes/<ids>',methods=['POST','GET'])
def routes2(ids):
    points = None
    curent_route = None
    routes_name = db.session.query(Routes)
    if ids:
        points = []
        curent_route = db.session.query(Routes).filter(Routes.id == ids).first()
        print(curent_route)
        for u in db.session.query(Stops) \
                .join(Routes.stops).filter(Routes.id == ids):
            stops_dict = u.__dict__
            if '_sa_instance_state' in stops_dict:
                del stops_dict['_sa_instance_state']
            points.append(stops_dict)

    return render_template('RoutesMap.html',routes= routes_name,points=json.dumps(points), curent_route=curent_route)

if __name__ == '__main__':
    app.run(debug=True)
