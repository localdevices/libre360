# Server is setup here

from flask import (
    Flask,
    render_template,
    redirect,
    request,
    jsonify,
    flash,
    url_for,
    make_response,
    Response,
)
# import items for navigation bar
from flask_bootstrap import Bootstrap

import os
import psycopg2
import json
import logging
import time
import zipstream
import gpsd
import numpy as np

from odm360.log import start_logger, stream_logger
from odm360.camera360rig import do_request
from odm360 import dbase
from odm360.states import states
from odm360.utils import cleanopts, get_key_state, create_geo_txt
from werkzeug.utils import secure_filename

def _allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _check_offline(conn, max_idle=60):
    """
    Check if devices have not requested anything for a too long time. Device is set to offline if this is the case. Rig
    is switched off in this case.
    :param max_idle: maximum allowed idle time
    :return:
    """
    """Run scheduled job."""
    with conn.cursor() as cur_check:
        devices = dbase.query_devices(cur_check)
        for dev in devices:
            # check the last time the device was online
            time_idle = time.time() - dev[3]  # seconds
            if (time_idle > max_idle) and (dev[2] != 0):
                logger.warning(f"Device {dev[0]} is offline...")
                # check if there is an active project
                rig = dbase.query_project_active(cur_check, as_dict=True)
                if len(rig) > 0:
                    # check if project is capturing
                    if get_key_state(rig["status"]) == "capture":
                        # set back to ready
                        logger.warning(f"Stopping capturing")
                        dbase.update_project_active(cur_check, states["ready"])
                    logger.warning(f"Setting connection to offline")
                    dbase.update_device(
                        cur_check,
                        device_uuid=dev[0],
                        req_time=dev[3],
                        status=states["offline"],
                    )
                    # remove foreign server belonging to offline device
                    dbase.delete_server(cur_check, dev[0])


db = "dbname=odm360 user=odm360 host=localhost password=zanzibar"
conn = psycopg2.connect(db)

# cursor for requests
cur = conn.cursor()

# # dedicated cursor for checking the offline status of child devices
# cur_check = conn.cursor()

# make sure devices is empty
dbase.truncate_table(cur, "devices")
# make sure no server connections are present
dbase.delete_servers(cur)
time.sleep(0.2)
# start logger
logger = start_logger("True", "False")

# if there is an active project, put status on zero (waiting for cams) at the beginning no matter what
cur_project = dbase.query_project_active(cur)
if len(cur_project) == 1:
    dbase.update_project_active(cur, states["ready"])

# start scheduled task to check for offline devices
# checker = RepeatedTimer(5, _check_offline, start_time=time.time(), conn=conn)

UPLOAD_FOLDER = "./static/images"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)
app.logger.disabled = False
bootstrap = Bootstrap(app)
try:
    gpsd.connect()
except:
    # simply set gps unit to None to indicate that there is no GPS device available
    gpsd = None
    logger.warning("GPS unit not found or no connection possible")


