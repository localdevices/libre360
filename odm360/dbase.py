import psycopg2
import logging
import datetime as dt
# This file contains all database interactions
# to not jeopardize Ivan's health, we use functions rather than classes to approach our database
from odm360 import utils
from odm360.states import states

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
    ,device_id BIGINT
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


def create_table_project_active(cur, drop=False):
    """
    Create a table for just the project that is currently active, only holding the project_id and a status
    :param cur: cursor
    :param drop: bool - default False, if set to True, any existing table will be dropped first, before (re)creation
    :return:
    """
    if drop:
        sql_command = """
        -- Lists the current active project ID and that's it... .
        DROP TABLE IF EXISTS project_active CASCADE;
        CREATE TABLE IF NOT EXISTS project_active
        (
            project_id BIGINT
            ,status integer -- 0: waiting for cams to get ready, 1: ready, 2: capturing, 3: transferring
            ,start_time timestamp -- 
            ,CONSTRAINT fk_projects
                FOREIGN KEY(project_id) 
                  REFERENCES projects(project_id)
              ON DELETE CASCADE	
        );
        """
    else:
        sql_command = """
        -- Lists the current active project ID and that's it... .
        CREATE TABLE IF NOT EXISTS project_active
        (
            project_id BIGINT
            ,status integer  -- 0: waiting for cams to get ready, 1: ready, 2: capturing, 3: transferring
            ,CONSTRAINT fk_projects
                FOREIGN KEY(project_id) 
                  REFERENCES projects(project_id)
              ON DELETE CASCADE	
        );
        """

    create_table(cur, sql_command)

def delete_project(cur, project_name=None, project_id=None):
    """
    Deletes a indicated project and all relations from database (inc. photos, so be careful with this one!)
    Either a project name, or id has to be provided, both default to None.

    :param cur: cursor
    :param project_name: str - default None - if set then project_name is used to find project to delete
    :param project_id: int - default None - if set, then project_id is used to find project to delete
    :return:
    """
    if (project_name is None) and (project_id is None):
        raise ValueError('provide either a project_name or project_id')
    if not (project_name is None):
        sql_command = f"DELETE FROM projects WHERE project_name='{project_name}'"
    else:
        sql_command = f"DELETE FROM projects WHERE project_id={project_id}"

    cur.execute(sql_command)
    cur.connection.commit()


def drop_table(cur, table_name, cascade=False):
    """
    Drop a table from the database, if cascade is set to True, then all tables dependent also remove.
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

def insert_project_active(cur, project_id):
    sql_command = f"INSERT INTO project_active(project_id, status) VALUES ({project_id}, 0);"
    insert(cur, sql_command)

def insert_project(cur, project_name, n_cams, dt):
    """
    Insert a new project and associated settings into the database
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


