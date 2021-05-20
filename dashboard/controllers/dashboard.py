from flask import Blueprint, jsonify, request, flash, url_for, redirect
from jsonschema import validate, ValidationError

# API components that retrieve or download data from database for use on front end
dashboard_api = Blueprint("dashboard_api", __name__)

@dashboard_api.route("/api/get_devices", methods=["GET"])
def get_devices():
    """
    API endpoint for getting list of devices and states of devices

    :return:
    """
    # FIXME: implement retrieval of device states files, should lead to list of devices
    # return jsonify(devices.to_dict())

@dashboard_api.route("/api/get_gps", methods=["GET"])
def get_gps():
    """
    API endpoint for getting current gps location

    :return:
    """
    # FIXME: implement retrieval of gps status
    # return jsonify(gps.to_dict())

@dashboard_api.route("/api/get_status", methods=["GET"])
def get_status():
    """
    API endpoint for getting overall rig status

    :return:
    """
    # FIXME: implement retrieval of rig status
    return "success"
    # return jsonify(rig.to_dict())