@app.route("/", methods=["GET", "POST"])
def status():
    with conn.cursor() as cur_status:
        # check devices that are online and ready for capturing
        devices_ready = dbase.query_devices(cur_status, status=states["ready"])
        devices_total = dbase.query_devices(cur_status)

        if request.method == "POST":
            raw_form = request.form
            form = cleanopts(raw_form)
            if "project" in form:
                logger.info(f"Changing to project {form['project']}")
                # first drop the current active project table and create a new one
                dbase.truncate_table(cur_status, "project_active")
                # insert new active project
                dbase.insert_project_active(cur_status, int(form["project"]))
                cur_project = dbase.query_projects(
                    cur_status,
                    project_id=int(form["project"]),
                    as_dict=True,
                    flatten=True,
                )
                logger.info(
                    f"Successfully changed to project - name: {cur_project['project_name']} cams: {int(cur_project['n_cams'])} interval: {int(cur_project['dt'])} secs.'"
                )
            elif ("service" in form) or ("play-btn" in form):
                # rig has to start capturing OR streaming
                # if form["service"] == "on":
                cur_project = dbase.query_project_active(cur_status)
                project = dbase.query_projects(
                    cur_status, project_id=cur_project[0][0], as_dict=True, flatten=True
                )
                if project["n_cams"] == len(devices_ready):
                    # get details of current project
                    if "service" in form:
                        # start the capturing service
                        logger.info("Starting service")
                        dbase.update_project_active(cur_status, states["capture"])
                    else:
                        # start preview streaming
                        logger.info("Starting camera preview")
                        dbase.update_project_active(cur_status, states["stream"])
                else:
                    logger.info(
                        f"Attempted service start but only {len(devices_ready)} out of {project['n_cams']} devices ready"
                    )
            elif "stop-btn" in form:
                logger.info("Stopping streaming")
                dbase.update_project_active(cur_status, states["ready"])

            elif len(form) == 0:
                logger.info("Stopping service")
                dbase.update_project_active(
                    cur_status, states["ready"]
                )  # status 1 means auto_start cameras once they are all online

        # first check what projects already exist and list those in the status page as selectors
        projects = dbase.query_projects(cur_status)
        project_ids = [p[0] for p in projects]
        project_names = [p[1] for p in projects]
        projects = zip(project_ids, project_names)
        cur_project = dbase.query_project_active(cur_status)

        if len(cur_project) == 0:
            cur_project_id = None
            service_active = 0
            dbase.update_project_active(cur_status, status=states["idle"])
        else:
            cur_project_id = cur_project[0][0]
            service_active = cur_project[0][1]
            project = dbase.query_projects(
                cur_status, project_id=cur_project_id, as_dict=True, flatten=True
            )
            devices_expected = project["n_cams"]
            if (service_active != states["capture"]) and (
                service_active != states["stream"]
            ):
                # apparently there is a project, but not activated to capture or stream yet. So set on 'ready' instead
                dbase.update_project_active(cur_status, status=states["ready"])

        # from example https://stackoverflow.com/questions/24735810/python-flask-get-json-data-to-display
    return render_template(
        "status.html",
        projects=projects,
        cur_project_id=cur_project_id,
        service_active=service_active,
    )


@app.route("/project", methods=["GET", "POST"])
def project_page():
    """
        The settings page where you can manage the various services, the parameters, update, power...
    """
    if request.method == "POST":
        # config = current_app.config['config']
        form = cleanopts(request.form)
        # set the config options as provided
        dbase.insert_project(
            cur, form["project_name"], n_cams=int(form["n_cams"]), dt=int(form["dt"])
        )
        dbase.truncate_table(cur, "project_active")
        # set project to current by retrieving its id and inserting that in current project table
        project_id = dbase.query_projects(cur, project_name=form["project_name"])[0][0]
        dbase.insert_project_active(cur, project_id=project_id)
        logger.info(
            f'Created a new project name: "{form["project_name"]}" cams: {form["n_cams"]} interval: {int(form["dt"])} secs.'
        )
        return redirect("/")
    else:
        return render_template("project.html")


@app.route("/logs")
def logs_page():
    """
        The data web pages where you can download/delete the raw gnss data
    """
    return render_template("logs.html")


@app.route("/nodeodm")
def nodeodm_page():
    """
        The data web pages where you can download/delete the raw gnss data
    """
    return render_template("nodeodm.html")


@app.route("/settings", methods=["GET", "POST"])
def settings_page():
    """
        The data web pages where you can download/delete the raw gnss data
    """
    if request.method == "POST":
        form = cleanopts(request.form)
        if form["submit_button"] == "hotspot":
            logger.info("Switching to local hotspot")
            # switch to serving a hotspot, and tell all children to switch to hotspot
        elif form["submit_button"] == "logo":
            if "filename" not in request.files:
                logger.error("No file provided")
            else:
                file = request.files['filename']
                # if user does not select file, browser also
                # submit an empty part without filename
                if file.filename == '':
                    logger.error("Empty file name provided")
                else:
                    if file and _allowed_file(file.filename):
                        logger.info(f"Uploading {file.filename} to logo.png")
                        filename = "logo.png"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            ssid = form["ssid"]
            passwd = form["password"]
            if ssid != "" and passwd != "":
                # Check if all children for current job are online. If not, don't change, as all children need to be online first
                # TODO: implement check
                devices_ready = dbase.query_devices(cur, status=states["ready"])
                cur_project = dbase.query_project_active(cur)
                project = dbase.query_projects(
                    cur, project_id=cur_project[0][0], as_dict=True, flatten=True
                )
                if project["n_cams"] == len(devices_ready):
                    # Instruct all children to switch networks
                    logger.info(f"Switching to ssid: {ssid} with passwd: {passwd}")
                else:
                    logger.error(
                        f"Not all expected children ({len(devices_ready)}/{project['n_cams']}) ready"
                    )
                # TODO: make instruction upon task request
                # Switch network yourself.
                # TODO: make switcher for wifi network
            else:
                logger.error(f"ssid or password missing")

    return render_template("settings.html")


