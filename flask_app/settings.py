import os
from app import app, conn
from flask import request, render_template
from odm360 import dbase, states
from odm360.states import states
from odm360.utils import cleanopts

ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}

logger = app.logger


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/settings", methods=["GET", "POST"])
def settings_page():
    """
        The data web pages where you can download/delete the raw gnss data
    """
    with conn.cursor() as cur_settings:
        if request.method == "POST":
            form = cleanopts(request.form)
            if form["submit_button"] == "hotspot":
                logger.info("Switching to local hotspot")
                # switch to serving a hotspot, and tell all children to switch to hotspot
            elif form["submit_button"] == "logo":
                if "filename" not in request.files:
                    logger.error("No file provided")
                else:
                    file = request.files["filename"]
                    # if user does not select file, browser also
                    # submit an empty part without filename
                    if file.filename == "":
                        logger.error("Empty file name provided")
                    else:
                        if file and _allowed_file(file.filename):
                            logger.info(f"Uploading {file.filename} to logo.png")
                            filename = "logo.png"
                            file.save(
                                os.path.join(app.config["UPLOAD_FOLDER"], filename)
                            )
            else:
                ssid = form["ssid"]
                passwd = form["password"]
                if ssid != "" and passwd != "":
                    # Check if all children for current job are online. If not, don't change, as all children need to be online first
                    # TODO: implement check
                    devices_ready = dbase.query_devices(
                        cur_settings, status=states["ready"]
                    )
                    cur_project = dbase.query_project_active(cur_settings)
                    project = dbase.query_projects(
                        cur_settings,
                        project_id=cur_project[0][0],
                        as_dict=True,
                        flatten=True,
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
