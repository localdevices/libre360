from flask import Blueprint, jsonify, request, flash, url_for, redirect
from jsonschema import validate, ValidationError

child_api = Blueprint("child_api", __name__)

# FIXME: make a schema format to check task request messages of child against, before processing
task_schema = {
}

# FIXME: make a schema format to check log messages of child against, before processing
log_schema = {
}

@child_api.route("/api/task_request/<id>", methods=["POST"])
def task_request(id):
    """
    API endpoint for task request from child

    :param id: hostname of child
    :return:
    """
    content = request.get_json(silent=True)
    print(f"Content = {content}")
    validate(instance=content, schema=task_schema)
    # FIXME: implement task handling, which eventually should lead to return of task
    # ....
    # return jsonify(task.to_dict())

@child_api.route("/api/child_log/<id>", methods=["POST"])
def child_log(id):
    """
    API endpoint to post a log message of child to the parent device

    :param id: hostname of child
    """
    content = request.get_json(silent=True)
    print(f"Content = {content}")
    validate(instance=content, schema=log_schema)
    # parse content
    # FIXME: implement log message handling, eventually leading to a success/error msg for child
    # ...
    # return jsonify(bathymetry.to_dict())


@child_api.errorhandler(ValidationError)
@child_api.errorhandler(ValueError)
def handle(e):
    """
    Custom error handling for child API endpoints.

    :param e:
    :return:
    """
    return jsonify({"error": "Invalid input for child", "message": str(e)}), 400
