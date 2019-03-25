-- Database generated with pgModeler (PostgreSQL Database Modeler).
-- pgModeler  version: 0.9.1-beta
-- PostgreSQL version: 10.0
-- Project Site: pgmodeler.io
-- Model Author: ---


-- Database creation must be done outside an multicommand file.
-- These commands were put in this file only for convenience.
-- -- object: iot | type: DATABASE --
-- -- DROP DATABASE IF EXISTS iot;
-- CREATE DATABASE iot
-- 	OWNER = postgres
-- ;
-- -- ddl-end --
-- 

-- object: postgis | type: EXTENSION --
-- DROP EXTENSION IF EXISTS postgis CASCADE;
CREATE EXTENSION postgis
      WITH SCHEMA public;
-- ddl-end --

-- object: public.sensor | type: TABLE --
-- DROP TABLE IF EXISTS public.sensor CASCADE;
CREATE TABLE public.sensor(
	id serial NOT NULL,
	name text,
	note text,
	coordinates geography(POINT),
	id_sensor_type integer NOT NULL,
	CONSTRAINT sensors_pk PRIMARY KEY (id)

);
-- ddl-end --

-- object: public.data | type: TABLE --
-- DROP TABLE IF EXISTS public.data CASCADE;
CREATE TABLE public.data(
	id serial NOT NULL,
	value jsonb,
	"timestamp" timestamp NOT NULL,
	created timestamp NOT NULL,
	id_sensor integer NOT NULL,
	CONSTRAINT data_pk PRIMARY KEY (id)

);
-- ddl-end --

-- object: public.sensor_type | type: TABLE --
-- DROP TABLE IF EXISTS public.sensor_type CASCADE;
CREATE TABLE public.sensor_type(
	id serial NOT NULL,
	name text,
	typedef jsonb,
	CONSTRAINT sensor_type_pk PRIMARY KEY (id)

);
-- ddl-end --

-- object: sensor_type_fk | type: CONSTRAINT --
-- ALTER TABLE public.sensor DROP CONSTRAINT IF EXISTS sensor_type_fk CASCADE;
ALTER TABLE public.sensor ADD CONSTRAINT sensor_type_fk FOREIGN KEY (id_sensor_type)
REFERENCES public.sensor_type (id) MATCH FULL
ON DELETE CASCADE ON UPDATE CASCADE;
-- ddl-end --

-- object: sensor_fk | type: CONSTRAINT --
-- ALTER TABLE public.data DROP CONSTRAINT IF EXISTS sensor_fk CASCADE;
ALTER TABLE public.data ADD CONSTRAINT sensor_fk FOREIGN KEY (id_sensor)
REFERENCES public.sensor (id) MATCH FULL
ON DELETE CASCADE ON UPDATE CASCADE;
-- ddl-end --


