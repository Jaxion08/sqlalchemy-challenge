# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
#this works better to open and close sessions in each request
#session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    return(
        f"Welcome to the Hawaii Climate API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def get_precipitation():
    session = Session(engine)
    # Find the most recent date in the data set.
    most_recent = session.query(Measurement).order_by(Measurement.date.desc()).first()
    # Calculate the date one year from the last date in data set.
    last_date = dt.datetime.strptime(most_recent.date, '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    precip_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_year_ago).all()

    #convert query to dictionary
    precip_dict = {date: prcp for date, prcp in precip_data}

    session.close()

    #return JSON of dictionary
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def get_stations():
    session = Session(engine)
    #get list of stations
    stations_query = session.query(Station.station).all()
    stations_list = [station[0] for station in stations_query]

    session.close()

    #return JSON list of stations
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def get_tobs():
    session = Session(engine)
    #get most active station
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    most_active_station = active_stations[0][0]

    #calculate last year
    most_recent = session.query(Measurement).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(most_recent.date, '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)

    #query last year
    tobs_data = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()

    #creating list
    tobs_list = [tobs[0] for tobs in tobs_data]

    session.close()

    #JSON of list
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def get_stats_start(start):
    session = Session(engine)

    #temp stats query
    temp_stats = session.query(func.min(Measurement.tobs),
                                  func.avg(Measurement.tobs),
                                  func.max(Measurement.tobs)).\
    filter(Measurement.station >= start).all()

    #temp stats dictionary
    temp_stats_dict = {
        "start_date": start,
        "TMIN": temp_stats[0][0],
        "TAVG": temp_stats[0][1],
        "TMAX": temp_stats[0][2]
    }

    session.close()

    #retrun JSON
    return jsonify(temp_stats_dict)

@app.route("/api/v1.0/<start>/<end>")
def get_stats_range(start, end):
    session = Session(engine)

    # temp stats query
    temp_stats = session.query(func.min(Measurement.tobs),
                               func.avg(Measurement.tobs),
                               func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    # temp stats dictionary
    temp_stats_dict = {
        "start_date": start,
        "end_date": end,
        "TMIN": temp_stats[0][0],
        "TAVG": temp_stats[0][1],
        "TMAX": temp_stats[0][2]
    }

    session.close()

    #retrun JSON
    return jsonify(temp_stats_dict)



if __name__ == "__main__":
    app.run(debug=True)