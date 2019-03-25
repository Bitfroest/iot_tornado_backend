# iot_tornado_backend
Tornado Backend for a simple websocket based IoT platform. Implemented as part of the lab course IoT 2 - Aufbau eines Sensornetzwerks at TUM.

# Installation instructions to use IoT Tornado Server

## Get latest version of iot git repository
```
git clone https://github.com/Bitfroest/iot_tornado_backend.git
git submodule update --recursive --remote
```

## Install Node.js and npm
```
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## Build static HTML file
Go into the frontend folder and execute
```
npm install
```
And
```
npm run build
```
Copy the build folder into the backendfolder
```
cp -r build ../backend/
```

## Get Docker
Install Docker CE from https://docs.docker.com/install/

## Download Docker image of the PostgreSQL database
When the image cannot be found locally, docker automatically searches in the Docker repository.
```
docker run --name station-postgres -e POSTGRES_PASSWORD=<secret_password> -e POSTGRES_DB=iot -d postgres
```
Replace '<secret_password>' with your own password or your set it to postgres (Note: Remember the password as it is needed later for the 'database.ini' file)

Create database by executing the sql file into the running postgres docker container:
```
cat iot_database.sql | docker exec -i station-postgres psql -U postgres
```

## Build a Docker image of the Tornado Web Server
Go to the 'Team Station/backend' folder and copy 'database.template.ini' and rename it to 'database.ini' (Update the line *password* if you have set a password different from *postgres*)..
Execute the docker command within the *backend* folder:
```
docker build -t station-python
```
Run the container:
```
docker run -it -d --name station-python --link station-postgres:postgres -v "$PWD":/usr/src/app -p 80:8888 station-python
```

## Useful docker commands
List all running docker containers:
```
docker container ls
docker ps --all
```
Start, Restart, Stop, Remove Docker Container
```
//start
docker start <container-name>
//restart
docker restart <container-name>
//stop
docker stop <container-name>
//remove
docker rm <container-name>
```
Type the IP address of the raspberry Pi in your browser and check if the server responds
(*Note*: You need to be in the same network)

