-- Diff code generated with pgModeler (PostgreSQL Database Modeler)
-- pgModeler version: 0.9.1-beta
-- Diff date: 2018-09-08 13:07:56
-- Source model: iot
-- Database: iot
-- PostgreSQL version: 9.5

-- [ Diff summary ]
-- Dropped objects: 5
-- Created objects: 4
-- Changed objects: 2
-- Truncated tables: 0

SET search_path=public,pg_catalog,iot;
-- ddl-end --


-- [ Dropped objects ] --
ALTER TABLE public.data DROP CONSTRAINT IF EXISTS sensors_fk CASCADE;
-- ddl-end --
ALTER TABLE public.sensors DROP CONSTRAINT IF EXISTS sensor_type_fk CASCADE;
-- ddl-end --
DROP SCHEMA IF EXISTS iot CASCADE;
-- ddl-end --
DROP TABLE IF EXISTS public.sensors CASCADE;
-- ddl-end --
DROP SEQUENCE IF EXISTS public.sensors_id_seq CASCADE;
-- ddl-end --
ALTER TABLE public.data DROP COLUMN IF EXISTS id_sensors CASCADE;
-- ddl-end --


-- [ Created objects ] --
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

-- object: id_sensor | type: COLUMN --
-- ALTER TABLE public.data DROP COLUMN IF EXISTS id_sensor CASCADE;
ALTER TABLE public.data ADD COLUMN id_sensor integer NOT NULL;
-- ddl-end --




-- [ Changed objects ] --
ALTER TABLE public.data ALTER COLUMN id TYPE integer;
-- ddl-end --
ALTER TABLE public.data ALTER COLUMN id SET DEFAULT nextval('public.data_id_seq'::regclass);
-- ddl-end --
ALTER TABLE public.sensor_type ALTER COLUMN id TYPE integer;
-- ddl-end --
ALTER TABLE public.sensor_type ALTER COLUMN id SET DEFAULT nextval('public.sensor_type_id_seq'::regclass);
-- ddl-end --


-- [ Created foreign keys ] --
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

