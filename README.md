# sqlalchemy-challenge
 Module 10 challenge

 I used class materials, Xpert Learning Assistant, and ChatGPT as resources to complete this assignment.  I attempted to run the entire code through Xpert Learning Assistant for code improvement recommendations, but it has a 5,000 character limit.  I ran it through ChatGPT and had I followed their suggestions I think I would have changed the homework format too much.  Regardless, I will post the suggested code from ChatGPT below as I like how organized it is:

 # Import dependencies
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

# Set up matplotlib style
plt.style.use('fivethirtyeight')

# Create engine and reflect the tables
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Function to get the most recent date from the dataset
def get_most_recent_date():
    most_recent_date_str = session.query(func.max(Measurement.date)).scalar()
    return dt.datetime.strptime(most_recent_date_str, '%Y-%m-%d')

# Function to get the most active station
def get_most_active_station():
    return session.query(
        Measurement.station,
        func.count(Measurement.station).label('count')
    ).group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).first()

# Function to query and plot precipitation data
def plot_precipitation():
    most_recent_date = get_most_recent_date()
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    df = pd.DataFrame(results, columns=['Date', 'Precipitation'])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

    plt.figure(figsize=(10, 6))
    plt.plot(df['Date'], df['Precipitation'], label='Precipitation', color='blue')
    plt.xticks(rotation=90)
    plt.xlabel('Date')
    plt.ylabel('Precipitation')
    plt.title('Precipitation over the Last 12 Months')
    plt.legend()
    plt.grid(True)
    plt.show()

# Function to calculate and print summary statistics
def print_summary_statistics():
    df = pd.read_sql(session.query(Measurement.prcp).statement, session.bind)
    summary_stats = df['prcp'].describe()
    print("Summary statistics for precipitation data:")
    print(summary_stats)

# Function to get and print total number of stations
def print_total_stations():
    total_stations = session.query(func.count(Station.id)).scalar()
    print(f"Total number of stations in the dataset: {total_stations}")

# Function to get and print most active stations
def print_most_active_stations():
    most_active_stations = session.query(
        Measurement.station,
        func.count(Measurement.station).label('count')
    ).group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    print("Most active stations and their counts (in descending order):")
    for station, count in most_active_stations:
        print(f"Station: {station}, Count: {count}")

# Function to get temperature statistics for the most active station
def print_temperature_statistics():
    most_active_station_id = get_most_active_station()[0]

    temperature_stats = session.query(
        func.min(Measurement.tobs).label('min_temp'),
        func.max(Measurement.tobs).label('max_temp'),
        func.avg(Measurement.tobs).label('avg_temp')
    ).filter(Measurement.station == most_active_station_id).all()

    min_temp, max_temp, avg_temp = temperature_stats[0]
    print(f"Lowest temperature: {min_temp}")
    print(f"Highest temperature: {max_temp}")
    print(f"Average temperature: {avg_temp:.2f}")

# Function to query and plot temperature data
def plot_temperature_histogram():
    most_active_station_id = get_most_active_station()[0]
    most_recent_date = get_most_recent_date()
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    temperatures = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    df = pd.DataFrame(temperatures, columns=['Temperature'])

    plt.figure(figsize=(10, 6))
    plt.hist(df['Temperature'], bins=12, edgecolor='black')
    plt.xlabel('Temperature')
    plt.ylabel('Frequency')
    plt.title(f'Temperature Distribution for Station {most_active_station_id} (Last 12 Months)')
    plt.grid(True)
    plt.show()

# Execute functions
try:
    print_total_stations()
    print_most_active_stations()
    plot_precipitation()
    print_summary_statistics()
    print_temperature_statistics()
    plot_temperature_histogram()
except Exception as e:
    print(f"Error: {e}")
finally:
    session.close()

