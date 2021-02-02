from app import app, conn
from flask import request, render_template, jsonify
from odm360 import dbase, states
from odm360.states import states
from odm360.utils import cleanopts, get_key_state
import time
import gpsd

logger = app.logger


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


@app.route("/_cam_summary")
def cam_summary():
    """
    Retrieve current status of cameras and compare against what's needed for the current project
    This is typically run every couple of seconds
    """
    with conn.cursor() as cur_summary:
        cur_project = dbase.query_project_active(cur_summary)
        project = dbase.query_projects(
            cur_summary, project_id=cur_project[0][0], as_dict=True, flatten=True
        )
        devices_ready = dbase.query_devices(cur_summary, status=states["ready"])

        devices = dbase.query_devices(cur_summary)
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
