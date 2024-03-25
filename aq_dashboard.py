"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openaq

app = Flask(__name__)

API = openaq.OpenAQ()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(app)


class Record(DB.Model):
    # id (integer, primary key)
    id = DB.Column(DB.Integer, primary_key=True,
                   nullable=False, autoincrement=True,)
    # datetime (string)
    datetime = DB.Column(DB.String)
    # value (float, cannot be null)
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f"Record: {self.id}, {self.datetime}, {self.value}"


def convert_to_tuples(results):
    return [(data['date']['utc'], data['value'])
            for data in results]


def get_results():
    _, body = API.measurements(parameter='pm25')

    return convert_to_tuples(body['results'])


def add_all_to_db(data):
    for item in data:
        if item:
            DB.session.add(item)


@app.route('/')
def root():
    """Base view."""
    results = Record.query.all()

    results_str = str(results)

    return results_str


@app.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()

    results = get_results()
    records = [
        Record(datetime=value[0], value=value[1])
        for value in results
    ]

    add_all_to_db(records)
    DB.session.commit()

    return root()
