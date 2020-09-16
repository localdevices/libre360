-- It is useful to create the projects table first,
-- since it's primary key will be used in the photos table.
DROP TABLE IF EXISTS projects CASCADE;
CREATE TABLE IF NOT EXISTS projects
(
	projectid INT GENERATED ALWAYS AS IDENTITY -- rather than serial, we will comply with the SQL standard
	,projectname text NOT NULL -- I assuming this is a project name and have renamed as such
	,root varchar (100) NOT NULL
	,n_cams integer NOT NULL
	,dt integer NOT NULL
	,PRIMARY KEY(projectid) 
	-- just to keep constraints to the end of the table creation process,we call out the primary key separately
);

DROP TABLE IF EXISTS photos;
CREATE TABLE IF NOT EXISTS photos 
(
	photoid INT GENERATED ALWAYS AS IDENTITY  --renamed: UUID usually is usually a universally unique identifier, and this is a serial
	--,project varchar (50) NOT NULL -- Removing: this only belongs in the project file and will be joined using a foreign key
	,projectid INT
	,survey_run VARCHAR (50) NOT NULL
	,device VARCHAR (50) NOT NULL
	,photo_filename VARCHAR (100) NOT NULL
	,photo_id VARCHAR (50) NOT NULL
	,photo BYTEA NOT NULL
	,thumbnail BYTEA
	,PRIMARY KEY(photoid)
	,CONSTRAINT fk_project -- add foreign key constraint referencing the project ID
         FOREIGN KEY(projectid) 
    	   REFERENCES projects(projectid)
	   ON DELETE CASCADE
);
	

CREATE TABLE IF NOT EXISTS device_status(
	deviceid 
	,devicename varchar (50) NOT NULL
	, status integer NOT NULL
	, last_photo varchar (100)
	);
