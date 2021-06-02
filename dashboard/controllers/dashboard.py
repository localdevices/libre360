import json
from flask import Blueprint, jsonify, request, flash, url_for, redirect
from models import Device
# API components that retrieve or download data from database for use on front end
dashboard_api = Blueprint("dashboard_api", __name__)

@dashboard_api.route("/api/get_devices", methods=["GET"])
def get_devices():
    """
    API endpoint for getting list of devices and states of devices

    :return:
    """
    devices = Device.query.all()
    return jsonify([d.to_dict() for d in devices])

@dashboard_api.route("/api/get_gps", methods=["GET"])
def get_gps():
    """
    API endpoint to retrieve all gps points belonging to current project

    :param id: id of project
    """
    import gpsd
    gpsd.connect()
    gpsd.gpsd_stream.write("?POLL;\n")
    gpsd.gpsd_stream.flush()
    raw = gpsd.gpsd_stream.readline()
    return jsonify(json.loads(raw)["tpv"])

