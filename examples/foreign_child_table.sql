-- Lay the ground work
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- This will need done each time a child is added
CREATE SERVER child_id_1_foreign_server
        FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host '<child_pi_1_hostname>', port '5432', dbname 'child_hostname_db');
        
CREATE FOREIGN TABLE child_id_1_foreign_table (
	photoid BIGINT
	,projectid BIGINT
	,survey_run text NOT NULL
	,device text NOT NULL
	,photo_filename text NOT NULL
	,photo BYTEA NOT NULL
	,thumbnail BYTEA
        ,child_pi_id text -- we need the child pi id in the table so we know where the data came from when we merge the tables together
)
        SERVER child_id_1_foreign_server
        OPTIONS (schema_name 'public', table_name 'cameras');

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
