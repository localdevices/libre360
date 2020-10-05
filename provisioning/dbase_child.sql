CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "multicorn";

-- drop any tables if they exist
DROP TABLE IF EXISTS device;
DROP TABLE IF EXISTS photos;

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
CREATE FOREIGN TABLE IF NOT EXISTS photos
(
    device_uuid UUID
    ,project_id INT
    ,survey_run text NOT NULL
    ,device_name text NOT NULL
    ,PRIMARY KEY (photo_filename) UUID NOT NULL
    ,photo BYTEA NOT NULL
) server filesystem_srv options(
    root_dir    '/home/pi/odm360/piimage',
    {device_uuid}/{project_id}/{survey_run}/{device_name}/{photo_filename}.jpg
    ,photo 'content'
);

ALTER TABLE device OWNER TO odm360;
ALTER TABLE photos OWNER TO odm360;
-- Now add one device
INSERT INTO device (name) VALUES ('picam');
-- And that's it! Only one device entry ever!
