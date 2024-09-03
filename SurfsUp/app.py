# Import the dependencies.
from flask import Flask, jsonify, request
import pandas as pd
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# reflect the tables


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
Session = sessionmaker(bind=engine)
session = Session()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route('/')
def home():
    return """
    <h1>Welcome to the Climate Analysis API</h1>
    <p>Available routes:</p>
    <ul>
        <li><a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a></li>
        <li><a href="/api/v1.0/stations">/api/v1.0/stations</a></li>
        <li><a href="/api/v1.0/tobs">/api/v1.0/tobs</a></li>
        <li><a href="/api/v1.0/&lt;start&gt;">/api/v1.0/&lt;start&gt;</a> - Replace &lt;start&gt; with a start date in YYYY-MM-DD format</li>
        <li><a href="/api/v1.0/&lt;start&gt;/&lt;end&gt;">/api/v1.0/&lt;start&gt;/&lt;end&gt;</a> - Replace &lt;start&gt; and &lt;end&gt; with dates in YYYY-MM-DD format</li>
    </ul>
    """

@app.route('/api/v1.0/precipitation')
def precipitation():
    most_recent_date_str = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date_str, '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    precipitation_dict = {date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations():
    results = session.query(Station.station, Station.name).all()
    stations_list = [{'station': station, 'name': name} for station, name in results]
    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
    most_recent_date_str = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date_str, '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    most_active_station = session.query(
        Measurement.station,
        func.count(Measurement.station).label('count')
    ).group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).first()

    most_active_station_id = most_active_station.station

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    tobs_list = [{'date': date, 'temperature': tobs} for date, tobs in results]
    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>', methods=['GET'])
@app.route('/api/v1.0/<start>/<end>', methods=['GET'])
def stats(start, end=None):
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        if end:
            end_date = dt.datetime.strptime(end, '%Y-%m-%d')
        else:
            end_date = dt.datetime.now()  # or the most recent date in your dataset

        results = session.query(
            func.min(Measurement.tobs).label('min_temp'),
            func.avg(Measurement.tobs).label('avg_temp'),
            func.max(Measurement.tobs).label('max_temp')
        ).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

        stats_dict = {
            'Start Date': start_date.strftime('%Y-%m-%d'),
            'End Date': end_date.strftime('%Y-%m-%d'),
            'Min Temperature': results[0].min_temp,
            'Avg Temperature': results[0].avg_temp,
            'Max Temperature': results[0].max_temp
        }
        return jsonify(stats_dict)

    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

if __name__ == '__main__':
    app.run(debug=True)
