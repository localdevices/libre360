from flask import Blueprint, jsonify, request, flash, url_for, redirect
from jsonschema import validate, ValidationError

# API components that retrieve or download data from database for use on front end
data_api = Blueprint("data_api", __name__)

@data_api.route("/api/get_project/<id>", methods=["GET"])
def get_project(id):
    """
    API endpoint for getting list of files from project

    :param id: id of project
    :return:
    """
    # FIXME: implement retrieval of files, should lead to list of files with details and report of files missing or not
    # ....
    # return jsonify(files.to_dict())

@data_api.route("/api/get_gps_locs/<id>", methods=["GET"])
def get_gps_locs(id):
    """
    API endpoint to retrieve all gps points belonging to current project

    :param id: id of project
    """
    # FIXME: implement gps data retrieval, should lead to dict with gps locs, relevant for project (e.g. for plotting
    #  on a map
    # ...
    # return jsonify(gps.to_dict())

@data_api.route("/api/download_zip/<id>", methods=["GET"])
def download_zip(id):
    """
    API end point for retrieving a zip file from all files in a project

    :param id: id of project
    """
    # FIXME: implement zip download
    # ...
    # response = Response(generator(cur_download, fns), mimetype="application/zip")
    # response.headers["Content-Disposition"] = "attachment; filename={}".format(zip_fn)
    # return response

@data_api.route("/api/download_zip_time/<id>/<time>", methods=["GET"])
def download_zip_timestamp(id, time):
    """
    API end point for retrieving a zip file from files in a project belonging to a survey run of specified time stamp

    :param id: id of project
    :param time: time stamp of project
    """
    # response = Response(generator(cur_download, fns), mimetype="application/zip")
    # response.headers["Content-Disposition"] = "attachment; filename={}".format(zip_fn)
    # return response

@data_api.route("/api/delete_project/<id>", methods=["GET"])
def delete_project(id):
    """
    API end point for deleting a project with all files under that project
    """
    # return success or not


@data_api.errorhandler(ValidationError)
@data_api.errorhandler(ValueError)
def handle(e):
    """
    Custom error handling for child API endpoints.

    :param e:
    :return:
    """
    return jsonify({"error": "Invalid input for child", "message": str(e)}), 400
