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
from flask_socketio import SocketIO, emit

import base64
import psycopg2
import json
import logging
import time
import zipstream

from odm360.log import start_logger, stream_logger
from odm360.camera360rig import do_request
from odm360 import dbase
from odm360.states import states
from odm360.utils import cleanopts, get_key_state
from odm360.timer import RepeatedTimer


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
                        cur_check, device_uuid=dev[0], req_time=dev[3], status=states["offline"]
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

app = Flask(__name__)
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)
app.logger.disabled = True
bootstrap = Bootstrap(app)
socketio = SocketIO(app)
socketio.frame = None

clients = []
@socketio.on('my event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']})

@socketio.on('my broadcast event', namespace='/test')
def test_message(message):
    print(f"Received message {message}")
    emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('connect', namespace='/test')
def test_connect():
    # users[:] = []
    clients.append(request.sid)
    print(f"A client connected {request.sid}")
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    # remove client from list of clients
    clients.remove(request.sid)
    print(f"Client disconnected, connected clients are {clients}")
    if len(clients) == 1:  ## TODO: add if stop button is pressed
        # apparently no-one's watching anymore so stop!
        emit("_stop", {}, namespace='/test', broadcast=True)

@socketio.on('stream_request', namespace='/test')
def stream_video(message):
    # print("Received .jpg, now emitting")
    # socketio.frame = message["image"]
    # with open('test.jpg', 'wb') as f:
    #     frame = base64.b64decode(message["image"].encode("utf8"))
    #     f.write(frame)

    socketio.emit('stream_response', {'image': message['image']}, namespace='/test', broadcast=True)
    socketio.sleep(0.)

    # return

@socketio.on('request_video', namespace='/test')
def request_video(message):
    print("Received request for video stream, emitting to clients")
    socketio.emit('_video', {}, namespace='/test', broadcast=True)
    socketio.sleep(0)
    # return

@socketio.on('request_video_stop', namespace='/test')
def request_video_stop(message):
    print("Received request to stop video stream, emitting to clients")
    socketio.emit('_stop', {}, namespace='/test', broadcast=True)
    socketio.sleep(0)
    # return


@app.route("/", methods=["GET", "POST"])
def status():
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

    # from example https://stackoverflow.com/questions/24735810/python-flask-get-json-data-to-display
    return render_template("status.html", projects=projects,
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
    with conn.cursor() as cur_files:
        project = dbase.query_projects(
            cur_files, project_id=args["project_id"], as_dict=True, flatten=True
        )
        fns = dbase.query_photo_names(cur_files, project_id=project["project_id"])
    return jsonify(fns)


@app.route("/_cam_summary")
def cam_summary():
    devices_ready = dbase.query_devices(cur, status=states["ready"])
    devices = dbase.query_devices(cur)
    cams = {"ready": len(devices_ready), "total": len(devices)}
    return jsonify(cams)


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
        z = zipstream.ZipFile(mode="w", compression=zipstream.ZIP_DEFLATED, allowZip64=True)
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
    # open a dedicated connection for the download
    cur_download = conn.cursor()
    response = Response(generator(cur_download, fns), mimetype="application/zip")
    response.headers["Content-Disposition"] = "attachment; filename={}".format(
        "odm360.zip"
    )
    return response

@app.route("/_delete", methods=["GET"])
def _delete():
    """
    delete selection
    """
    # retrieve arguments (stringified json)
    logger.info('Deleting file selection')
    args = cleanopts(request.args)
    fns = json.loads(args["photos"])
    # find unique survey runs
    survey_runs = set([fn["survey_run"] for fn in fns])
    # find unique servers
    srvnames = set([fn["srvname"] for fn in fns])

    # open a dedicated connection for the download
    cur_delete = conn.cursor()
    for srvname in srvnames:
        for survey_run in survey_runs:
            dbase.delete_photos(cur_delete, srvname, survey_run.upper())  # conversion to upper case needed after json-text conversion
    # TODO: delete selection return positive response.
    logger.info('Delete is done')

    # response = Response(generator(cur_download), mimetype="application/zip")
    # response.headers["Content-Disposition"] = "attachment; filename={}".format(
    #     "odm360.zip"
    # )
    return make_response(jsonify('Files successfully deleted', 200))

##### SOME FIDDLING WITH A VIRTUAL CAM OBJECT JUST FOR TESTING
class Camera(object):
    def __init__(self):
        import glob
        fns = glob.glob('/home/hcwinsemius/temp/c9f1c734-ac7a-4241-8988-2d1fb30cc0e7/6/2020-11-10t13:00:30/*.jpg')
        self.frames = [open(fn, 'rb').read() for fn in fns]

    def get_frame(self):
        return self.frames[int(time.time()) % len(self.frames)]


# def gen(camera):
def gen():
    while True:
        # TODO replace frame by a stream from a POST request
        # frame = camera.get_frame()
        frame = base64.b64decode(socketio.frame.encode("utf8"))
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/_video", methods=["GET", "POST"])
def _video():
    """
    Receive a video stream with request.stream
    :return:
    """
    if request.method == "GET":
        return Response(gen(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
        # return Response(gen(Camera()),
        #                 mimetype='multipart/x-mixed-replace; boundary=frame')


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
    socketio.run(app, debug=True, port=5000, host="0.0.0.0")
    # app.run(debug=False, port=5000, host="0.0.0.0")


if __name__ == "__main__":
    run(app)