@app.route("/file_page")  # , methods=["GET", "POST"])
def file_page():
    projects = dbase.query_projects(cur)
    project_ids = [p[0] for p in projects]
    project_names = [p[1] for p in projects]
    projects = zip(project_ids, project_names)
    return render_template("file_page.html", projects=projects)


@app.route("/log_stream", methods=["GET"])
def stream():
    """returns logging information"""
    # largely taken from https://towardsdatascience.com/how-to-add-on-screen-logging-to-your-flask-application-and-deploy-it-on-aws-elastic-beanstalk-aa55907730f
    return Response(
        stream_logger(), mimetype="text/plain", content_type="text/event-stream"
    )


@app.route("/_cameras")
def cameras():
    with conn.cursor() as cur_camera:
        cur_project = dbase.query_project_active(cur_camera)
        project = dbase.query_projects(
            cur_camera, project_id=cur_project[0][0], as_dict=True, flatten=True
        )
        devices = dbase.make_dict_devices(cur_camera)
        n_online = len(devices)
        # when streaming, add stream link
        # add offline devices
        n_offline = int(project["n_cams"]) - n_online
        for n in range(n_offline):
            devices.append(
                {
                    "device_no": f"camera{n + n_online}",
                    "device_uuid": "-",
                    "device_name": "-",
                    "device_ip": "-",
                    "status": "offline",
                    "last_photo": None,
                }
            )

        return jsonify(devices)


@app.route("/_files", methods=["GET", "POST"])
def _files():
    try:
        args = cleanopts(request.args)
        with conn.cursor() as cur_files:
            # first query the relevant project
            project = dbase.query_projects(
                cur_files, project_id=args["project_id"], as_dict=True, flatten=True
            )
            # check what the survey_run id is
            if args["survey_run"] == "all":
                survey_run = None
            else:
                survey_run = args["survey_run"].upper()
            fns = dbase.query_photo_names(
                cur_files, project_id=project["project_id"], survey_run=survey_run
            )
        return jsonify(fns)
    except BaseException as e:
        logger.error(f"{_files} failed with error {e}")


@app.route("/_surveys", methods=["GET", "POST"])
def _surveys():
    args = cleanopts(request.args)
    with conn.cursor() as cur_surveys:
        # first query the relevant project
        project = dbase.query_projects(
            cur_surveys, project_id=args["project_id"], as_dict=True, flatten=True
        )
        surveys = dbase.query_surveys(
            cur_surveys, project_id=project["project_id"], as_dict=True
        )
    return jsonify(surveys)


@app.route("/_cam_summary")
def cam_summary():
    """
    Retrieve current status of cameras and compare against what's needed for the current project
    This is typically run every couple of seconds
    """
    cur_project = dbase.query_project_active(cur)
    project = dbase.query_projects(
        cur, project_id=cur_project[0][0], as_dict=True, flatten=True
    )
    devices_ready = dbase.query_devices(cur, status=states["ready"])

    devices = dbase.query_devices(cur)
    # request gps location
    try:
        msg = gpsd.get_current()
        logger.debug(f"GPS msg: {msg}")
    except:
        logger.debug("No msg received from GPS unit or unit not available")
        msg = None
    cams = {
        "ready": len(devices_ready),
        "total": len(devices),
        "required": project["n_cams"],
        "lat": msg.lat if msg is not None else 0.0,
        "lon": msg.lon if msg is not None else 0.0,
        "alt": msg.alt if msg is not None else 0.0,
        "sats": msg.sats if msg is not None else 0,
        "error": msg.error if msg is not None else "-",
        "mode": msg.mode if msg is not None else "OFF",
    }
    return jsonify(cams)


@app.route("/_proj_locs")
def _proj_locs():
    """
    Retrieve project locations. Typically run when the status page is opened or refreshed.

    """
    with conn.cursor() as cur_locs:
        cur_project = dbase.query_project_active(cur_locs)
        project_id = cur_project[0][0]
        geojson = dbase.query_gps(cur_locs, project_id=project_id)

    return jsonify(geojson)


