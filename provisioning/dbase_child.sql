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
CREATE SERVER filesystem_srv foreign data wrapper multicorn options (
    wrapper 'multicorn.fsfdw.FilesystemFdw'
);

-- create photos table (dependent on projects)
CREATE FOREIGN TABLE photos_child (
    device_uuid UUID
    ,project_id INT
    ,survey_run text
    ,photo_filename text
    ,photo bytea
    ,filename character varying
) server filesystem_srv options(
    root_dir    '/home/pi/piimages'
    ,pattern '{device_uuid}/{project_id}/{survey_run}/{photo_filename}.jpg'
    ,content_column 'photo'
    ,filename_column 'filename'
);


ALTER TABLE device OWNER TO odm360;
ALTER TABLE photos_child OWNER TO odm360;
-- Now add one device
INSERT INTO device (name) VALUES ('picam');
-- And that's it! Only one device entry ever!

