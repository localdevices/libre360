import psycopg2

# This file contains all database interactions
# to not jeopardize Ivan's health, we use functions rather than classes to approach our database
from odm360 import utils


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
        raise ValueError("provide either a project_name or project_id")
    if not (project_name is None):
        sql_command = f"DELETE FROM projects WHERE project_name='{project_name}'"
    else:
        sql_command = f"DELETE FROM projects WHERE project_id={project_id}"

    cur.execute(sql_command)
    cur.connection.commit()


def drop_photo(cur):
    # FIXME: implement
    raise NotImplementedError("Not yet implemented")


def insert(cur, sql_command):
    """
    Insert a new record using a sql command

    :param cur: cursor
    :param sql_command: command to create record with
    :return:
    """
    # try:
    cur.connection.rollback()
    cur.execute(sql_command)
    cur.connection.commit()
    # except:
    #     raise IOError(f'Insertion command {sql_command} failed')


def insert_device(cur, device_uuid, device_name, status):
    """
    insert a new device in table (leave out last_photo since it is not available yet).
    :param cur: cursor
    :param device_uuid: uuid - id of device (auto-generated on child side)
    :param status: int - status of device, each int has a specific meaning
    :return:
    """
    sql_command = f"INSERT INTO devices(device_uuid, device_name, status) VALUES ('{device_uuid}', '{device_name}', {status});"
    insert(cur, sql_command)


def insert_project_active(cur, project_id):
    sql_command = (
        f"INSERT INTO project_active(project_id, status) VALUES ({project_id}, 0);"
    )
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


