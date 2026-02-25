docker stop roadmonitor_api 2>/dev/null || true
docker rm -f roadmonitor_api 2>/dev/null || true

docker build -t roadmonitor-api .
docker volume create persistent-database
docker run -d \
	--rm \
	--mount type=volume,src=persistent-database,dst=/container/api/database \
	-p 8000:8000 \
	--name roadmonitor_api \
	roadmonitor-api:latest
