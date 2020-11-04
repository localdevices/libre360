# Server is setup here

from flask import (
    Flask,
    render_template,
    redirect,
    request,
    jsonify,
    make_response,
    Response,
)
from flask_bootstrap import Bootstrap

import psycopg2
import logging
import time
import zipstream

from odm360.log import start_logger, stream_logger
from odm360.camera360rig import do_request
from odm360 import dbase
from odm360.states import states
from odm360.utils import cleanopts, get_key_state
from odm360.timer import RepeatedTimer


db = "dbname=odm360 user=odm360 host=localhost password=zanzibar"
conn = psycopg2.connect(db)
cur = conn.cursor()


def _check_offline(cur=cur, max_idle=60):
    """
    Check if devices have not requested anything for a too long time. Device is set to offline if this is the case. Rig
    is switched off in this case.
    :param max_idle: maximum allowed idle time
    :return:
    """
    """Run scheduled job."""
    devices = dbase.query_devices(cur)
    for dev in devices:
        # check the last time the device was online
        time_idle = time.time() - dev[3]  # seconds
        if (time_idle > max_idle) and (dev[2] != 0):
            logger.warning(f"Device {dev[0]} is offline...")
            # check if there is an active project
            rig = dbase.query_project_active(cur, as_dict=True)
            if len(rig) > 0:
                # check if project is capturing
                if get_key_state(rig["status"]) == "capture":
                    # set back to ready
                    logger.warning(f"Stopping capturing")
                    dbase.update_project_active(cur, states["ready"])
                logger.warning(f"Setting connection to offline")
                dbase.update_device(
                    cur, device_uuid=dev[0], req_time=dev[3], status=states["offline"]
                )
                # remove foreign server belonging to offline device
                dbase.delete_server(cur, dev[0])


def _generator(cur, table, fn, chunksize=1024):
    # print(table, fn)
    sql_command = f"SELECT photo from {table} where photo_filename='{fn}'"
    print(sql_command)
    cur.connection.rollback()
    cur.execute(sql_command)
    photo = cur.fetchall()[0][0]
    for n in range(0, len(photo), chunksize):
        chunk = photo[n : n + chunksize]
        yield chunk


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
checker = RepeatedTimer(5, _check_offline, start_time=time.time())

app = Flask(__name__)
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)
app.logger.disabled = True
bootstrap = Bootstrap(app)


@app.route("/", methods=["GET", "POST"])
def gps_page():
    # check devices that are online and ready for capturing
    devices_ready = dbase.query_devices(cur, status=states["ready"])
    devices_total = dbase.query_devices(cur)

    if request.method == "POST":
        raw_form = request.form
        form = cleanopts(raw_form)
        if "project" in form:
            logger.info(f"Changing to project {form['project']}")
            # first drop the current active project table and create a new one
            dbase.truncate_table(cur, "project_active")
            # insert new active project
            dbase.insert_project_active(cur, int(form["project"]))
            cur_project = dbase.query_projects(
                cur, project_id=int(form["project"]), as_dict=True, flatten=True
            )
            logger.info(
                f"Successfully changed to project - name: {cur_project['project_name']} cams: {int(cur_project['n_cams'])} interval: {int(cur_project['dt'])} secs.'"
            )
        elif "service" in form:
            if form["service"] == "on":
                cur_project = dbase.query_project_active(cur)
                project = dbase.query_projects(
                    cur, project_id=cur_project[0][0], as_dict=True, flatten=True
                )
                if project["n_cams"] == len(devices_ready):
                    # get details of current project
                    logger.info("Starting service")
                    dbase.update_project_active(cur, states["capture"])
                else:
                    logger.info(
                        f"Attempted service start but only {len(devices_ready)} out of {project['n_cams']} devices ready"
                    )
        elif len(form) == 0:
            logger.info("Stopping service")
            dbase.update_project_active(
                cur, states["ready"]
            )  # status 1 means auto_start cameras once they are all online

    # first check what projects already exist and list those in the status page as selectors
    projects = dbase.query_projects(cur)
    project_ids = [p[0] for p in projects]
    project_names = [p[1] for p in projects]
    projects = zip(project_ids, project_names)
    cur_project = dbase.query_project_active(cur)

    if len(cur_project) == 0:
        cur_project_id = None
        service_active = 0
        dbase.update_project_active(cur, status=states["idle"])
    else:
        cur_project_id = cur_project[0][0]
        service_active = cur_project[0][1]
        project = dbase.query_projects(
            cur, project_id=cur_project_id, as_dict=True, flatten=True
        )
        devices_expected = project["n_cams"]
        if service_active != states["capture"]:
            # apparently there is a project, but not activated to capture yet. So set on 'ready' instead
            dbase.update_project_active(cur, status=states["ready"])

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
        # FIXME: put inputs into the database and remove config stuff below
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


