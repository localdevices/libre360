CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- drop any tables if they exist
DROP TABLE IF EXISTS photos_child;

-- create photos table (dependent on projects)
CREATE TABLE IF NOT EXISTS photos_child
(
    photo_uuid uuid DEFAULT uuid_generate_v4 ()
    ,project_id INT
    ,survey_run text NOT NULL
    ,device_name text NOT NULL
    ,photo_filename text NOT NULL
    ,photo BYTEA NOT NULL
    ,thumbnail BYTEA
    ,device_id BIGINT
    ,PRIMARY KEY(photo_uuid)
--    ,CONSTRAINT fk_project -- add foreign key constraint referencing the project ID
--        FOREIGN KEY(project_id)
--            REFERENCES projects(project_id)
--        ON DELETE CASCADE
);

ALTER TABLE photos_child OWNER TO odm360;

