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

# Backend

As of now there are hundrets of possibilities to use in IoT for the backend (server side) and/ or frontend (client side). In the following we want to describe what we have choosen for the practical lab course and why we choose what we choose.

## Apache/ Nginx

Start Apache2 server
```
$ sudo /etc/init.d/apache2 restart
```

Stop Apache2 server
```
$ sudo /etc/init.d/apache2 stop
```

Create symlink for domain
```
sudo ln -s /etc/apache2/sites-available/example.com /etc/apache2/sites-enabled/example.com
```

## PostgreSQL

Backup database
```
docker exec -t -u postgres your-db-container pg_dumpall -c > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql
```

Restore database or apply migrations/ database changes via sql file
```
cat your_dump.sql | docker exec -i your-db-container psql -Upostgres
```

## Tornado

## Docker

psql into docker container to do queries
```
docker exec -ti NAME_OF_CONTAINER psql -U YOUR_POSTGRES_USERNAME
```

# Type Definitions defined in Frontend

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
![image](https://user-images.githubusercontent.com/11216482/54961601-b181b300-4f61-11e9-8ba4-a136f92a9383.png)
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
![image](https://user-images.githubusercontent.com/11216482/54961626-c9593700-4f61-11e9-94d8-3de0302a789a.png)
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
![image](https://user-images.githubusercontent.com/11216482/54961644-daa24380-4f61-11e9-9009-403fd6437cf2.png)

```
    ...
    "alarm": {
        "type": "Alarm",
        "label": "Calendar Week Alarm"
    }
    ...
```

### Dropdown Selection
![image](https://user-images.githubusercontent.com/11216482/54961661-e857c900-4f61-11e9-9591-0192d145f769.png)
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
![image](https://user-images.githubusercontent.com/11216482/54961676-f574b800-4f61-11e9-9edb-e9e1b37040f7.png)
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
![image](https://user-images.githubusercontent.com/11216482/54961689-ff96b680-4f61-11e9-9924-1a3ccbc49b6b.png)
```
    ...
    "battery": {
        "type": "Battery"
    }
    ...
```

### Single Value with zoomable plot
![image](https://user-images.githubusercontent.com/11216482/54961706-0f15ff80-4f62-11e9-8202-de9b3206b030.png)
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

