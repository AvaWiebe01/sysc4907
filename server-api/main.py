from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
from sqlmodel import Field, SQLModel

app = FastAPI()

# Format for receiving condition data from RPi
# If this class is changed, the class "RoadData" in /rpi-api/apiRequests.py must also be updated.
class RoadData(BaseModel):
    x_coord: float
    y_coord: float
    roughness: float
    timestamp: float

# Root endpoint
@app.get("/")
def read_root():
    return {"Response": "You have reached RoadMonitor's API. Visit www.roadmonitor.online/docs/api for more information."}

# Send data to the database (used from RoadMonitor sensor device only)
@app.post("/data")
def post_road_data(data: RoadData):

    return {"Response": "Data received!"}

# Get conditions by coordinates (publicly available)
@app.get("/conditions/coords/")
def get_conditions_from_coordinates(x_coord: float, y_coord: float, radius: int = 200, start: float = 0, end: float = 0):

    # x_coord (latitude) must be within [-90, 90]
    if (x_coord < -90 or x_coord > 90):
        raise HTTPException(status_code=400, detail="x_coord (latitude) must be within the bounds [-90, 90].")

    # y_coord (longitude) must be within [-180, 180]
    if (y_coord < -180 or y_coord > 180):
        raise HTTPException(status_code=400, detail="y_coord (longitude) must be within the bounds [-180, 180].")

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

    return {"x_coord": x_coord, "y_coord": y_coord}


