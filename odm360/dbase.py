# This file contains all database interactions
# to not jeopardize Ivan's health, we use functions rather than classes to approach our database
from odm360 import utils
import json
from datetime import datetime

def _generator(cur, table, uuid, chunksize=1024):
    """
    Generator for streaming photos to zip files
    :param cur: cursor
    :param table: name of (foreign) table to retrieve photos from
    :param uuid: photo_uuid of current photo
    :param chunksize: nr of bytes to return per yield
    :return: chunk of photo
    """
    sql_command = f"SELECT photo from {table} where photo_uuid='{uuid}'"
    cur.execute(sql_command)
    photo = cur.fetchall()
    photo = photo[0][0]
    for n in range(0, len(photo), chunksize):
        chunk = photo[n : n + chunksize]
        yield chunk


def create_foreign_table(cur, host):
    cur.execute("SELECT foreign_server_name FROM information_schema.foreign_servers;")
    nr_of_servers = len(cur.fetchall())

    sql_command = f"""
CREATE SERVER IF NOT EXISTS child_{nr_of_servers}
    FOREIGN DATA WRAPPER postgres_fdw 
    OPTIONS (host '{host}', port '5432', dbname 'odm360');
    """
    cur.execute(sql_command)
    cur.connection.commit()

    sql_command = f"""
CREATE FOREIGN TABLE IF NOT EXISTS child_{nr_of_servers} (
photo_uuid uuid
,project_id BIGINT
,survey_run text NOT NULL
,device_uuid uuid NOT NULL
,device_name text 
,photo_filename text NOT NULL
,ts TIMESTAMP
,photo BYTEA NOT NULL)
SERVER child_{nr_of_servers} OPTIONS (schema_name 'public', table_name 'photos_child');
"""
    cur.execute(sql_command)
    cur.connection.commit()

    sql_command = f"""
CREATE USER MAPPING IF NOT EXISTS FOR odm360 
    SERVER child_{nr_of_servers}
    OPTIONS (user 'odm360', password 'zanzibar');
"""
    cur.execute(sql_command)
    cur.connection.commit()


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
        sql_command = f"DELETE FROM projects WHERE project_name='{project_name}';"
    else:
        sql_command = f"DELETE FROM projects WHERE project_id={project_id};"

    cur.execute(sql_command)
    cur.connection.commit()


def delete_server(cur, device_uuid):
    srvoptions = f"host={device_uuid},port=5432,dbname=odm360"
    sql_command = (
        "select srvname from pg_foreign_server WHERE srvoptions='{" + srvoptions + "}'"
    )
    cur.execute(sql_command)
    server_name = cur.fetchone()
    # delete server from database
    cur.execute(f"DROP SERVER IF EXISTS {server_name[0]} CASCADE")
    cur.connection.commit()


def delete_servers(cur):
    """
    Deletes all foreign servers from the connected database, including any connected views

    :param cur: cursor
    :return:
    """

    # find names of all existing servers
    cur.execute("SELECT foreign_server_name FROM information_schema.foreign_servers;")
    server_names = cur.fetchall()

    for server_name in server_names:
        cur.execute(f"DROP SERVER IF EXISTS {server_name[0]} CASCADE")
        cur.connection.commit()


def delete_survey(cur, survey_run=None):
    """
    Deletes a indicated survey_run

    :param cur: cursor
    :param survey_run: str - default None - if set then survey_run is deleted
    :return:
    """
    if survey_run is None:
        raise ValueError("provide a survey_run to delete")
    sql_command = f"DELETE FROM surveys WHERE survey_run='{survey_run}';"
    cur.execute(sql_command)
    cur.connection.commit()


def delete_photos(cur, table, survey_run):
    sql_command = f"DELETE FROM {table} WHERE survey_run='{survey_run}';"
    cur.execute(sql_command)
    cur.connection.commit()


def insert(cur, sql_command):
    """
    Insert a new record using a sql command

    :param cur: cursor
    :param sql_command: command to create record with
    :return:
    """
    # try:
    # cur.connection.rollback()
    cur.execute(sql_command)
    cur.connection.commit()
    # except:
    #     raise IOError(f'Insertion command {sql_command} failed')


def insert_device(cur, device_uuid, device_name, status, req_time):
    """
    insert a new device in table (leave out last_photo since it is not available yet).
    :param cur: cursor
    :param device_uuid: uuid - id of device (auto-generated on child side)
    :param status: int - status of device, each int has a specific meaning
    :return:
    """
    sql_command = f"INSERT INTO devices(device_uuid, device_name, status, req_time) VALUES ('{device_uuid}', '{device_name}', {status}, {req_time});"
    insert(cur, sql_command)


