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


# Type Definitions

## Sending JSON Data
The following code block is an example of setting the battery to 30% at a specified timestamp.
```
{
    "value": {
        "battery" : 0.3
    },
    "timestamp" : "2018-08-22 12:32:30.495815"
}
```
Timestamps should be in a standardized format which is understandable by PostgreSQL like the _ISO 8601_ format  
`"yyyy-MM-dd'T'HH:mm:ss.SSS'Z"`

## Example type definition
### Text

```
    ...
    "text": {
        "type": "Text",
        "label": "Test",
        "placeholder": "Bla"
    }
    ...
```

You can use the `inputType` to change the input type of the input field between `text`(default), `number` and `textarea`.
```
    ...
    "text2" : {
        "type": "Text"
        "label": "Nummer Eingabe 2"
        "inputType": "number"
    }
    ...
```
### Date and Time picker

```
    ...
    "time": {
        "type": "DateTimePicker"
    }
    ...
```

```
    ...
    "time": {
        "type": "DateTimePicker",
        "label": "Zeit",
        "dateFormat": "LLL",
        "timeFormat": "HH:mm",
        "timeIntervals": 15,
        "showTimeSelect": true,
        "showTimeSelectOnly": true
    }
    ...
```


### Calendar Week

```
    ...
    "alarm": {
        "type": "Alarm",
        "label": "Calendar Week Alarm"
    }
    ...
```

### Dropdown Selection

```
    ...
    "select": {
        "type": "Select",
        "label": "Dropdown",
        "options": [
            {
                "label": "Chocolate",
                "value": "chocolate"
            },
            {
                "label": "Vanilla",
                "value": "vanilla"
            },
            {
                "label": "Strawberry",
                "value": "strawberry"
            }
        ]
    }
    ...
```

### Switch

```
    ...
    "switch": {
        "type": "Boolean",
        "style": "ParkingLot"
    }
    ...
```

```
    ...
    "switch2": {
        "type": "Boolean",
        "label": "Test",
        "style": "Switch"
    }
    ...
```

```
    ...
    "switch3": {
        "type": "Boolean",
        "style": "Switch",
        "isDisabled": true
    }
    ...
```

### Battery level

```
    ...
    "battery": {
        "type": "Battery"
    }
    ...
```

### Single Value with zoomable plot

```
    ...
    "temperature": {
        "type": "ValuePlot",
        "unit": "°C",
        "label": "Temperature",
        "FlexibleWidthXYPlot": {
            "xType": "time",
            "height": 300,
            "yDomain": [
                0,
                40
            ]
        }
    }
    ...
```

