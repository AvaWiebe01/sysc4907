docker build -t roadmonitor-api .
docker run -d -p 8000:8000 --restart unless-stopped --name roadmonitor_api roadmonitor-api:latest
