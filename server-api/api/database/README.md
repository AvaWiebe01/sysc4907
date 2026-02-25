This directory is used for storing RoadMonitor's database.
When the Docker container is created, this directory is mounted as a volume, to let the data persist between containers.
The database will be stored in docker's managed volumes location - this directory only serves to explain the database functionality. 
/server-api/api/main.py contains the functionality for the database.
