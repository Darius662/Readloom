@echo off
echo Stopping any running containers...
docker compose down

echo Building and starting test container...
docker compose -f docker-compose.test.yml up --build

echo Done!
