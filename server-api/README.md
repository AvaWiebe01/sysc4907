Run "docker compose up -d" to deploy the RoadMonitor API with all required containers.

The API will be run inside a Docker container using FastAPI.

A separate Nginx container will be created, listening to port 8000.
Nginx forwards HTTPS requests on port 8000 to the API.