@app.route("/cams")
def cam_page():
    # from example https://stackoverflow.com/questions/24735810/python-flask-get-json-data-to-display
    return render_template("cam_status.html")


@app.route("/file_page")  # , methods=["GET", "POST"])
def file_page():
    # if request.method == "POST":
    #     form = cleanopts(request.form)
    #     project = dbase.query_projects(cur, project_name=form["project"])
    #
    #     if form["submit_button"] == 'hotspot':
    #         logger.info('Switching to local hotspot')
    #         # switch to serving a hotspot, and tell all children to switch to hotspot

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
    cur_project = dbase.query_project_active(cur)
    project = dbase.query_projects(
        cur, project_id=cur_project[0][0], as_dict=True, flatten=True
    )
    devices = dbase.make_dict_devices(cur)
    n_online = len(devices)
    # add offline devices
    n_offline = int(project["n_cams"]) - n_online
    for n in range(n_offline):
        devices.append(
            {
                "device_no": f"camera{n + n_online}",
                "device_uuid": "uknown",
                "device_name": "unknown",
                "status": "offline",
                "last_photo": None,
            }
        )

    return jsonify(devices)


@app.route("/_files", methods=["GET", "POST"])
def files():
    args = cleanopts(request.args)
    project = dbase.query_projects(
        cur, project_id=args["project_id"], as_dict=True, flatten=True
    )
    fns = dbase.query_photo_names(cur, project_id=project["project_id"])
    return jsonify(fns)


@app.route("/_cam_summary")
def cam_summary():
    devices_ready = dbase.query_devices(cur, status=states["ready"])
    devices = dbase.query_devices(cur)
    cams = {"ready": len(devices_ready), "total": len(devices)}
    return jsonify(cams)


@app.route("/odm360.zip", methods=["GET"], endpoint="download")
def download():
    # for now hard coded so that we can test
    # open a dedicated connection for the download
    db = "dbname=odm360 user=odm360 host=localhost password=zanzibar"
    conn2 = psycopg2.connect(db)
    cur2 = conn2.cursor()

    project = 1
    photos = dbase.query_photo_names(cur2, project_id=project)

    # FIXME: retrieve queried photos from combined postgresql view and prepare stream zip
    def generator(cur):
        z = zipstream.ZipFile(mode="w", compression=zipstream.ZIP_DEFLATED)
        for photo in photos[-3:]:
            z.write_iter(
                photo["photo_filename"],
                _generator(cur, photo["srvname"], photo["photo_filename"]),
            )
        # z.write_iter("/home/hcwinsemius/temp/odm360/2.jpg", _generator("http://i.imgur.com/uAWnH3S.jpg"))
        # # add all the necessary files here
        # z.write_iter("/home/hcwinsemius/temp/odm360/3.png", _generator("http://i.imgur.com/Phhjhbn.png"))
        # here is where the magic happens. Each call will iterate the generator we wrote for each file
        # one at a time until all files are completed.
        for chunk in z:
            yield chunk

    response = Response(generator(cur2), mimetype="application/zip")
    response.headers["Content-Disposition"] = "attachment; filename={}".format(
        "odm360.zip"
    )
    return response


@app.route("/picam", methods=["GET", "POST"])
def picam():
    if request.method == "POST":

        r, status_code = do_request(cur, method="POST")
        return make_response(jsonify(r), status_code)

    elif request.method == "GET":
        r, status_code = do_request(
            cur, method="GET"
        )  # response is passed back to client
        # print(r, status_code)
        return make_response(jsonify(r), status_code)


def run(app):
    server = "0.0.0.0"
    port = 5000
    logger.info(f"Running application on http://{server}:{port}")
    app.run(debug=False, port=5000, host="0.0.0.0")


# def _generator(photo_url):
#     # download a file and stream it
#     r = requests.get(photo_url, stream=True)
#     if r.status_code != 200:
#         return
#     for chunk in r.iter_content(10240):
#         print(type(chunk))
#         yield chunk

if __name__ == "__main__":
    run(app)
