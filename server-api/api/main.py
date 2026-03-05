from typing import Union
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from scipy import stats
import pydantic
import sqlmodel
import requests
from datetime import datetime
import math

IQ_SEARCH_RADIUS = 100
UNNAMED_ROAD_STRING = "Unnamed"
IQ_TOKEN = "pk.e27e659d87b04fd8f55014c2e2e82ccc"; # locationIQ API token
OUTLIER_THRESHOLD = 3 # z_score threshold to drop outlier points

# Format for receiving condition data from RPi
# If this class is changed, the class "RoadData" in /rpi-api/apiRequests.py must also be updated.
class RoadData(pydantic.BaseModel):
    lat: float = pydantic.Field(..., ge=-90, le=90, description="lat must be within bounds [-90, 90]")
    lng: float = pydantic.Field(..., ge=-180, le=180, description="lng must be within bounds [-180, 180]")
    roughness: float = pydantic.Field(..., ge=0, description="roughness must be non-negative")
    timestamp: float = pydantic.Field(..., ge=0, description="timestamp (in unix epoch milliseconds) must be non-negative")

# Format for data points in the database
class DataPoint(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    lat: float = sqlmodel.Field(..., index=True, ge=-90, le=90, description="lat must be within bounds [-90, 90]")
    lng: float = sqlmodel.Field(..., index=True, ge=-180, le=180, description="lng must be within bounds [-180, 180]")
    roughness: float = sqlmodel.Field(..., ge=0, description="roughness must be non-negative")
    timestamp: float = sqlmodel.Field(..., index=True, ge=0, description="timestamp (in unix epoch milliseconds) must be non-negative")
    streetname: str = sqlmodel.Field(..., index=True, description="street name as returned by LocationIQ Nearest API")

# Create API instance
app = FastAPI()

# Define CORS middleware (allows broader API use)
origins = [
    "http://roadmonitor.online",
    "http://roadmonitor.online:8000",
    "https://roadmonitor.online",
    "https://roadmonitor.online:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start the database engine instance (creates database file if it doesn't exist)
sqlite_file_name = "roadmonitor-data-points.db"
sqlite_url = f"sqlite:///api/database/{sqlite_file_name}"
engine = sqlmodel.create_engine(sqlite_url, echo=True)

# Create a table with DataPoint if doesn't already exist
sqlmodel.SQLModel.metadata.create_all(engine)

# Root endpoint
@app.get("/")
def read_root():
    return {"Response": "You have reached RoadMonitor's API. Visit www.roadmonitor.online/docs/api for more information."}

# Send data to the database (used from RoadMonitor sensor device only)
@app.post("/data")
def post_road_data(data: RoadData = Depends()):

    # get the street name for this point from LocationIQ Nearest API - LONGITUDE BEFORE LATITUDE


    # if we cannot find a nearby road, reject the data
    try:
        url = (f"https://us1.locationiq.com/v1/nearest/driving/"
            f"{data.lng:.7f},"
            f"{data.lat:.7f}"
            f"?radiuses={IQ_SEARCH_RADIUS}"
            f"&key={IQ_TOKEN}"
            f"&number=1")
        print(url)

        resp = requests.get(url)
        resp_dict = resp.json()
        datapoint_streetname = resp_dict["waypoints"][0]["name"] if (resp_dict["waypoints"][0]["name"] != "") else UNNAMED_ROAD_STRING

        print("New point streetname:", datapoint_streetname)

    except:
        print("No nearby road found, data rejected")
        raise HTTPException(status_code=400, detail="No nearby road found, data rejected")

    # data point is validated by the pydantic model
    # Store received point in server's local database
    with sqlmodel.Session(engine) as session:
        new_datapoint = DataPoint(
            lat = data.lat,
            lng = data.lng,
            roughness = data.roughness,
            timestamp = data.timestamp,
            streetname = datapoint_streetname)
        session.add(new_datapoint)
        session.commit()
        print("New Point ID:", new_datapoint.id)

    return {"Response": f"Data received for {datapoint_streetname}!"}

# Get conditions by coordinates (publicly available)
@app.get("/conditions/coords/")
def get_conditions_from_coordinates(lat: float, lng: float, radius: int = 200, start: float = 0, end: float = 0):

    # lat (latitude) must be within [-90, 90]
    if (lat < -90 or lat > 90):
        raise HTTPException(status_code=400, detail="lat (latitude) must be within the bounds [-90, 90].")

    # lng (longitude) must be within [-180, 180]
    if (lng < -180 or lng > 180):
        raise HTTPException(status_code=400, detail="lng (longitude) must be within the bounds [-180, 180].")

    # radius must be a positive integer
    if (radius <= 0):
        raise HTTPException(status_code=400, detail="radius must be a positive integer.")

    # start and end must be non-negative
    if (start < 0 or end < 0):
        raise HTTPException(status_code=400, detail="start and end must be non-negative.")

    # start cannot be after end
    if (start > end):
        raise HTTPException(status_code=400, detail="start cannot be after end.")

    # if start = end = 0, no range is specified and set "end" to current UNIX milliseconds
    if (start == 0 and end == 0):
        end = datetime.now().timestamp()*1000

    # get the closest road to the requested coordinates using locationIQ - LONGITUDE BEFORE LATITUDE
    streetname = None
    try: 
        url = (f"https://us1.locationiq.com/v1/nearest/driving/"
                f"{lng:.7f},"
                f"{lat:.7f}"
                f"?radiuses={IQ_SEARCH_RADIUS}"
                f"&key={IQ_TOKEN}"
                f"&number=1")
        print(url)

        resp = requests.get(url)
        resp_dict = resp.json()
        streetname = resp_dict["waypoints"][0]["name"] if (resp_dict["waypoints"][0]["name"] != "") else UNNAMED_ROAD_STRING

        print("Request streetname:", streetname)

     # if no road is close enough, raise an error
    except:
        print("No nearby road found, request rejected")
        raise HTTPException(status_code=400, detail="No nearby road found. Please select coordinates which are closer to the road.")

    # convert radius (m) to approximate longitude and latitude values
    lat_radius = radius / 111_111 # conversion factor
    lng_radius = radius / (111_111 * math.cos(lng*(math.pi/180))) # conversion factor using longitude in radians

    # create the latitude/longitude boundaries, based on the requested radius and the formula [min + (value - min) % (max - min)] to wrap values
    lat_bounds = [-90 + (lat-lat_radius+90) % 180, -90 + (lat+lat_radius+90) % 180]
    lng_bounds = [-180 + (lng-lng_radius+180) % 360, -180 + (lng+lng_radius+180) % 360]
    #TODO: Fix the SQL search if value wraps by doing two queries (will never happen in ottawa)

    # select specified data from RoadMonitor database
    with sqlmodel.Session(engine) as session:
        statement = sqlmodel.select(DataPoint.roughness) \
            .where(DataPoint.lat >= lat_bounds[0], DataPoint.lat <= lat_bounds[1]) \
            .where(DataPoint.lng >= lng_bounds[0], DataPoint.lng <= lng_bounds[1]) \
            .where(DataPoint.streetname == streetname) \
            .where(DataPoint.timestamp >= start, DataPoint.timestamp <= end)
            
        matching_datapoints = session.exec(statement).all()
        df_datapoints = pd.DataFrame(matching_datapoints, columns=["Roughness"])
        
        num_original = len(df_datapoints)

        # If there are no points, then do not process data
        if num_original > 0:
            
            # remove outliers from the data
            z_scores = np.abs(stats.zscore(df_datapoints["Roughness"]))
            outlier_indices = np.where(z_scores > OUTLIER_THRESHOLD)[0]
            clean_data = df_datapoints.drop(index=outlier_indices)

            num_points = len(clean_data)
            num_dropped = len(outlier_indices)

            print(f"Dropped {num_dropped} outliers out of {num_original} data points, leaving {num_points} to be used")

            points_variance = clean_data["Roughness"].var() # find variance of non-outlier values. Higher variance means we should be less confident
            if pd.isna(points_variance): points_variance = None

            roughness = clean_data["Roughness"].mean() # average the non-outlier values

            # return the requested data to user
            return {
                "lat": lat, # lat: the requested latitude
                "lng": lng, # lng: the requested longitude
                "radius": radius, # radius: the requested search radius
                "start": start, # start: the requested time range start in UNIX epoch milliseconds
                "end": end, # end: the requested time range end in UNIX epoch milliseconds
                "streetname": streetname, # streetname: derived from locationIQ, roughness only pertains to data collected on this road
                "num_points": num_points, # num_points: the number of data points used in calculating roughness
                "points_variance": points_variance, # points_variance: the variance of the data points used in calculating roughness - higher = less reliable estimate
                "roughness": roughness} # roughness: the roughness of the street, determined from all data points within the radius and time range

        # return with no data
        return {
            "lat": lat, # lat: the requested latitude
            "lng": lng, # lng: the requested longitude
            "radius": radius, # radius: the requested search radius
            "start": start, # start: the requested time range start in UNIX epoch milliseconds
            "end": end, # end: the requested time range end in UNIX epoch milliseconds
            "streetname": streetname, # streetname: derived from locationIQ, roughness only pertains to data collected on this road
            "num_points": 0, # num_points: the number of data points used in calculating roughness
            "points_variance": 0, # points_variance: the variance of the data points used in calculating roughness - higher = less reliable estimate
            "roughness": 0} # roughness: the roughness of the street, determined from all data points within the radius and time range
