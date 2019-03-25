## Setup of Raspberry Pi
1. Download the the latest version of Raspbian from the Raspberry homepage: https://www.raspberrypi.org/downloads/raspbian/ (current version Stretch from April 2018).
2. Using an image writing tool, like Etcher, write an image of the OS on a microSD card (32GB recommended).
3. Install PostgreSQL as database, following this tutorial: https://opensource.com/article/17/10/set-postgres-database-your-raspberry-pi
4. Install Docker CE (refer to https://doc.docker.com/install/linux/docker-ce/debian/#install-docker-ce). NOTE: Raspberry Pi 3 has *armhf* architecture:
5. Manage docker as non-root user: https://docs.docker.com/install/linux/linux-postinstall/

## Setup of PostgreSQL database
1. When PostgreSQL has been installed successfully, switch to user postgres typing: `sudo su postgres`
2. Create *iot* database: `psql create database iot;`
3. Create tables:
```
CREATE TABLE sensor(
    sensor_id serial PRIMARY KEY,
    name text UNIQUE NOT NULL,
    description text
);
CREATE TABLE data(
    record_id serial PRIMARY KEY,
    value REAL NOT NULL,
    sensor_id integer NOT NULL,
    created_on TIMESTAMP NOT NULL,
    CONSTRAINT data_sensor_id_fkey FOREIGN KEY (sensor_id)
        REFERENCES sensor (sensor_id) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION
);
```

## Important Commands for psql Tool
* `\l` : list all available databases
* `\dt` : list all columns of a specific database
* `\connect` : connect to different database
* For further reference see: https://www.postgresql.org/docs/current/static/app-psql.html