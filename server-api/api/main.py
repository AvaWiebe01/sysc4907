from typing import Union
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Depends
import pydantic
import sqlmodel

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

# Create API instance
app = FastAPI()

# Start the database engine instance (creates database file if it doesn't exist)
sqlite_file_name = "roadmonitor-data-points.db"
sqlite_url = f"sqlite:///database/{sqlite_file_name}"
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

    # data point is validated by the pydantic model
    # Store received point in server's local database
    with sqlmodel.Session(engine) as session:
        new_datapoint = DataPoint(lat = data.lat, lng = data.lng, roughness = data.roughness, timestamp = data.timestamp)
        session.add(new_datapoint)
        session.commit()
        print("New Point ID:", new_datapoint.id)

    return {"Response": "Data received!"}

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

    # No date range if start == end == 0
    if (start == 0 and end == 0):
        has_range = False
    else: 
        has_range = True

    return {"lat": lat, "lng": lng}