def insert_photo(
    cur,
    project_id,
    survey_run,
    device_uuid,
    device_name,
    fn,
    photo_uuid=None,
    photo=None,
    thumb=None,
):
    """
    Insert a photo into the photos table. TODO: fix the blob conversion, now a numpy object is assumed
    :param cur: cursor
    :param project_id: int - project id
    :param survey_run: string - id of survey within project
    :param device_uuid: uuid - id of device
    :param fn: string - filename
    :param photo: bytes - content of photo TODO: check how photos are returned and revise if needed
    :param thumb: bytes - content of thumbnail TODO: check how thumbnails are returned and revise if needed
    :return:
    """
    _photo = psycopg2.Binary(
        photo
    )  # note: photo can be retrieved with _photo.tobytes()
    if photo_uuid is not None:
        # occurs when parent-side storage is done, no binary data is stored
        sql_command = f"""
        INSERT INTO photos
        (
        photo_uuid
        ,project_id
        ,survey_run
        ,device_uuid
        ,device_name
        ,photo_filename
        ,photo
        ) VALUES
        (
        '{photo_uuid}'
        ,'{project_id}'
        ,'{survey_run}'
        ,'{device_uuid}'
        ,'{device_name}'
        ,'{fn}'
        ,{_photo}
        );"""

    elif thumb is None:
        sql_command = f"""
        INSERT INTO photos
        (
        project_id
        ,survey_run
        ,device_uuid
        ,device_name
        ,photo_filename
        ,photo
        ) VALUES
        (
        '{project_id}'
        ,'{survey_run}'
        ,'{device_uuid}'
        ,'{device_name}'
        ,'{fn}'
        ,{_photo}
        );"""
    else:
        _thumb = psycopg2.Binary(thumb)
        sql_command = f"""
        INSERT INTO photos_child
        (
        project_id
        ,survey_run
        ,device_uuid
        ,device_name
        ,photo_filename
        ,photo
        ,thumbnail
        ) VALUES
        (
        '{project_id}'
        ,'{survey_run}'
        ,'{device_uuid}'
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


def is_device(cur, device_uuid):
    """
    Simple check to see if device exists
    :param cur: cursor
    :param device_uuid: uuid - name of device
    :return: True/False
    """
    sql_command = (
        f"SELECT EXISTS ( SELECT 1 FROM devices WHERE device_uuid='{device_uuid}')"
    )
    cur.connection.rollback()
    cur.execute(sql_command)
    return cur.fetchone()[0]


def make_dict_devices(cur):
    devices_raw = query_devices(cur)
    devices = [
        {
            "device_no": f"camera{n}",
            "device_uuid": d[0],
            "device_name": d[1],
            "status": utils.get_key_state(int(d[2])),
            "last_photo": d[3],
        }
        for n, d in enumerate(devices_raw)
    ]
    return devices


def query_devices(cur, status=None, device_uuid=None, as_dict=False, flatten=False):
    table_name = "devices"
    sql_command = f"""SELECT * FROM {table_name}"""
    if status is not None:
        sql_command = sql_command + f""" WHERE status={status}"""
    if device_uuid is not None:
        sql_command = sql_command + f""" WHERE device_uuid='{device_uuid}'"""

    return query_table(
        cur, sql_command, table_name=table_name, as_dict=as_dict, flatten=flatten
    )


def query_photo(cur, fn):
    """

    :param cur: cursor
    :param fn: file name to search for in photos table
    :param kwargs: query_table kwargs (as_dict and flatten)
    :return:
    """
    table_name = "photos"
    if fn is None:
        raise ValueError("Must provide filename as string")
    sql_command = f"SELECT * FROM {table_name} WHERE photo_filename='{fn}'"
    # as we are looking for one unique, photo, as_dict and flatten need to be True
    return query_table(
        cur, sql_command, table_name=table_name, as_dict=True, flatten=True
    )


def query_photos(cur, project_id=None, as_dict=False, flatten=False):
    """
    queries all photos for a given project name
    :param cur: cursor
    :param project_id: int - project id
    :return: list of results
    """
    table_name = "photos"
    if project_id is None:
        raise ValueError("provide a project_id")
    sql_command = f"SELECT * FROM {table_name} WHERE project_id={project_id}"

    return query_table(
        cur, sql_command, table_name=table_name, as_dict=as_dict, flatten=flatten
    )


def query_photos_survey(cur, project_id, survey_run):
    # FIXME: prepare this function
    raise NotImplemented("Function needs to be prepared")


def query_projects(
    cur, project_id=None, project_name=None, as_dict=False, flatten=False
):
    """
    returns all project names available in table "photos" as flattened list
    :param cur: cursor
    :return: list of strings
    """
    table_name = "projects"
    if project_id is not None:
        sql_command = f"SELECT * FROM {table_name} WHERE project_id={project_id}"
    elif project_name is not None:
        sql_command = f"SELECT * FROM {table_name} WHERE project_name='{project_name}'"
    else:
        sql_command = f"SELECT * FROM {table_name}"
    return query_table(
        cur, sql_command, table_name=table_name, as_dict=as_dict, flatten=flatten
    )


def query_project_active(cur, as_dict=False):
    """
    list the currently active project and its status flag. This should always only contain one project!
    :param cur: cursor
    :return: list of one project
    """
    table_name = "project_active"
    sql_command = f"SELECT * FROM {table_name}"
    return query_table(
        cur, sql_command, table_name=table_name, as_dict=as_dict, flatten=True
    )


def query_table(cur, sql_command, table_name=None, as_dict=False, flatten=False):
    cur.execute(sql_command)
    data = cur.fetchall()
    if as_dict:
        if table_name is None:
            raise ValueError(
                "table_name is of type None, has to be type str to use as_dict=True"
            )
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


def update_device(cur, device_uuid, status, last_photo=None):
    """
    Update the status of a given (existing) device in devices table
    :param cur: cursor
    :param device_uuid: uuid - id of device
    :param status: int - status indicator
    :param last_photo: str - uuid of last photo (error returned if uuid does not exist in database)
    :return:
    """
    if not (is_device(cur, device_uuid)):
        raise KeyError(
            f'device "{device_uuid}" does not exist in table "device_status"'
        )
    if last_photo is not None:
        sql_command = f"UPDATE devices SET status={status}, last_photo='{last_photo}' WHERE device_uuid='{device_uuid}'"
    else:
        sql_command = (
            f"UPDATE devices SET status={status} WHERE device_uuid='{device_uuid}'"
        )
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
        start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
        sql_command = (
            f"UPDATE project_active SET status={status}, start_time='{start_time_str}'"
        )
    cur.execute(sql_command)
    cur.connection.commit()
