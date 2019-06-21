from .openaq import OpenAQ
from .models import DB, PM_10_Values, PM_Values

def get_records(city, parameter):
    # Set up the API object
    api = OpenAQ()
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