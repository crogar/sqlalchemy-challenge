import numpy as np
import pandas as pd
import pendulum

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


#################################################
# Database Setup                               #
###############################################

# Creating engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurements = Base.classes.measurement
Stations = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################


@app.route("/")
def index():
    """List all available api routes."""
    return (
        f"<h1>Available Routes:</h1><br/>"
        f"<ul>"
        f"<h3>"
        f"<li>/api/v1.0/precipitation</li>"
        f"<li>/api/v1.0/stations</li>"
        f"<li>/api/v1.0/tobs</li>"
        f"<li>/api/v1.0/2017-08-23</li>"
        f"<li>/api/v1.0/2017-08-23/2018-08-23</li>"
        f"</h3>"
        f"</ul>"
    )

@app.route("/api/v1.0/precipitation")
def precipitations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all PRCPs for all  datess"""
    # Query all the dates and PRCPs
    results = session.query(Measurements.date,Measurements.prcp).all()
    # date as the key and prcp as the value.
    precipitations = []
    for date, prcp in results:
        precipitations_dict = {}
        precipitations_dict["date"] = date
        precipitations_dict["prcp"] = prcp
        precipitations.append(precipitations_dict)

    session.close()

    return jsonify(precipitations)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a list of all the stations"""
    # Query all the dates and PRCPs
    results = session.query(Stations).statement
    stations_df = pd.read_sql_query(results, session.bind)
    
    stations = []
    for index, row in stations_df.iterrows():
        station_dict = {}
        for column in stations_df.columns:
            station_dict[column] = row[column]
        stations.append(station_dict)
    session.close()
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all tobs for the last year"""
    # Calculating most recent date in DB and obtaining a year of data from that date.
    # Find the most recent date in the data set.
    most_recent_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()[0]
    # Starting from the most recent data point in the database. 
    dt = pendulum.parse(most_recent_date)  # creating a DataTime object type using pendulum module
    # Calculate the date one year from the last date in data set.
    previous_year = dt.subtract(years=1).to_date_string() # Substracting one year to the most recent date and formating as YYYY-MM-DD

    # Calculating the top Station
    # List the stations and the counts in descending order.
    stations_activity = session.query(Measurements.station, func.count(Measurements.station)).group_by(Measurements.station).\
    order_by(func.count(Measurements.station).desc()).all()
    top_station = stations_activity[0]

    # Design a query to retrieve the last 12 months of tobs data.
    results = session.query(Measurements.date, Measurements.tobs).filter(Measurements.date >= previous_year).\
    filter(Measurements.station == top_station[0]).order_by(Measurements.date).all()
    
    # date as the key and prcp as the value.
    tobs = []
    for date, tob in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tob
        tobs.append(tobs_dict)

    session.close()

    return jsonify(tobs)

@app.route("/api/v1.0/<init_date>/")
def temp_stats(init_date=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Formatting Date. 
    date = pendulum.parse(init_date).to_date_string()  # creating a DataTime object type using pendulum module and formatting like YYYY-MM_DD
    temp_query = session.query(Measurements.tobs).filter(Measurements.date >= date).all()
    
    return jsonify(temp_query)


if __name__ == '__main__':
    app.run(debug=True)