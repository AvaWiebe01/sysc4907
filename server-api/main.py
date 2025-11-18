from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class RoadData(BaseModel):
    x_coord: float
    y_coord: float
    street_name: str
    iri: float

# Test endpoint
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/data")
def post_road_data(data: RoadData):
    return {"condition": "Data received!"}

# Get conditions by coordinates
@app.get("/conditions/coords/{x_coord}/{y_coord}")
def get_conditions_from_coordinates(x_coord: float, y_coord: float):
    return {"x_coord": x_coord, "y_coord": y_coord}

# Get conditions by street name
@app.get("/conditions/streetname/{street_name}")
def get_conditions_from_street_name(street_name: str):
    return {"street_name": street_name}

