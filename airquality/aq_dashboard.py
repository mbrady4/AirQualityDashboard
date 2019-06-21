"""OpenAQ Air Quality Dashboard with Flask."""
from decouple import config
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import openaq

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'DATABASE_URL'
DB = SQLAlchemy(APP)


class PM_Values(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'< Time {self.datetime} --- Value {self.value} >'


class PM_10_Values(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'< Time {self.datetime} --- Value {self.value} >'

@APP.route('/')
def root():
    """Base view."""
    pm_values = danger_zone(PM_Values)
    pm_10_values = danger_zone(PM_10_Values, 100)
    return render_template('base.html', title='Air Quality Dashboard', pm_values=pm_values, pm_10_values=pm_10_values)

@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    values = get_records('Los Angeles', 'pm25')
    add_records(PM_Values, values)
    values = get_records('Los Angeles', 'pm10')
    add_records(PM_10_Values, values)
    DB.session.commit()
    pm_values = danger_zone(PM_Values)
    pm_10_values = danger_zone(PM_10_Values, 100)
    return render_template('base.html', title='Refreshed Data', pm_values=pm_values, pm_10_values=pm_10_values)


def get_records(city, parameter):
    # Set up the API object
    api = openaq.OpenAQ()
    _, body = api.measurements(city=city, parameter=parameter)
    results = body['results']
    values = []
    for result in results:
        values.append((result['date']['utc'], result['value'] ))
    return values


def add_records(table_name, values):
    for value in values:
        entry = table_name()
        DB.session.add(entry)
        entry.datetime = value[0]
        entry.value = value[1]
        DB.session.commit()

def danger_zone(table_name, threshold=10):
    danger_zone = table_name.query.filter(table_name.value >= threshold).all()
    return danger_zone
