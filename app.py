import numpy as np
import pendulum

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

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
# session = Session(engine)

# """Return a list of all passenger names"""
#     # Query all passengers
# results = session.query(Measurements.date,Measurements.prcp).all()
# print(results)
# session.close()

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
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    results = session.query(Measurements.date,Measurements.prcp).all()

    results_dict = {k:v for k,v in results} 
    session.close()

    # Convert list of tuples into normal list

    return jsonify(results_dict)


if __name__ == '__main__':
    app.run(debug=True)