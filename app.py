import pandas as pd
import subprocess
import sys

try:
    import pendulum
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'pendulum'])
finally:
    import pendulum

from collections import OrderedDict

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
app.config["JSON_SORT_KEYS"] = False # Preventing Jsonify to reorder the dictionario elements by the keys
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
        precipitations_dict = OrderedDict()
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
def temp_stats(init_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    try:
        date = pendulum.parse(init_date).to_date_string()  # creating a DataTime object type using pendulum module and formatting like YYYY-MM_DD
    except:
        return ("<h3>Please Make sure that the Date format matches the next example: </h3>"
        f"<em><b>YYYY-MM-DD</b></em>")
    
    temp_query = session.query(Measurements.date, func.min(Measurements.tobs),func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        group_by(Measurements.date).filter(Measurements.date >= date).all()
    stats = []
    for date, t_min, t_avg, t_max in temp_query:
        temps_dict = OrderedDict()
        temps_dict["date"] = date
        temps_dict["Min_Temp"] = t_min
        temps_dict["Avg_Temp"] = round(t_avg,2)
        temps_dict["Max_Temp"] = t_max        
        stats.append(temps_dict)
    session.close()  # closing the SQLAlchemy Session!
    if len(stats)==0:
        return f"<h2>No records where found for {date} and after</2>"
    else:
        return jsonify(stats)

@app.route("/api/v1.0/<init_date>/<end_date>")
def temp_stats_multiple(init_date,end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    try:
        init_date = pendulum.parse(init_date).to_date_string()  # creating a DataTime object type using pendulum module and formatting like YYYY-MM_DD
        end_date = pendulum.parse(end_date).to_date_string()  # creating a DataTime object type using pendulum module and formatting like YYYY-MM_DD        
    except:
        return ("<h3>Please Make sure that the Date format matches the next example: </h3>"
        f"<em><b>YYYY-MM-DD</b></em>")

    if pendulum.parse(init_date) > pendulum.parse(end_date):
        return f"<em>Initial date can't be greater than final date</em>"

    temp_query = session.query(Measurements.date, func.min(Measurements.tobs),func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        group_by(Measurements.date).filter(Measurements.date >= init_date).filter(Measurements.date <= end_date).all()
    stats = []
    for date, t_min, t_avg, t_max in temp_query:
        temps_dict = OrderedDict()
        temps_dict["date"] = date
        temps_dict["Min_Temp"] = t_min
        temps_dict["Avg_Temp"] = round(t_avg,2)
        temps_dict["Max_Temp"] = t_max        
        stats.append(temps_dict)
    session.close()  # closing the SQLAlchemy Session!
    if len(stats)==0:
        return f"<h2>No records where found</h2>"
    else:
        session.close()
        return jsonify(stats)
    
if __name__ == '__main__':
    app.run(debug=True)