from flask import Blueprint, jsonify, current_app
from jsonschema import validate, ValidationError
from models.photo import Photo
from models.project import Project
from models.survey import Survey
from models import db

# API components that retrieve or download data from database for use on front end
data_api = Blueprint("data_api", __name__)

@data_api.route("/api/get_files/<project_id>", defaults={"survey_id": None}, methods=["GET"])
@data_api.route("/api/get_files/<project_id>/<survey_id>", methods=["GET"])
def get_files(project_id, survey_id):
    """
    API endpoint for getting list of files from project

    :param id: id of project
    :return:
    """
    current_app.logger.info(f"Retrieving files for project_id: {project_id} and survey_id: {survey_id}")
    if survey_id is None:
        files = Photo.query.filter(Photo.project_id == project_id).all()
    else:
        files = Photo.query.filter(Photo.project_id == project_id).filter(Photo.survey_id == survey_id).all()
    return jsonify([f.to_dict() for f in files]), 200

@data_api.route("/api/download_zip/<project_id>", defaults={"survey_id": None}, methods=["GET"])
@data_api.route("/api/download_zip/<project_id>/<survey_id>", methods=["GET"])
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

@data_api.route("/api/delete_files/<project_id>", defaults={"survey_id": None}, methods=["GET"])
@data_api.route("/api/delete_files/<project_id>/<survey_id>", methods=["GET"])
def delete_files(project_id, survey_id):
    """
    API end point for deleting a project with all files under that project
    """
    current_app.logger.info(f"Deleting files for project_id: {project_id} and survey_id: {survey_id}")
    if survey_id is None:
        Photo.query.filter(Photo.project_id == project_id).delete()
        Project.query.filter(Project.id == project_id).delete()
    else:
        Photo.query.filter(Photo.project_id == project_id).filter(Photo.survey_id == survey_id).delete()
        Survey.query.filter(Survey.id == survey_id).delete()
    db.commit()
    return "Files successfully deleted from database", 200


@data_api.errorhandler(ValidationError)
@data_api.errorhandler(ValueError)
def handle(e):
    """
    Custom error handling for child API endpoints.

    :param e:
    :return:
    """
    return jsonify({"error": "Invalid input for child", "message": str(e)}), 400
