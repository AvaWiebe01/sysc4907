from typing import Union
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Depends
import pydantic
import sqlmodel
import requests
import json

### These constants must be the same as 
IQ_SEARCH_RADIUS = 100
UNNAMED_ROAD_STRING = "Unnamed"
IQ_TOKEN = "pk.e27e659d87b04fd8f55014c2e2e82ccc"; # locationIQ API token

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
    url = (f"https://us1.locationiq.com/v1/nearest/driving/"
           f"{data.lng:.7f},"
           f"{data.lat:.7f}"
           f"?radiuses={IQ_SEARCH_RADIUS}"
           f"&key={IQ_TOKEN}"
           f"&number=1")
    print(url)
    
    try:
        resp = requests.get(url)
        resp_dict = resp.json()
        datapoint_streetname = resp_dict["waypoints"][0]["name"] if (resp_dict["waypoints"][0]["name"] != "") else UNNAMED_ROAD_STRING
        print("New point streetname:", datapoint_streetname)
    except:
        print("No nearby road found, data rejected")
        return {"Response": "No nearby road found, data rejected"}

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

    # select specified data from RoadMonitor database
    streetname = None
    num_points = None
    points_variance = None
    roughness = None

    # return the requested data to user
        # lat: the requested latitude
        # lng: the requested longitude
        # radius: the requested search radius
        # start: the requested time range start in UNIX epoch milliseconds
        # end: the requested time range end in UNIX epoch milliseconds
        # streetname: derived from locationIQ, roughness only pertains to data collected on this road
        # num_points: the number of data points used in calculating roughness
        # points_variance: the variance of the data points used in calculating roughness - higher = less reliable estimate
        # roughness: the roughness of the street, determined from all data points within the radius and time range
    return {
        "lat": lat,
        "lng": lng,
        "radius": radius,
        "start": start,
        "end": end,
        "streetname": streetname,
        "num_points": num_points,
        "points_variance": points_variance,
        "roughness": roughness}


