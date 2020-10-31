-- Lay the ground work
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- This will need done each time a child is added
CREATE SERVER pi1_foreign_server
        FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host '<child_pi_1_hostname>', port '5432', dbname 'child_hostname_db');

-- not sure if needed
CREATE USER MAPPING
    FOR odm360
 SERVER pi1_foreign_server
OPTIONS (user 'odm360', password 'zanzibar');

CREATE FOREIGN TABLE pi1_foreign_table (
	photo_uuid uuid
	,project_id BIGINT
	,survey_run text NOT NULL
	,device_name text NOT NULL
	,photo_filename text NOT NULL
	,photo BYTEA
	,thumbnail BYTEA
	,device_uuid uuid
	)
        SERVER pi1_foreign_server
        OPTIONS (schema_name 'public', table_name 'photos');

-- This will be needed every time a child is detected removed
DROP SERVER IF EXISTS child_id_1_foreign_server;        

-- Create aggregate view of all child tables
-- This will need modified each time a child is added or removed
CREATE OR REPLACE VIEW photos
SELECT * FROM child_id_1_foreign_table
    UNION
SELECT * FROM child_id_2_foreign_table
     UNION
SELECT * FROM child_id_3_foreign_table;
