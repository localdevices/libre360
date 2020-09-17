import psycopg2
import numpy as np

# to not jeopardize Ivan's health, we use functions rather than classes to approah our databse

def create_table(cur, sql_command):
    """
    Create a new table using a sql command
    :param cur:
    :param sql_command:
    :return:
    """
    try:
        cur.execute(sql_command)
        cur.connection.commit()
    except:
        raise IOError('Table creation did not succeed.')

def create_table_photos(cur):
    """
    create table for storing photos
    :param cur:
    :return:
    """

    sql_command = """
    CREATE TABLE IF NOT EXISTS photos
    (photo_uuid uuid DEFAULT uuid_generate_v4 () 
    ,project_id INT
    ,survey_run text NOT NULL
    ,device_name text NOT NULL
    ,photo_filename text NOT NULL
    ,photo BYTEA NOT NULL
    ,thumbnail BYTEA
    ,PRIMARY KEY(photo_uuid)
    ,CONSTRAINT fk_project -- add foreign key constraint referencing the project ID
        FOREIGN KEY(project_id) 
            REFERENCES projects(project_id)
        ON DELETE CASCADE
    );

    """
    create_table(cur, sql_command)


def create_table_projects(cur):
    sql_command = """
    CREATE TABLE IF NOT EXISTS projects
    (
    project_id BIGINT GENERATED ALWAYS AS IDENTITY -- rather than serial, we will comply with the SQL standard
    ,project_name text NOT NULL -- I assuming this is a project name and have renamed as such
    ,n_cams integer NOT NULL
    ,dt BIGINT NOT NULL
    ,PRIMARY KEY(project_id)
    -- just to keep constraints to the end of the table creation process,we call out the primary key separately
    );
    """
    
    create_table(cur, sql_command)


def create_table_devices(cur):
    """
    creates a status table for the camera rig, always first drops the existing status table before creating a new one
    :param cur: cursor
    :return:
    """
    # first drop the existing status table
    drop_table(cur, 'devices')
    # then create a new one
    sql_command = """
    CREATE TABLE IF NOT EXISTS devices
    (
    device_id BIGINT GENERATED ALWAYS AS IDENTITY
    ,device_name text NOT NULL
    ,status integer NOT NULL -- what are our status codes?
    ,last_photo uuid
    ,PRIMARY KEY(device_id)
    ,CONSTRAINT fk_photo -- add foreign key constraint referencing the project ID
            FOREIGN KEY(last_photo) 
            REFERENCES photos(photo_uuid)
        ON DELETE CASCADE	
    );

    """
    create_table(cur, sql_command)


def delete_project(cur, project_name=None, project_id=None):
    if (project_name is None) and (project_id is None):
        raise ValueError('provide either a project_name or project_id')
    if not(project_name is None):
        sql_command = f"DELETE FROM projects WHERE project_name='{project_name}'"
    else:
        sql_command = f"DELETE FROM projects WHERE project_id={project_id}"

    cur.execute(sql_command)
    cur.connection.commit()


def drop_table(cur, table_name, cascade=False):
    """
    Drop a table from the database
    :param cur: cursor
    :param table_name: string - name of table (e.g. projects)
    :param cascade: bool (default False) - cascades to all other tables (yay! tidy databases)
    :return:
    """
    if cascade:
        sql_command = f"DROP TABLE IF EXISTS {table_name} CASCADE"
    else:
        sql_command = f"DROP TABLE IF EXISTS {table_name} "

    cur.execute(sql_command)
    cur.connection.commit()

def drop_photo(cur):
    # FIXME: implement
    raise NotImplementedError('Not yet implemented')


def insert(cur, sql_command):
    """
    Insert a new record using a sql command

    :param cur: cursor
    :param sql_command: command to create record with
    :return:
    """
    try:
        cur.execute(sql_command)
        cur.connection.commit()
    except:
        raise IOError(f'Insertion command {sql_command} failed')


def insert_device(cur, device_name, status):
    """
    insert a new device in table (leave out last_photo since it is not available yet).
    :param cur: cursor
    :param device_name: string - id of device (auto-generated on child side)
    :param status: int - status of device, each int has a specific meaning
    :return:
    """
    sql_command = f"INSERT INTO devices(device_name, status) VALUES ('{device_name}', {status});"
    insert(cur, sql_command)


def insert_project(cur, project_name, n_cams, dt):
    """

    :param cur: cursor
    :param project_name: str - (user defined) name of project (note: id is provided automatically)
    :param n_cams: int - nr of cameras in project
    :param dt: int - time interval between photos
    :return:
    """
    sql_command = f"""
    INSERT INTO projects
    (
    project_name
    ,n_cams
    ,dt
    ) VALUES
    (
    '{project_name}'
    ,{n_cams}
    ,{dt}
    );
    """
    insert(cur, sql_command)

def insert_photo(cur, project_id, survey_run, device_name, fn, photo, thumb):
    """

    :param cur: cursor
    :param project_id: int - project id
    :param survey_run: string - id of survey within project
    :param device_name: string - id of device
    :param folder: string - folder containing photos on child
    :param fn: string - filename
    :param photo: numpy-array with photo TODO: check how photos are returned and revise if needed
    :param thumb: numpy-array with thumbnail TODO: check how thumbnails are returned and revise if needed
    :return:
    """
    try:
        _photo = psycopg2.Binary(photo)
        _thumb = psycopg2.Binary(thumb)
    except:
        raise ValueError('photo or thumbnail are not numpy-arrays')
    sql_command = f"""
    INSERT INTO photos
    (
    project_id
    ,survey_run
    ,device_name
    ,photo_filename
    ,photo
    ,thumbnail
    ) VALUES
    (
    '{project_id}'
    ,'{survey_run}'
    ,'{device_name}'
    ,'{fn}'
    ,{_photo}
    ,{_thumb}
    );"""
    insert(cur, sql_command)


