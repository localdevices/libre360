CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- It is useful to create the projects table first,
-- since it's primary key will be used in the photos table.
DROP TABLE IF EXISTS projects CASCADE;
CREATE TABLE IF NOT EXISTS projects
(
	projectid BIGINT GENERATED ALWAYS AS IDENTITY -- rather than serial, we will comply with the SQL standard
	,projectname text NOT NULL -- I assuming this is a project name and have renamed as such
	,root varchar (100) NOT NULL
	,n_cams integer NOT NULL
	,dt integer NOT NULL
	,PRIMARY KEY(projectid) 
	-- just to keep constraints to the end of the table creation process,we call out the primary key separately
);

-- Lists the current active project ID and that's it... .
DROP TABLE IF EXISTS project_active CASCADE;
CREATE TABLE IF NOT EXISTS projectactive
(
	projectid BIGINT
	,CONSTRAINT fk_projecta
        FOREIGN KEY(projectid) 
    	  REFERENCES projects(projectid)
	  ON DELETE CASCADE	
);

DROP TABLE IF EXISTS devices CASCADE;
CREATE TABLE IF NOT EXISTS devices
(
	deviceid BIGINT GENERATED ALWAYS AS IDENTITY
	,devicename text NOT NULL
	,status integer NOT NULL -- what are our status codes?
	,last_photo uuid
	,PRIMARY KEY(deviceid)
	,CONSTRAINT fk_photo -- add foreign key constraint referencing the project ID
         FOREIGN KEY(last_photo) 
    	   REFERENCES photos(photouuid)
	   ON DELETE CASCADE	
);

-- References the project and has a delete cascade, so if the project gets deleted, the photos get deleted
-- Yay! Tidy databases
DROP TABLE IF EXISTS photos CASCADE;
CREATE TABLE IF NOT EXISTS photos 
(
	photouuid uuid DEFAULT uuid_generate_v4 ()
	--,project varchar (50) NOT NULL -- Removing: this only belongs in the project file and will be joined using a foreign key
	,projectid INT
	,survey_run text NOT NULL
	,photo_filename text NOT NULL
	,photo BYTEA NOT NULL
	,thumbnail BYTEA
	,deviceid BIGINT
	,PRIMARY KEY(photouuid)
	,CONSTRAINT fk_project -- add foreign key constraint referencing the project ID
         FOREIGN KEY(projectid) 
    	   REFERENCES projects(projectid)
	   ON DELETE CASCADE
	,CONSTRAINT fk_devicephoto -- add foreign key constraint referencing the project ID
        FOREIGN KEY(deviceid) 
            REFERENCES devices(deviceid)
        ON DELETE CASCADE
);


