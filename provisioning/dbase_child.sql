CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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

-- create photos table (dependent on projects)
CREATE TABLE IF NOT EXISTS photos
(
    photo_uuid uuid DEFAULT uuid_generate_v4 ()
    ,project_id INT
    ,survey_run text NOT NULL
    ,device_name text NOT NULL
    ,photo_filename text NOT NULL
    ,photo BYTEA NOT NULL
    ,thumbnail BYTEA
    ,device_uuid uuid
    ,PRIMARY KEY(photo_uuid)
);


ALTER TABLE device OWNER TO odm360;
ALTER TABLE photos OWNER TO odm360;
-- Now add one device
INSERT INTO device (name) VALUES ('picam');
-- And that's it! Only one device entry ever!

