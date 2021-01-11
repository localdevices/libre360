CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- drop any tables if they exist
DROP TABLE IF EXISTS project_active CASCADE;
DROP TABLE IF EXISTS devices CASCADE;
DROP TABLE IF EXISTS surveys CASCADE;

--DROP TABLE IF EXISTS photos CASCADE;
DROP TABLE IF EXISTS projects;

-- create projects table (independent)
CREATE TABLE IF NOT EXISTS projects
(
    project_id BIGINT GENERATED ALWAYS AS IDENTITY -- rather than serial, we will comply with the SQL standard
    ,project_name text NOT NULL -- I assuming this is a project name and have renamed as such
    ,n_cams integer NOT NULL
    ,dt BIGINT NOT NULL
    ,PRIMARY KEY(project_id)
    -- just to keep constraints to the end of the table creation process,we call out the primary key separately
);

CREATE TABLE IF NOT EXISTS surveys
(
    survey_run text
    ,project_id INT
    ,CONSTRAINT fk_project -- add foreign key constraint referencing the project ID
        FOREIGN KEY(project_id)
            REFERENCES projects(project_id)
        ON DELETE CASCADE
);
-- create photos table (dependent on projects)
--CREATE TABLE IF NOT EXISTS photos
--(
--    photo_uuid uuid DEFAULT uuid_generate_v4 ()
--    ,project_id INT
--    ,survey_run text NOT NULL
--    ,device_name text NOT NULL
--    ,photo_filename text NOT NULL
--    ,photo BYTEA
--    ,thumbnail BYTEA
--    ,device_uuid uuid
--    ,PRIMARY KEY(photo_uuid)
--    ,CONSTRAINT fk_project -- add foreign key constraint referencing the project ID
--        FOREIGN KEY(project_id)
--            REFERENCES projects(project_id)
--        ON DELETE CASCADE
--);

-- Create a table for just the project that is currently active, only holding the project_id, status and start time
-- for image capturing
CREATE TABLE IF NOT EXISTS project_active
(
    project_id BIGINT
    ,status integer -- 0: waiting for cams to get ready, 1: idle, 2: ready, 3: capture, 9: broken (if one of devices fails)
    ,start_time timestamp --
    ,CONSTRAINT fk_projects
        FOREIGN KEY(project_id)
          REFERENCES projects(project_id)
      ON DELETE CASCADE
);

-- create a status table for the camera rig
CREATE TABLE IF NOT EXISTS devices
(
device_uuid uuid  -- GENERATED ALWAYS AS IDENTITY
,device_name text -- NOT NULL
,status integer NOT NULL -- what are our status codes?
,req_time double precision
,last_photo uuid
,PRIMARY KEY(device_uuid)
--,CONSTRAINT fk_photo -- add foreign key constraint referencing the project ID
--        FOREIGN KEY(last_photo)
--        REFERENCES photos(photo_uuid)
--    ON DELETE CASCADE
);

ALTER TABLE projects OWNER TO odm360;
ALTER TABLE surveys OWNER TO odm360;
--ALTER TABLE photos OWNER TO odm360;
ALTER TABLE project_active OWNER TO odm360;
ALTER TABLE devices OWNER TO odm360;

