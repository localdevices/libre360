CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgres_fdw;
--CREATE EXTENSION IF NOT EXISTS "multicorn";

-- drop any tables if they exist
DROP TABLE IF EXISTS device;
DROP TABLE IF EXISTS photos_child;

-- create device table (only one col and one row)
CREATE TABLE IF NOT EXISTS device
(
    device_uuid uuid DEFAULT uuid_generate_v4 ()
    ,name text NOT NULL
    ,PRIMARY KEY(device_uuid)
);

-- add file system foreign data wrapper
--CREATE SERVER filesystem_srv foreign data wrapper multicorn options (
--    wrapper 'multicorn.fsfdw.FilesystemFdw'
--);

-- create photos table (dependent on projects)
CREATE TABLE photos_child (
    photo_uuid uuid
    ,project_id int
    ,survey_run text
    ,device_uuid UUID
    ,device_name text
    ,photo_filename text
    ,ts TIMESTAMP
    ,photo bytea
);
ALTER TABLE device OWNER TO odm360;
ALTER TABLE photos_child OWNER TO odm360;
-- Now add one device
INSERT INTO device (name) VALUES ('picam');
-- And that's it! Only one device entry ever!
-- make odm360 superuser so that pg_read_binary_file can be used (ugh! change with psycopg3 if it comes available)
ALTER USER odm360 WITH SUPERUSER;

