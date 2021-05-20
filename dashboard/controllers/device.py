from flask import Blueprint, jsonify, request, flash, url_for, redirect
from jsonschema import validate, ValidationError
from models import db
from models.device import Device, DeviceStatus

device_api = Blueprint("device_api", __name__)

# FIXME: make a schema format to check task request messages of child against, before processing
task_schema = {
    "type": "object",
    "required": ["request_time", "status"],
    "properties": {
        "request_time": {"type": "string"},
        "status": {"type": "string"},
    }
}

# FIXME: make a schema format to check log messages of child against, before processing
log_schema = {
}

@device_api.route("/api/task_request/<hostname>", methods=["POST"])
def task_request(hostname):
    """
    API endpoint for task request from child

    :param id: hostname of child
    :return:
    """
    content = request.get_json(silent=True)
    print(f"Content = {content}")
    validate(instance=content, schema=task_schema)
    content["hostname"] = hostname  # add the host to the content
    # content["status"] = DeviceStatus[content["status"]]
    # FIXME: implement task handling, which eventually should lead to return of task
    device = Device.query.filter(Device.hostname == hostname).first()
    if device is None:
        # device hasn't been online yet, add to database
        print(content)
        db.add(Device(**content))
    else:
        # update status
        device.status = content["status"]
    db.commit()
    # ....
    return "Success", 200
    # return jsonify(task.to_dict())

@device_api.route("/api/child_log/<id>", methods=["POST"])
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


@device_api.errorhandler(ValidationError)
@device_api.errorhandler(ValueError)
def handle(e):
    """
    Custom error handling for child API endpoints.

    :param e:
    :return:
    """
    return jsonify({"error": "Invalid input for child", "message": str(e)}), 400