def insert_gps(cur, project_id, survey_run, timestamp, msg):
    sql_command = f"INSERT INTO gps(project_id, survey_run, ts, msg) VALUES ({project_id}, '{survey_run}', '{timestamp}', '{msg}');"
    insert(cur, sql_command)


def insert_survey(cur, project_id, survey_run):
    """
    insert a new device in table (leave out last_photo since it is not available yet).
    :param cur: cursor
    :param device_uuid: uuid - id of device (auto-generated on child side)
    :param status: int - status of device, each int has a specific meaning
    :return:
    """
    sql_command = f"INSERT INTO surveys(project_id, survey_run) VALUES ('{project_id}', '{survey_run}');"
    insert(cur, sql_command)


def insert_photo(
    cur,
    photo_uuid,
    project_id,
    survey_run,
    device_uuid,
    device_name,
    photo_filename,
    timestamp,
    fn,
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
    # occurs when parent-side storage is done, no binary data is stored
    ts = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
    sql_command = f"""
    INSERT INTO photos_child
    (
    photo_uuid
    ,project_id
    ,survey_run
    ,device_uuid
    ,device_name
    ,photo_filename
    ,ts
    ,photo
    ) SELECT
    '{photo_uuid}'
    , {project_id}
    , '{survey_run}'
    , '{device_uuid}'
    , '{device_name}'
    , '{photo_filename}'
    , '{ts}'
    , pg_read_binary_file('{fn}')
    ;"""
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
            "device_stream": f'<a href="http://{d[0]}.local:8554/stream">http://{d[0]}.local:8554/stream</a>'
            if utils.get_key_state(int(d[2])) == "stream"
            else "",
            "last_photo": d[
                3
            ],  # TODO: currently last_photo is the last moment device was online. Change to last_photo once database structure is entirely clear.
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
    sql_command = sql_command + """;"""
    return query_table(
        cur, sql_command, table_name=table_name, as_dict=as_dict, flatten=flatten
    )


def query_photo(cur, uuid):
    """

    :param cur: cursor
    :param fn: file name to search for in photos table
    :param kwargs: query_table kwargs (as_dict and flatten)
    :return:
    """
    table_name = "photos"
    if fn is None:
        raise ValueError("Must provide filename as string")
    sql_command = f"SELECT * FROM {table_name} WHERE photo_uuid='{uuid}'"
    # as we are looking for one unique, photo, as_dict and flatten need to be True
    return query_table(
        cur, sql_command, table_name=table_name, as_dict=True, flatten=True
    )


def query_photo_names(cur, project_id=None, survey_run=None):
    """
    queries all photos for a given project name
    :param cur: cursor
    :param project_id: int - project id
    :param survey_run: str - name of survey_run
    :return: list of results
    """
    # query all available foreign table names
    cur.execute("select foreign_table_name from information_schema.foreign_tables")
    tables = cur.fetchall()
    cols = ["photo_filename", "photo_uuid", "survey_run", "project_id", "ts"]
    # start with an empty list of files
    fns = []
    for n, table in enumerate(tables):
        # get further information about the server (table names and server names are the same)
        cur.execute(
            f"SELECT srvoptions from pg_foreign_server where srvname='{table[0]}';"
        )
        # strip the host name from the info
        host = cur.fetchone()[0][0].split("=")[-1]
        if survey_run is None:
            sql_command = f"SELECT photo_filename, photo_uuid, survey_run, project_id, ts from {table[0]} WHERE project_id={project_id};"
        else:
            sql_command = f"SELECT photo_filename, photo_uuid, survey_run, project_id, ts from {table[0]} WHERE survey_run='{survey_run}';"

        data = query_table(cur, sql_command, table_name=table[0])
        fns_server = [dict(zip(cols, d)) for d in data]
        # add the device id
        for n in range(len(fns_server)):
            fns_server[n]["ts"] = fns_server[n]["ts"].strftime("%Y-%m-%d %H:%M:%S.%f")
            fns_server[n]["device_uuid"] = host
            fns_server[n]["srvname"] = table[0]
        fns += fns_server
    # finally add locations to the files
    # for fn in fns:

    return fns

def query_gps_timestamp(cur, timestamp, before=True):
    """
    Query gps table for location closest to provided time stamp, either before or after that time stamp
    :param cur: cursor
    :param timestamp: stamp in "%Y-%m-%d %H:%M:%S.%f format in UTC (very important to make sure UTC is always used!)
    :param before: If set to True, then the location with closest time stamp before the provided time stamp is provided, otherwise the one after
    :return: msg in dictionary (from json) format
    """
    if before:
        sql = f"SELECT (msg -> 'tpv'->> -1) FROM gps WHERE ts < '{timestamp}' ORDER BY ts DESC FETCH FIRST ROW ONLY;"
        sql_ts = f"SELECT (ts) FROM gps WHERE ts < '{timestamp}' ORDER BY ts DESC FETCH FIRST ROW ONLY;"
    else:
        sql = f"SELECT (msg -> 'tpv'->> -1) FROM gps WHERE ts >= '{timestamp}' FETCH FIRST ROW ONLY;"
        sql_ts = f"SELECT (ts) FROM gps WHERE ts >= '{timestamp}' FETCH FIRST ROW ONLY;"
    # retrieve time stamp

    cur.execute(sql)
    data = cur.fetchall()
    if len(data) > 0:
        loc = json.loads(data[0][0])
        # also query ts
        cur.execute(sql_ts)
        ts = cur.fetchone()[0]
        print(ts, loc)
        return ts, loc
    else:
        return None

def query_gps(cur, project_id, as_geojson=True):
    """
    Query only lat and lon locations from database

    """
    sql = f"SELECT (msg -> 'tpv'->-1->>'lat') FROM gps WHERE project_id={project_id};"
    cur.execute(sql)
    data_lat = cur.fetchall()
    sql = f"SELECT (msg -> 'tpv'->-1->>'lon') FROM gps WHERE project_id={project_id};"
    cur.execute(sql)
    data_lon = cur.fetchall()
    lon_lat = [[x[0], y[0]] for x, y in zip(data_lon, data_lat)]
    if as_geojson:
        geojson = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": lon_lat,
                },
                "properties": {
                    "OBJECTID": project_id,
                }
            }]
        }
        return geojson
    else:
        return lon_lat