def insert_photo(cur, project_id, survey_run, device_name, fn, photo, thumb=None):
    """
    Insert a photo into the photos table. TODO: fix the blob conversion, now a numpy object is assumed
    :param cur: cursor
    :param project_id: int - project id
    :param survey_run: string - id of survey within project
    :param device_name: string - id of device
    :param fn: string - filename
    :param photo: bytes - content of photo TODO: check how photos are returned and revise if needed
    :param thumb: bytes - content of thumbnail TODO: check how thumbnails are returned and revise if needed
    :return:
    """
    if thumb is None:
        sql_command = f"""
        INSERT INTO photos_child
        (
        project_id
        ,survey_run
        ,device_name
        ,photo_filename
        ,photo
        ) VALUES
        (
        '{project_id}'
        ,'{survey_run}'
        ,'{device_name}'
        ,'{fn}'
        ,{photo}
        );"""
    else:
        sql_command = f"""
        INSERT INTO photos_child
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
        ,{photo}
        ,{thumb}
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


def query_devices(cur, status=None, device_name=None, as_dict=False, flatten=False):
    table_name = 'devices'
    sql_command = f"""SELECT * FROM {table_name}"""
    if status is not None:
        sql_command = sql_command + f""" WHERE status={status}"""
    if device_name is not None:
        sql_command = sql_command + f""" WHERE device_name='{device_name}'"""

    return query_table(cur, sql_command, table_name=table_name, as_dict=as_dict, flatten=flatten)


def query_photos(cur, project_id=None, as_dict=False, flatten=False):
    """
    queries all photos for a given project name
    :param cur: cursor
    :param project_id: int - project id
    :return: list of results
    """
    table_name = 'photos'
    if project_id is None:
        raise ValueError('provide a project_id')
    sql_command = f"SELECT * FROM {table_name} WHERE project_id={project_id}"

    return query_table(cur, sql_command, table_name=table_name, as_dict=as_dict, flatten=flatten)


def query_photos_survey(cur, project_id, survey_run):
    # FIXME: prepare this function
    raise NotImplemented("Function needs to be prepared")


def query_projects(cur, project_id=None, project_name=None, as_dict=False, flatten=False):
    """
    returns all project names available in table "photos" as flattened list
    :param cur: cursor
    :return: list of strings
    """
    table_name = 'projects'
    if project_id is not None:
        sql_command = f"SELECT * FROM {table_name} WHERE project_id={project_id}"
    elif project_name is not None:
        sql_command = f"SELECT * FROM {table_name} WHERE project_name='{project_name}'"
    else:
        sql_command = f"SELECT * FROM {table_name}"
    return query_table(cur, sql_command, table_name=table_name, as_dict=as_dict, flatten=flatten)


def query_project_active(cur, as_dict=False):
    """
    list the currently active project and its status flag. This should always only contain one project!
    :param cur: cursor
    :return: list of one project
    """
    table_name = 'project_active'
    sql_command = f"SELECT * FROM {table_name}"
    return query_table(cur, sql_command, table_name=table_name, as_dict=as_dict, flatten=True)

def query_table(cur, sql_command, table_name=None, as_dict=False, flatten=False):
    cur.execute(sql_command)
    data = cur.fetchall()
    if as_dict:
        if table_name is None:
            raise ValueError('table_name is of type None, has to be type str to use as_dict=True')
        # add the column labels and make a dict out of the data
        sql_command = f"""SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}'"""
        cur.execute(sql_command)
        cols = [c[0] for c in cur.fetchall()]
        if flatten and (len(data) == 1):
            return {k: v[0] for k, v in zip(cols, zip(*data))}
        else:
            return {k: list(v) for k, v in zip(cols, zip(*data))}

    else:
        return data


def truncate_table(cur, table):
    sql_command = f"""TRUNCATE {table}"""
    cur.execute(sql_command)
    cur.connection.commit()


def update_device(cur, device_name, status, last_photo=None):
    """
    Update the status of a given (existing) device in devices table
    :param cur: cursor
    :param device_name: str - id of device
    :param status: int - status indicator
    :param last_photo: str - uuid of last photo (error returned if uuid does not exist in database)
    :return:
    """
    if not (is_device(cur, device_name)):
        raise KeyError(f'device "{device_name}" does not exist in table "device_status"')
    if last_photo is not None:
        sql_command = f"UPDATE devices SET status={status}, last_photo='{last_photo}' WHERE device_name='{device_name}'"
    else:
        sql_command = f"UPDATE devices SET status={status} WHERE device_name='{device_name}'"
    cur.execute(sql_command)


def update_project_active(cur, status, start_time=None):
    """
    Update status of the currently running project. 0/1: service (not) running
    :param cur: cursor
    :param status: int - update the status of the rig to given state (0: not running, 1: running)
    :return:
    """
    if start_time is None:
        sql_command = f"UPDATE project_active SET status={status}"
    else:
        start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')
        sql_command = f"UPDATE project_active SET status={status}, start_time='{start_time_str}'"
    cur.execute(sql_command)
    cur.connection.commit()