"_proj_locs"


@app.route("/odm360.zip", methods=["GET"], endpoint="_download")
def _download():
    """
    # download works with a streeaming zip archive: all files listed are queued first, and then streamed to a end-user
    # zip file
    """

    def generator(cur, fns):
        """
        generator for zip archive
        :param cur: cursor for retrieval of individual files
        :return: chunk (i.e. one photo) for zip stream
        """
        z = zipstream.ZipFile(
            mode="w", compression=zipstream.ZIP_DEFLATED, allowZip64=True
        )
        # first make a geo.txt file
        geo = create_geo_txt(fns)
        z.writestr("geo.txt", geo.encode())
        for fn in fns:
            z.write_iter(
                fn["photo_filename"],
                dbase._generator(cur, fn["srvname"], fn["photo_uuid"]),
            )
        for chunk in z:
            yield chunk

    # retrieve arguments (stringified json)
    args = cleanopts(request.args)
    fns = json.loads(args["photos"])
    # build zipfile name
    if len(np.unique([fn["survey_run"] for fn in fns])) > 1:
        # apparently a full project is downloaded
        zip_fn = "{:03d}.zip".format(fns[0]['project_id'])
    else:
        zip_fn = "{:03d}_{:s}.zip".format(fns[0]["project_id"], fns[0]["survey_run"].upper())
    # change filename so that ODM can handle them
    for n in range(len(fns)):
        fns[n]["photo_filename"] = fns[n]["photo_filename"].replace("/", "_")
    # open a dedicated connection for the download
    cur_download = conn.cursor()
    response = Response(generator(cur_download, fns), mimetype="application/zip")
    response.headers["Content-Disposition"] = "attachment; filename={}".format(
        zip_fn
    )
    return response


@app.route("/_delete", methods=["GET"])
def _delete():
    """
    delete selection
    """
    # retrieve arguments (stringified json)
    logger.info("Deleting file selection")
    args = cleanopts(request.args)
    fns = json.loads(args["photos"])
    # find unique projects
    project_ids = set([int(fn["project_id"]) for fn in fns])
    # find unique survey runs
    survey_runs = set([fn["survey_run"].upper() for fn in fns])
    # find unique servers
    srvnames = set([fn["srvname"] for fn in fns])

    # open a dedicated connection for the download
    cur_delete = conn.cursor()
    for survey_run in survey_runs:
        # check if there are still photos, if not delete the survey_run
        fns = dbase.query_photo_names(cur_delete, survey_run=survey_run)
        # deletion sometimes doesn't fully work with remote tables, so we repeat this until no files are found
        while len(fns) > 0:
            for srvname in srvnames:
                dbase.delete_photos(
                    cur_delete, srvname, survey_run
                )  # conversion to upper case needed after json-text conversion
                fns = dbase.query_photo_names(cur_delete, survey_run=survey_run)
        # TODO: delete selection return positive response.
        fns = dbase.query_photo_names(cur_delete, survey_run=survey_run)
        if len(fns) == 0:
            # apparently all photos are successfully deleted, so remove the survey run from the table
            dbase.delete_survey(cur_delete, survey_run=survey_run)
    # finally check over the entire project if there are files left. If not, delete the project!
    for project_id in project_ids:
        fns = dbase.query_photo_names(cur_delete, project_id=project_id)
        if len(fns) == 0:
            dbase.delete_project(cur_delete, project_id=project_id)

    logger.info("Delete is done")
    return make_response(jsonify("Files successfully deleted", 200))


@app.route("/picam", methods=["GET", "POST"])
def picam():
    with conn.cursor() as cur_request:
        if request.method == "POST":

            r, status_code = do_request(cur_request, method="POST")
            return make_response(jsonify(r), status_code)

        elif request.method == "GET":
            r, status_code = do_request(
                cur_request, method="GET"
            )  # response is passed back to client
            # print(r, status_code)
            return make_response(jsonify(r), status_code)


def run(app):
    server = "0.0.0.0"
    port = 5000
    logger.info(f"Running application on http://{server}:{port}")
    app.run(debug=False, port=5000, host="0.0.0.0")


if __name__ == "__main__":
    run(app)
