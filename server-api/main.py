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
    iri: float

# Root (default) endpoint
@app.get("/")
def read_root():
    return {"Response": "You have reached RoadMonitor's API. Visit www.roadmonitor.online/docs/api for more information."}

# Send data to the database
@app.post("/data")
def post_road_data(data: RoadData):
    return {"Response": "Data received!"}

# Get conditions by coordinates
@app.get("/conditions/coords/{x_coord}/{y_coord}")
def get_conditions_from_coordinates(x_coord: float, y_coord: float):
    return {"x_coord": x_coord, "y_coord": y_coord}

# Get conditions by street name
@app.get("/conditions/streetname/{street_name}")
def get_conditions_from_street_name(street_name: str):
    return {"street_name": street_name}