def is_table(cur, table_name):
    """
    Simple check to see if table exists or not
    :param cur: cursor
    :param table_name: str - name of table
    :return: True/False
    """
    sql_command = f"SELECT EXISTS ( SELECT FROM information_schema.tables WHERE table_name = '{table_name}' );"
    cur.execute(sql_command)
    return cur.fetchall()[0][0]


def is_device(cur, device_name):
    """
    Simple check to see if device exists
    :param cur: cursor
    :param device_name: str - name of device
    :return: True/False
    """
    cur.execute(f"SELECT EXISTS ( SELECT 1 FROM devices WHERE device_name='{device_name}')")
    return cur.fetchall()[0][0]


def query_photos(cur, project_id=None):
    """
    queries all photos for a given project name
    :param cur: cursor
    :param project_id: int - project id
    :return: list of results
    """
    if project_id is None:
        raise ValueError('provide a project_id')
    sql_command = f"SELECT * FROM photos WHERE project_id={project_id}"

    cur.execute(sql_command)
    return cur.fetchall()


def query_photos_survey(cur, project_id, survey_run):
    # FIXME: prepare this function
    raise NotImplemented("Function needs to be prepared")


def query_projects(cur):
    """
    returns all project names available in table "photos" as flattened list
    :param cur: cursor
    :return: list of strings
    """
    cur.execute("SELECT DISTINCT(project_name) FROM projects")
    return [x[0] for x in cur.fetchall()]


def update_device(cur, device_name, status, last_photo=""):
    """

    :param cur: cursor
    :param device_name: str - id of device
    :param status: int - status indicator
    :param last_photo: str - uuid of last photo (error returned if uuid does not exist in database)
    :return:
    """
    if not(is_device(cur, device_name)):
        raise KeyError(f'device "{device_name}" does not exist in table "device_status"')
    sql_command = f"UPDATE devices SET status={status}, last_photo='{last_photo}' WHERE device_name='{device_name}'"
    cur.execute(sql_command)


con = psycopg2.connect('dbname=odm360 user=odm360 host=localhost password=zanzibar')
cur = con.cursor()

# DO SOMETHING
# We'll start with a clean slate
if is_table(cur, 'devices'):
    drop_table(cur, 'devices')
if is_table(cur, 'photos'):
    drop_table(cur, 'photos')
if is_table(cur, 'projects'):
    drop_table(cur, 'projects')
# print(is_table(cur, 'photos'))

# setup project and photos table
create_table_projects(cur)
create_table_photos(cur)

# try to add a photo in a non-existing project (should fail! It did so it is commented below)
# insert_photo(cur, 0, 'today', '1', '/here/is/something/DCIM_12345.JPG', np.random.rand(24, 24),
#              np.random.rand(24, 24))

# now create two projects
insert_project(cur, 'Dar', 7, 5)
insert_project(cur, 'Mwanza', 7, 2)
cur.execute("SELECT * FROM projects")
print(f'Two projects should be setup, with a unique ID {cur.fetchall()}')

# try adding a photo from non-existing device, should fail
print(f'Only the names of the projects, looks like: {query_projects(cur)}')

create_table_devices(cur)
insert_device(cur, 'some_camera1', 0)
insert_device(cur, 'another_camera1', 0)
#
cur.execute("SELECT * FROM devices")
print(f'We have inserted two devices without any status: {cur.fetchall()}')

# now add photos for the given devices
insert_photo(cur, 1, '2020-09-17', 'some_camera1', '/some/test/to/DCIM12345.JPG',np.random.rand(24, 24), np.random.rand(24, 24))
insert_photo(cur, 1, '2020-09-17', 'some_camera1', '/some/test/to/DCIM67890.JPG',np.random.rand(24, 24), np.random.rand(24, 24))
insert_photo(cur, 2, '2020-09-17', 'another_camera1', '/some/test/to/DCIM12345.JPG',np.random.rand(24, 24), np.random.rand(24, 24))
insert_photo(cur, 2, '2020-09-17', 'another_camera1', '/some/test/to/DCIM12345.JPG',np.random.rand(24, 24), np.random.rand(24, 24))
cur.execute("SELECT * FROM photos")
print(f'For both projects, we have inserted 2 (total 4) photos: {cur.fetchall()}')
last_photo = query_photos(cur, 1)[0][0]
print(f'The uuid of the last photo is {last_photo}')
update_device(cur, 'some_camera1', 99, last_photo=last_photo) # last_photo is the uuid gibberish of the last photo id
cur.execute("SELECT * FROM devices")
print(f'After updating status of "some_camera1", status is {cur.fetchall()}')

delete_project(cur, project_id=1)
# all above photos for project Dar (numbered 1) should now also be removed! Check below
cur.execute("SELECT * FROM photos")
print(f'We have now deleted everything for project_id 1 (name Dar). We now only have these photos: {cur.fetchall()}')

cur.close()
con.close()
