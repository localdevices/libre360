import psycopg2
import numpy as np


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
    sql_command = "CREATE TABLE photos(uuid serial PRIMARY KEY, project varchar (50) NOT NULL, survey_run VARCHAR (50) NOT NULL, device VARCHAR (50) NOT NULL, photo_filename VARCHAR (100) NOT NULL, photo_id VARCHAR (50) NOT NULL, photo BYTEA, thumbnail BYTEA)"
    create_table(cur, sql_command)


def create_table_projects(cur):
    sql_command = "CREATE TABLE projects(number serial PRIMARY KEY, project varchar (50) NOT NULL, root varchar (100) NOT NULL, n_cams integer NOT NULL, dt integer NOT NULL)"
    create_table(cur, sql_command)


def create_table_status(cur):
    """
    creates a status table for the camera rig
    :param cur: cursor
    :return:
    """
    sql_command = "CREATE TABLE device_status(device varchar (50) NOT NULL, status integer NOT NULL, last_photo varchar (100))"
    create_table(cur, sql_command)

def drop_table(cur, table_name):
    """
    Drop a table from the database
    :param cur: cursor
    :param table_name: string - name of table (e.g. projects)
    :return:
    """
    sql_command = f"DROP table {table_name}"
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

def insert_device(cur, device, status):
    """
    insert a new device in table (leave out last_photo since it is not available yet).
    :param cur: cursor
    :param device: string - id of device
    :param status: int - status of device, each int has a specific meaning
    :return:
    """
    sql_command = f"INSERT INTO device_status(device, status) VALUES ('{device}', {status});"
    insert(cur, sql_command)


def insert_photo(cur, project, survey, device, folder, fn, photo, thumb):
    """

    :param cur: cursor
    :param project: string - project name
    :param survey: string - id of survey within project
    :param device: string - id of device
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
    sql_command = f"INSERT INTO photos(project, survey_run, device, photo_filename, photo_id, photo, thumbnail) VALUES ('{project}', '{survey}', '{device}', '{folder}', '{fn}', {_photo}, {_thumb});"
    insert(cur, sql_command)


def is_table(cur, table_name):
    sql_command = f"SELECT EXISTS ( SELECT FROM information_schema.tables WHERE table_name = '{table_name}' );"
    cur.execute(sql_command)
    return cur.fetchall()[0][0]


def query_photos(cur, project):
    """
    queries all photos for a given project name
    :param cur: cursor
    :param project: string - project name
    :return: list of results
    """
    sql_command = f"SELECT * FROM photos WHERE project='{project}'"
    cur.execute(sql_command)
    return cur.fetchall()


def query_photos_survey(cur, project, survey):
    # FIXME: prepare this function
    raise NotImplemented("Function needs to be prepared")


def query_projects(cur):
    """
    returns all project names available in table "photos" as flattened list
    :param cur: cursor
    :return: list of strings
    """
    cur.execute("SELECT DISTINCT(project) FROM photos")
    return [x[0] for x in cur.fetchall()]

def update_device(cur, device, status, last_photo=""):
    """

    :param cur: cursor
    :param device: str - id of device
    :param status: int - status indicator
    :param last_photo: str - local filename of last photo
    :param last_thumb: 2D np-array - last thumbnail available
    :return:
    """
    # FIXME: implement update function
    raise NotImplemented('Not yet implemented')

con = psycopg2.connect('dbname=odm360 user=odm360 host=localhost password=zanzibar')
cur = con.cursor()

# DO SOMETHING
# print(is_table(cur, 'photos'))
# print(is_table(cur, 'phoblajhflhgkf'))
# print(query_projects(cur))
# insert_photo(cur, 'mwanza', 'today', '1', '/here/is/something', 'DCIM_12345.JPG', np.random.rand(24, 24),
#              np.random.rand(24, 24))
# print(query_projects(cur))
# print(query_photos(cur, 'dar'))
print(is_table(cur, 'device_status'))
if not(is_table(cur, 'device_status')):
    create_table_status(cur)
print(is_table(cur, 'device_status'))
insert_device(cur, 'some_camera1', 5)
insert_device(cur, 'another_camera1', 6)

cur.execute("SELECT * FROM device_status")
print(cur.fetchall())

drop_table(cur, 'device_status')
print(is_table(cur, 'device_status'))

#


cur.close()
con.close()
