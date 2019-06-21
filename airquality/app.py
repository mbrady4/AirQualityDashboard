from decouple import config
from flask import Flask, render_template, request
from .models import DB, PM_10_Values, PM_Values
from .data import danger_zone, get_records, add_records


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    DB.init_app(app)

    @app.route('/')
    def root():
        """Base view."""
        pm_values = danger_zone(PM_Values)
        pm_10_values = danger_zone(PM_10_Values, 100)
        return render_template('base.html', title='Air Quality Dashboard', pm_values=pm_values, pm_10_values=pm_10_values)

    @app.route('/refresh')
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

    return app