def query_location(cur, timestamp, dt_max=2.):
    ts_before, msg_before = query_gps_timestamp(cur, timestamp)
    ts_after, msg_after = query_gps_timestamp(cur, timestamp, before=False)
    keys = ["lon", "lat", "alt", "epx", "epy", "epv"]
    loc = {k: None for k in keys}
    if (msg_before is None) or (msg_after is None):
        # no suitable location found or one location missing return Nones only
        return loc

    if (msg_before["mode"] < 2) or (msg_after["mode"] < 2):
        # mode of one of the locations is less than 2D fix, so no reliable position
        return loc

    ts_photo = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
    dt_before = abs((ts_before - ts_photo).total_seconds())
    dt_after = abs((ts_after - ts_photo).total_seconds())
    if (dt_before > dt_max) or (dt_after > dt_max):
        # positions have been taken too far apart from each other to be reliable, so return empty
        return loc
    weight_before = 1./dt_before
    weight_after = 1./dt_after
    print(weight_before, weight_after)
    # normalize weights
    weight_sum = weight_before + weight_after
    weight_before = weight_before/weight_sum
    weight_after = weight_after/weight_sum
    print(f"sum of weights: {weight_before + weight_after}")
    # compute position
    for k in keys:
        loc[k] = msg_before[k] * weight_before + msg_after[k] * weight_after
    return loc


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


def query_surveys(cur, project_id, as_dict=False, flatten=False):
    table_name = "surveys"
    sql_command = f"SELECT * FROM {table_name} WHERE project_id={project_id}"
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
            return dict(zip(cols, data[0]))
        # return {k: v[0] for k, v in zip(cols, zip(*data))}
        else:
            return [dict(zip(cols, d)) for d in data]
            # return {k: list(v) for k, v in zip(cols, zip(*data))}

    else:
        return data


def truncate_table(cur, table):
    sql_command = f"""TRUNCATE {table}"""
    cur.execute(sql_command)
    cur.connection.commit()


def update_device(cur, device_uuid, status, req_time, last_photo=None):
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
    if (last_photo is not None) and (last_photo != ""):
        sql_command = f"UPDATE devices SET status={status}, last_photo='{last_photo}', req_time={req_time} WHERE device_uuid='{device_uuid}'"
    else:
        sql_command = f"UPDATE devices SET status={status}, req_time={req_time} WHERE device_uuid='{device_uuid}'"
    cur.execute(sql_command)
    cur.connection.commit()


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
